from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask import Flask, render_template
import json
import requests

app = Flask(__name__)
CORS(app)

@app.route('/webhook', methods=['POST'])
def efetivar_compra():
    pedido = request.json()
    pagamento = input("Pagamento - aprovado/recusado: ")
    pedido = altera_status_pedido(pedido,pagamento)
    try:
        response = requests.post('http://localhost:3001/pagamento',json.dumps(pedido) )
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
        exit(1)

def altera_status_pedido(pedido,pagamento): 
    pedido['status'] = 'Pagamento '+ pagamento 
    return pedido

if __name__ == '__main__':

    app.run(debug=False, port=3010)