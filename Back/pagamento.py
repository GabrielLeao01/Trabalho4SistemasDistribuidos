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
import requests
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
pedidos_aguardando_pagamento = []

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    return jsonify(pedidos_aguardando_pagamento), 200

@app.route('/pagamento', methods=['POST'])
def pagamento_efetuado():
    pedido = request.json()
    json.loads(pedido)
    print(pedido)

    if(pedido):            
        if(pedido['status'] == 'Pagamento aprovado'):
                publica_pagamento_aprovado(pedido)
        elif(pedido['status'] == 'Pagamento recusado'):
                publica_pagamento_recusado(pedido)
        else:
                print('opcao nao valida')

def publica_pagamento_aprovado(pedido):
    Publicar(pagamentos_aprovados, pedido, "'Pagamento Aprovado'")
def publica_pagamento_recusado(pedido):
    Publicar(pagamentos_recusados, pedido, "'Pagamento Recusado'")

def consome_pedidos_criados():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        
        print(body)
        pedido = json.dumps(pedido)
        headers = {'Content-Type': 'application/json'}  
        response = requests.post('http://localhost:3010/webhook', json=pedido, headers=headers)  
        print(response.status_code, response.text)

    msg = ' [*] Pagamento Waiting for messages. To exit press CTRL+C'
    Consumir(pedidos_criados, callback, msg)


if __name__ == '__main__':
    thread1 = threading.Thread(target=consome_pedidos_criados)
    thread1.start()
    app.run(debug=False, port=3001)

