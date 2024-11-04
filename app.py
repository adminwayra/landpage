from flask import Flask, render_template, send_from_directory, request
import os
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv('entorno.env')  # Cargar variables de entorno desde .env
app = Flask(__name__)

# Asegúrate de que la carpeta 'static' exista
STATIC_FOLDER = 'static'

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.json.get('text')  # Corregido para obtener el texto del JSON

    if not text:
        return {'error': 'No text provided'}, 400

    # Generar el archivo de audio
    audio_file = os.path.join(STATIC_FOLDER, 'audio.mp3')
    tts = gTTS(text, lang='es')
    tts.save(audio_file)

    return {'message': 'Audio generated', 'file': 'audio.mp3'}

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/mostrar-ruta')
def mostrar_ruta():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('mostrar-ruta.html', api_key=api_key)

@app.route('/nuestra-carta')
def carta():
    return render_template('carta.html')

if __name__ == '__main__':
    app.run(debug=True)
