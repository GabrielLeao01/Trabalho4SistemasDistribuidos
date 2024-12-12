from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import pika
import threading
import requests
from consumir import Consumir 
from publicar import Publicar
app = Flask(__name__)
CORS(app)
produtos = []
try:
    response = requests.get('http://localhost:3002/estoque')
    produtos = response.json()
    print("Resposta do Microserviço B:", response.json())
except requests.exceptions.RequestException as e:
    print("Erro na requisição:", e)
    exit(1)
carrinho = []
orders = []
notificacoes = []
pedidos = []
pedidos_criados = 'Pedidos_Criados'
pedidos_excluidos = 'Pedidos_Excluidos'
pagamentos_aprovados = 'Pagamentos_Aprovados'
pagamentos_recusados = 'Pagamentos_Recusados'
pedidos_enviados = 'Pedidos_Enviados'


@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    return jsonify(pedidos), 200

@app.route('/produtos', methods=['GET'])
def get_produtos():
    return jsonify(produtos), 200

@app.route('/carrinho', methods=['GET'])
def get_carrinho():
    return jsonify({"items": carrinho}), 200

@app.route('/carrinho/add', methods=['POST'])
def adicionar_carrinho():
    data = request.json
    produto_id = data.get("produtoId")
    produto = next((p for p in produtos if p["id"] == produto_id), None)
    if not produto:
        return jsonify({"message": "Produto não encontrado"}), 404

    existing_item = next((item for item in carrinho if item["produtoId"] == produto_id), None)
    if existing_item:
        existing_item["quantidade"] += 1
    else:
        carrinho.append({"produtoId": produto["id"], "nome": produto["nome"], "preco": produto["preco"], "quantidade": 1})

    return jsonify({"message": "Produto adicionado ao carrinho"}), 200

@app.route('/carrinho/remove', methods=['POST'])
def remover_carrinho():
    data = request.json
    produto_id = data.get("produtoId")
    existing_item = next((item for item in carrinho if item["produtoId"] == produto_id), None)
    if not existing_item:
        return jsonify({"message": "Produto não encontrado no carrinho"}), 404

    if existing_item["quantidade"] > 1:
        existing_item["quantidade"] -= 1
    else:
        carrinho.remove(existing_item)

    return jsonify({"message": "Produto removido do carrinho"}), 200

@app.route('/carrinho/checkout', methods=['POST'])
def efetivar_compra():

    if not carrinho:
        return jsonify({"message": "O carrinho está vazio"}), 400
    order = {
        "id": len(orders) + 1,
        "items": carrinho.copy(),
        "total": sum(item["preco"] * item["quantidade"] for item in carrinho),
        "status": "Pedido Criado"
    }
    pedidos.append(order)
    orders.append(order)
    print(orders)
    carrinho.clear()
    msg = "'Pedidos_Criados'"
    Publicar(pedidos_criados, order, msg)

    return jsonify({"message": "Compra efetivada", "order": order}), 200

@app.route('/pedidos/excluir', methods=['DELETE'])
def excluir_pedido():
    pedido = request.json
    pedido_id = pedido.get('id')
    if not pedido_id:
        return jsonify({"message": "ID do pedido não informado"}), 400
    for p in pedidos:
        if p['id'] == pedido_id:
            if p['status'] == 'Pedido excluido':
                return jsonify({"message": "Pedido já foi excluído"}), 400
            p['status'] = 'Pedido excluido'
            pedido['status'] = 'Pedido excluido'
            pedido['items'] = p['items']
            msg = "'Pedidos_Excluidos'"
            Publicar(pedidos_excluidos, pedido, msg)
            return jsonify({"message": "Pedido removido com sucesso"}), 200
    return jsonify({"message": "Pedido não encontrado"}), 404

        

def atualiza_status_pedido(dados_pedido):
    print(dados_pedido)
    for pedido in pedidos:
        if pedido['id'] == dados_pedido['id']:
            pedido['status'] = dados_pedido['status']
            break

def consome_pagamentos_aprovados():
    def callback(ch, method, properties, body):
        dados_pedido = json.loads(body)
        print(dados_pedido)
        atualiza_status_pedido(dados_pedido)

    msg = "[*] Principal - pagamentos aprovados - Waiting for messages."
    Consumir(pagamentos_aprovados, callback, msg)

def consome_pagamentos_recusados():
    def callback(ch, method, properties, body):
        dados_pedido = json.loads(body)
        msg = f"pedido {dados_pedido['id']} pagamento recusado"
        atualiza_status_pedido(dados_pedido)
        publicar = Publicar(pedidos_excluidos, dados_pedido, msg)
        print(dados_pedido)

    msg = "[*] Principal - pagamentos recusados - Waiting for messages."
    Consumir(pagamentos_recusados, callback, msg)
    
def consome_pedidos_enviados():
    def callback(ch, method, properties, body):
        dados_pedido = json.loads(body)
        atualiza_status_pedido(dados_pedido)

    msg = "[*] Principal - pedidos enviados - Waiting for messages."
    Consumir(pedidos_enviados, callback, msg)


if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pagamentos_aprovados)
    thread1.start()
    thread2 = threading.Thread(target=consome_pagamentos_recusados)
    thread2.start()
    thread3 = threading.Thread(target=consome_pedidos_enviados)
    thread3.start()
    app.run(debug=False, port=3000)
