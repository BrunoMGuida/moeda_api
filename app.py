from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import requests
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)  # Libera CORS para todas as origens (útil para desenvolvimento)
swagger = Swagger(app)

API_URL = "https://api.frankfurter.app/latest"

def converter_moeda(origem, destino, valor):
    try:
        valor = float(valor)
    except ValueError:
        return None, None, "Valor inválido"

    if origem.upper() == destino.upper():
        # mesma moeda, retorna valor original e horário atual UTC
        horario = datetime.now(timezone.utc).isoformat()
        return valor, horario, None

    params = {
        "from": origem.upper(),
        "to": destino.upper()
    }

    resposta = requests.get(API_URL, params=params)

    if resposta.status_code != 200:
        return None, None, "Erro ao acessar provedor externo"

    dados = resposta.json()

    taxas = dados.get("rates")
    if not taxas or destino.upper() not in taxas:
        return None, None, f"Não foi possível obter taxa de câmbio para {destino.upper()}"

    taxa = taxas[destino.upper()]
    resultado = round(valor * taxa, 4)

    # A API retorna a data da cotação, adiciono horário atual UTC para maior precisão
    horario = datetime.now(timezone.utc).isoformat()

    return resultado, horario

@app.route('/converter', methods=['GET'])
def api_converter():
    """
    Converte valor entre moedas
    ---
    parameters:
      - name: origem
        in: query
        type: string
        required: true
        description: "Código da moeda origem (ex: BRL)"
      - name: destino
        in: query
        type: string
        required: true
        description: "Código da moeda destino (ex: USD)"
      - name: valor
        in: query
        type: number
        required: true
        description: Valor a ser convertido
    responses:
      200:
        description: Valor convertido com horário da cotação
        schema:
          type: object
          properties:
            valor_convertido:
              type: number
              example: 17.821
            horario_cotacao:
              type: string
              example: "2025-05-15T01:45:30.123456+00:00"
            erro:
              type: string
              example: null
    """
    origem = request.args.get('origem')
    destino = request.args.get('destino')
    valor = request.args.get('valor')

    if not origem or not destino or not valor:
        return jsonify({"valor_convertido": None, "horario_cotacao": None, "erro": "Parâmetros obrigatórios faltando"}), 400

    resultado, horario = converter_moeda(origem, destino, valor)
    return jsonify({
        "valor_convertido": resultado,
        "horario_cotacao": horario
    })

# if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8080)
