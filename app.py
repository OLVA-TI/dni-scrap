from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from scraper import scrape_dni_info

app = Flask(__name__)
api = Api(app)

class DniScraper(Resource):
    def get(self):
        dni = request.args.get('dni')
        if not dni:
            return {'error': 'DNI parameter is required'}, 400
        
        result = scrape_dni_info(dni)
        return jsonify(result)

api.add_resource(DniScraper, '/scrape')

if __name__ == '__main__':
    app.run(debug=True)
