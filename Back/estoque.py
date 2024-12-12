from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import pika
import threading
from consumir import Consumir

app = Flask(__name__)
CORS(app)
produtos = [
    {"id": 1, "nome": "Produto A", "preco": 50.0, "estoque": 30},
    {"id": 2, "nome": "Produto B", "preco": 75.0, "estoque": 20},
    {"id": 3, "nome": "Produto C", "preco": 100.0, "estoque": 40},
]
carrinho = []
orders = []
# topicos
#consome
pedidos_criados = 'Pedidos_Criados'
pedidos_excluidos = 'Pedidos_Excluidos'
pagamentos_recusados = 'Pagamentos_Recusados'


@app.route('/estoque', methods=['GET'])
def get_estoque():
    return jsonify(produtos), 200

@app.route('/estoque/remove', methods=['DELETE'])
def remover_produto(p):
    global produtos
    produtos = [produto for produto in produtos if produto["id"] != p['id']]
    return jsonify({"items": carrinho}), 200

@app.route('/estoque/add', methods=['POST'])
def adiciona_produto(produto):
    produtos.append(produto)
    return jsonify({"message": "Produto adicionado ao estoque"}), 200

def consome_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        #orders.append(pedido)
        print(f"Novo pedido criado: {pedido}")
        print(type(pedido))
        if isinstance(pedido, dict):
            print(pedido)
            for item in pedido['items']:
                for produto in produtos:
                    if produto['id'] == item['produtoId']:
                        if (produto['estoque'] - item['quantidade']) >= 0:
                            print(item)
                            print(f"produto {item['produtoId']} removido do estoque")
                            produto['estoque'] -= item['quantidade']
                        else:
                            print(f"nao ha produtos {produto['id']} suficientes no estoque")
        else: 
            print("Erro: pedido não é um dicionário") 

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_criados)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] ESTOQUE Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

def consome_pedidos_excluidos():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        #orders.append(pedido)
        print("pagamento excluido, retornando itens no estoque")
        if isinstance(pedido, dict): 
            for item in pedido['items']:
                for produto in produtos:
                    if produto['id'] == item['produtoId']:
                        print(f"produto {item['produtoId']} adicionado ao estoque")
                        produto['estoque'] += item['quantidade']
        else: 
            print("Erro: pedido não é um dicionário") 
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_excluidos)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] ESTOQUE EXLCUIDOS Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()          
          
if __name__ == '__main__':
    thread_consome_pedidos_criados = threading.Thread(target=consome_pedidos_criados)
    thread_consome_pedidos_criados.start()
    thread_consome_pagamentos_recusados = threading.Thread(target=consome_pedidos_excluidos)
    thread_consome_pagamentos_recusados.start()
    app.run(debug=False, port=3002)

