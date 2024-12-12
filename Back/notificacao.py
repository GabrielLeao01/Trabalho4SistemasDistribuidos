import datetime
from flask import Flask, render_template
from flask_cors import CORS
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import pika
import threading
import json
from consumir import Consumir



app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost" 
app.register_blueprint(sse, url_prefix='/stream')

pedidos_criados = 'Pedidos_Criados'
pedidos_enviados = 'Pedidos_Enviados'
pagamentos_aprovados = 'Pagamentos_Aprovados'
pagamentos_recusados = 'Pagamentos_Recusados'
pedidos_excluidos = 'Pedidos_Excluidos'


def consome_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"novo pedido criado, enviando sse {pedido}")
        with app.app_context():
            message = f"Pedido {pedido['id']} criado"
            sse.publish({"message": message}, type='publish')

    msg = ' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C'
    Consumir(pedidos_criados, callback, msg)


def consome_Pagamentos_aprovados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pagamento aprovado, enviando sse {pedido}")
        with app.app_context():
            message = f"Pedido {pedido['id']} - pagamento aprovado"
            sse.publish({"message": message}, type='publish')
        
    msg = ' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C'
    Consumir(pagamentos_aprovados, callback, msg)

def consome_pagamento_recusado():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pagamento recusado, enviando sse {pedido}")
        with app.app_context():
            message =f"Pedido {pedido['id']} - pagamento recusado"
            sse.publish({"message": message}, type='publish')
        
    msg = ' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C'
    Consumir(pagamentos_recusados, callback, msg)

def consome_pedido_enviado():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pedido enviado, enviando sse {pedido}")
        with app.app_context():
            #sse.publish({"message": pedido}, type='publish')
            message = f"Pedido {pedido['id']} enviado"
            sse.publish({"message": message}, type='publish')

        
    msg = ' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C'
    Consumir(pedidos_enviados, callback, msg)
    

def consome_pedido_excluido():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pedido excluido, enviando sse {pedido}")
        with app.app_context():
            #sse.publish({"message": pedido}, type='publish')
            message = f"Pedido {pedido['id']} excluido"
            sse.publish({"message": message}, type='publish')

    msg = ' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C'  
    Consumir(pedidos_excluidos, callback, msg)

                
if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pedidos_criados)
    thread1.start()
    thread2 = threading.Thread(target=consome_Pagamentos_aprovados)
    thread2.start()
    thread3 = threading.Thread(target=consome_pagamento_recusado)
    thread3.start()
    thread4 = threading.Thread(target=consome_pedido_enviado)
    thread4.start()
    thread5 = threading.Thread(target=consome_pedido_excluido)
    thread5.start()
    app.run(debug=False, port=3006)
