from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_cors import CORS
from scraper import fetch_dni_from_api
from searchdni import get_dni_info

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Bienvenido a la API de Scrapeo de DNI. Utiliza /scrape?dni=NUMERO_DNI para obtener información.'
    })

class DniScraper(Resource):
    def get(self, dni):
        if not dni:
            return error_response('DNI parameter is required', 400)
        
        result = fetch_dni_from_api(dni)
        return jsonify(result)

class Dni(Resource):
    def get(self, dni):
        if not dni:
            return error_response('DNI parameter is required', 400)
        response = get_dni_info(dni)
        if not response['success']:
            return make_response(jsonify(response), 204)
        return make_response(jsonify(response), 200)
    
def error_response(message, status_code):
    return make_response(jsonify({'error': message}), status_code)

api.add_resource(DniScraper, '/scrape/<dni>')
api.add_resource(Dni, '/dni/<dni>')

if __name__ == '__main__':
    app.run(debug=True)
