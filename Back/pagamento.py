from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import pika
import threading

app = Flask(__name__)
CORS(app)

# topicos
#consome
pedidos_criados = 'Pedidos_Criados'
pedidos_excluidos = 'Pedidos_Excluidos'

pedidos = []
@app.route('/entrega', methods=['GET'])
def envia_produto(compra):
    nota = emitir_nota()
    return jsonify(), 200

def emitir_nota(compra):
    nota = compra
    return nota

def altera_status_pedido(pedido):
    pedido['status'] = 'Pagamento aprovado'
    return pedido

def publica_pagamento_aprovado(pedido):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='direct_loja', exchange_type='direct')
    channel.basic_publish(exchange='direct_loja', routing_key='Pagamentos_Aprovados', body=json.dumps(pedido))
    print(" [x] Sent 'Pagamento Aprovado'")
    connection.close()

def consume_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(pedido)
        pedido = altera_status_pedido(pedido)
        publica_pagamento_aprovado(pedido)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_criados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Pagamento Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    thread1 = threading.Thread(target=consume_pedidos_criados)
    thread1.start()
    app.run(debug=False, port=3001)

