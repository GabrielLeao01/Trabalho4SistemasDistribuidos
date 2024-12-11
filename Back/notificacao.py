import datetime
from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import pika
import threading
import json


app = Flask(__name__)
app.config["SSE_REDIS_URL"] = "redis://localhost" 
app.register_blueprint(sse, url_prefix='/stream')

#topicos
#consome
pedidos_criados = 'Pedidos_Criados'


def consume_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"novo pedido criado, enviando sse {pedido}")
        with app.app_context():
            sse.publish({"message": pedido}, type='publish')
        
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key=pedidos_criados)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def consume_Pagamentos_aprovados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pagamento aprovado, enviando sse {pedido}")
        with app.app_context():
            sse.publish({"message": pedido}, type='publish')
        
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key='pagamentos_aprovados')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def consume_pagamento_recusado():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pagamento recusado, enviando sse {pedido}")
        with app.app_context():
            sse.publish({"message": pedido}, type='publish')
        
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key='pagamentos_recusados')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def consume_pedido_enviado():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"pedido enviado, enviando sse {pedido}")
        with app.app_context():
            #sse.publish({"message": pedido}, type='publish')
            sse.publish({"message": datetime.datetime.now()}, type='publish')

        
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='direct_loja', queue=queue_name, routing_key='Pedidos_Enviados')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] NOTIFICACAO Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
                
if __name__ == '__main__':
    thread1 = threading.Thread(target=consume_pedidos_criados)
    thread1.start()
    #thread2 = threading.Thread(target=consume_Pagamentos_aprovados)
    #thread2.start()
    #thread3 = threading.Thread(target=consume_pagamento_recusado)
    #thread3.start()
    #thread4 = threading.Thread(target=consume_pedido_enviado)
    #thread4.start()

    app.run(debug=False, port=6379)
