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
from publicar import Publicar
pagamentos_aprovados = 'pagamentos_aprovados'
app = Flask(__name__)
CORS(app)

# topicos
#publica
pedidos_enviados = 'Pedidos_Enviados'
#consome
pagamentos_aprovados = 'Pagamentos_Aprovados'


def altera_status_pedido(pedido):
    pedido['status'] = 'Pedido enviado'
    return pedido



def consome_pagamentos_aprovados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        pedido = altera_status_pedido(pedido)
        publica_pedido_enviado(pedido)
        print("pagamento aprovado recebido")

    msg = "[*] Entrega - esperando pagamentos aprovados - Waiting for messages."
    Consumir(pagamentos_aprovados, callback, msg)


def publica_pedido_enviado(pedido):
    print(" PEDIDO ENVIADO  ________------------")
    msg = "'Pedido Enviado'"
    Publicar(pedidos_enviados, pedido, msg)

if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pagamentos_aprovados)
    thread1.start()
    app.run(debug=False, port=3001)
