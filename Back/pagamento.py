from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import pika
import threading
from publicar import Publicar
from consumir import Consumir
app = Flask(__name__)
CORS(app)

# topicos
#publica
pagamentos_aprovados = 'Pagamentos_Aprovados'
pagamentos_recusados = 'Pagamentos_Recusados'
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

def altera_status_pedido(pedido,pagamento): 
    pedido['status'] = 'Pagamento '+ pagamento 
    return pedido


def publica_pagamento_aprovado(pedido):
    publicar = Publicar(pagamentos_aprovados, pedido, " [x] Sent 'Pagamento Aprovado'")
def publica_pagamento_recusado(pedido):
    publicar = Publicar(pagamentos_recusados, pedido, " [x] Sent 'Pagamento Recusado'")

def consome_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        pagamento = input("Pagamento - aprovado/recusado: ")
        if(pedido):
            if(pagamento == 'aprovado'):
                print(pedido)
                print(type(pedido))
                pedido = altera_status_pedido(pedido,pagamento)
                publica_pagamento_aprovado(pedido)
            elif(pagamento == 'recusado'):
                print(pedido)
                print(type(pedido))
                pedido = altera_status_pedido(pedido,pagamento)
                publica_pagamento_recusado(pedido)
            else:
                print('opcao nao valida')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_criados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Pagamento Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pedidos_criados)
    thread1.start()
    app.run(debug=False, port=3001)

