import pika

class Consumir:
    def __init__(self, routing_key, callback, msg = ''):
        if not routing_key and not callback and not msg:
            raise ValueError("Parametro routing_key, callback sao obrigatorio.")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange='direct_loja', queue=self.queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        print(msg)
        self.channel.start_consuming()
