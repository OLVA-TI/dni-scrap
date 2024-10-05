from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_cors import CORS
from scraper import fetch_dni_from_api
from searchdni import get_dni_info
from searchruc import get_ruc_info

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Bienvenido a la API de consulta de DNI y RUC'
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
        _source = request.args.get('source', 'OLVA')
        response = get_dni_info(dni, _source)
        if not response['success']:
            return make_response(jsonify(response), 204)
        return make_response(jsonify(response), 200)
    
class Ruc(Resource):
    def get(self, ruc):
        if not ruc:
            return error_response('RUC parameter is required', 400)
        _source = request.args.get('source', 'OLVA')
        response = get_ruc_info(ruc, _source)
        if not response['success']:
            return make_response(jsonify(response), 204)
        return make_response(jsonify(response), 200)
    
def error_response(message, status_code):
    return make_response(jsonify({'error': message}), status_code)

api.add_resource(DniScraper, '/scrape/<dni>')
api.add_resource(Dni, '/dni/<dni>')
api.add_resource(Ruc, '/ruc/<ruc>')

if __name__ == '__main__':
    app.run(debug=True)
