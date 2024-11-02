from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv('entorno.env')

app = Flask(__name__)
CORS(app)

RESTAURANTE_UBICACION = {
    "lat": -12.0764,
    "lng": -77.0638
}


@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    data = request.json

    if 'userLocation' not in data:
        return jsonify({'error': 'Ubicación del usuario no proporcionada'}), 400
    
    user_location = data['userLocation']
    

    if 'lat' not in user_location or 'lng' not in user_location:
        return jsonify({'error': 'Coordenadas inválidas'}), 400

    directions_api_url = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {
        'origin': f"{user_location['lat']},{user_location['lng']}",
        'destination': f"{RESTAURANTE_UBICACION['lat']},{RESTAURANTE_UBICACION['lng']}",
        'key': os.getenv('GOOGLE_MAPS_API_KEY')
    }

    try:
        response = requests.get(directions_api_url, params=params)
        response.raise_for_status()
        directions = response.json()

        if directions['status'] == 'OK':
            route = directions['routes'][0]
            distance = route['legs'][0]['distance']['text']
            duration = route['legs'][0]['duration']['text']
            return jsonify({
                'destination': RESTAURANTE_UBICACION,
                'distance': distance,
                'duration': duration,
                'status': 'OK'
            })
        else:
            return jsonify({'error': 'No se pudo calcular la ruta', 'status': directions['status']}), 400

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Error en la comunicación con la API de Google', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
