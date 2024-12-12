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
# topicos
#publica
pedidos_criados = 'Pedidos_Criados'
pedidos_excluidos = 'Pedidos_Excluidos'
#consome
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
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='direct_loja', exchange_type='direct')

    message = json.dumps(order)
    print(message)
    channel.basic_publish(exchange='direct_loja', routing_key=pedidos_criados, body=message)
    connection.close()

    return jsonify({"message": "Compra efetivada", "order": order}), 200

@app.route('/pedidos/excluir', methods=['DELETE'])
def excluir_pedido():
    pedido = request.json
    for p in pedidos:
        if(p['id'] == pedido['id'] and not (p['status'] == 'Pedido excluido')):
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.exchange_declare(exchange='direct_loja', exchange_type='direct')
            pedido['status'] = 'Pedido excluido'
            p['status'] = pedido['status']
            pedido['items'] = p['items']
            message = json.dumps(pedido)
            print(message)
            channel.basic_publish(exchange='direct_loja', routing_key=pedidos_excluidos, body=message)
            connection.close()
            return jsonify({"message": "Pedido removido"}), 200
        else:
            return jsonify({"message": "Pedido não existe"}), 404

        

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
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pagamentos_aprovados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("[*] Principal - pagamentos aprovados - Waiting for messages.")
    channel.start_consuming()

def consome_pagamentos_recusados():
    def callback(ch, method, properties, body):
        dados_pedido = json.loads(body)
        msg = f"pedido {dados_pedido['id']} pagamento recusado"
        atualiza_status_pedido(dados_pedido)
        publicar = Publicar(pedidos_excluidos, dados_pedido, msg)
        print(dados_pedido)
    msg = "[*] Principal - pagamentos recusados - Waiting for messages."
    #consumir = Consumir(pagamentos_recusados, callback, msg)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pagamentos_recusados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(msg)
    channel.start_consuming()

def consome_pedidos_enviados():
    def callback(ch, method, properties, body):
        dados_pedido = json.loads(body)
        atualiza_status_pedido(dados_pedido)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_enviados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("[*] Principal - pedidos enviados - Waiting for messages.")
    channel.start_consuming()

if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pagamentos_aprovados)
    thread1.start()
    thread2 = threading.Thread(target=consome_pagamentos_recusados)
    thread2.start()
    thread3 = threading.Thread(target=consome_pedidos_enviados)
    thread3.start()
    app.run(debug=False, port=3000)
