from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from scraper import scrape_dni_info, init_browser, close_browser
from searchdni import get_dni_info

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Bienvenido a la API de Scrapeo de DNI. Utiliza /scrape?dni=NUMERO_DNI para obtener información.'
    })
class DniScraper(Resource):
    def get(self):
        dni = request.args.get('dni')
        if not dni:
            return {'error': 'DNI parameter is required'}, 400
        
        result = scrape_dni_info(dni)
        return jsonify(result)

class Dni(Resource):
    def get(self, dni):
        if not dni:
            return {'error': 'DNI parameter is required'}, 400
        return jsonify(get_dni_info(dni))
    
api.add_resource(DniScraper, '/scrape')
api.add_resource(Dni, '/dni/<dni>')

if __name__ == '__main__':
    init_browser()
    try:
        app.run(debug=True)
    finally:
        close_browser()
