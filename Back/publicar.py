import pika
import json
class Publicar:
    def __init__(self, routing_key, body, msg = ''):
        if not routing_key and not body and not msg:
            raise ValueError("Parametros routing_key, body sao obrigatorio.")
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='direct_loja', exchange_type='direct')
        print(f" [x] Sent {msg}")
        channel.basic_publish(exchange='direct_loja', routing_key=routing_key, body=json.dumps(body))
        connection.close()

