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

def altera_status_pedido(pedido,pagamento): 
    pedido['status'] = 'Pagamento '+ pagamento 
    return pedido


def publica_pagamento_aprovado(pedido):
    Publicar(pagamentos_aprovados, pedido, "'Pagamento Aprovado'")
def publica_pagamento_recusado(pedido):
    Publicar(pagamentos_recusados, pedido, "'Pagamento Recusado'")

def consome_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        pagamento = input("Pagamento - aprovado/recusado: ")
        if(pedido):
            start_time = time.time()
            while True:
                if time.time() - start_time > 10:
                    print("Timeout: Cliente não realizou o pagamento em 30 segundos.")
                    pagamento = 'recusado'
                    break
                pagamento = input("Pagamento - aprovado/recusado: ")
                if pagamento in ['aprovado', 'recusado']:
                    break
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

    msg = ' [*] Pagamento Waiting for messages. To exit press CTRL+C'
    Consumir(pedidos_criados, callback, msg)

if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pedidos_criados)
    thread1.start()
    app.run(debug=False, port=3001)

