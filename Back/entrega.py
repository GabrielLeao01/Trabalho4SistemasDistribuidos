from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import pika
import threading

pagamentos_aprovados = 'pagamentos_aprovados'
app = Flask(__name__)
CORS(app)

# topicos
#publica
pedidos_enviados = 'Pedidos_Enviados'
#consome
pagamentos_aprovados = 'Pagamentos_Aprovados'

@app.route('/entrega', methods=['GET'])
def envia_produto(compra):
    nota = emitir_nota()
    return jsonify(), 200

def emitir_nota(compra):
    nota = compra
    return nota

def altera_status_pedido(pedido):
    pedido['status'] = 'Pedido enviado'
    return pedido

def consome_pagamentos_aprovados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        pedido = altera_status_pedido(pedido)
        publica_pedido_enviado(pedido)
        print("pagamento aprovado recebido")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pagamentos_aprovados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def publica_pedido_enviado(pedido):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='direct_loja', exchange_type='direct')
    channel.basic_publish(exchange='direct_loja', routing_key='Pedidos_Enviados', body=json.dumps(pedido))
    print(" [x] Sent 'pedido enviado'")
    connection.close()

if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pagamentos_aprovados)
    thread1.start()
    app.run(debug=False, port=3001)
