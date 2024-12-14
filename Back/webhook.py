from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
import json
import requests
import threading

app = Flask(__name__)
CORS(app)
def envia_resultado_pagamento(pedido):
    print('enviando resultado do pagamento')
    response = requests.post('http://localhost:3012/pagamento', json=pedido)
    print(response)
    
thread = threading.Thread(target=envia_resultado_pagamento)
@app.route('/webhook', methods=['POST'])
def efetivar_compra():
    pedido = request.get_json()
    pagamento = input("Pagamento - aprovado/recusado: ")
    pedido = altera_status_pedido(pedido,pagamento)
    envia_resultado_pagamento(pedido)
    return jsonify({
        "msg": "Informações recebidas"
    })


def altera_status_pedido(pedido,pagamento): 
    pedido['status'] = 'Pagamento '+ pagamento 
    return pedido

if __name__ == '__main__':

    app.run(debug=False, port=3010)