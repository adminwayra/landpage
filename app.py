from flask import Flask,render_template, send_from_directory, request, jsonify, session
import json
import os
import re
from gtts import gTTS
import uuid
#from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from datetime import datetime
from models import Plato, db,Cliente,Pedido,DetallePedido,Perfil  # Asegúrate de importar los modelos
import pymysql
from dotenv import load_dotenv
import secrets
# Cargar variables de entorno desde .env
load_dotenv("entorno.env")
# Inicializamos Flask
app = Flask(__name__)
# Configurar una clave secreta para las sesiones
app.secret_key = secrets.token_hex(16)  # Generar una clave secreta segura
# Asegúrate de usar la carpeta estática dentro de la raíz de la aplicación
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

api_key_google = os.getenv("GOOGLE_MAPS_API_KEY")
# Cargar respuestas desde un archivo JSON

# Inicializar el estado de la conversación
conversacion_estado = {}


# Función para normalizar opciones y el mensaje
def normalizar_texto(texto):
    # Quitar emojis y caracteres especiales
    texto = re.sub(r"[^\w\s]", "", texto)
    # Convertir a minúsculas y quitar espacios adicionales
    return texto.lower().strip()
def es_correo_valido(correo):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, correo)

# Configuración de tu base de datos en PythonAnywhere
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Configuración de SSH
ssh_host = os.getenv("SSH_HOST")
ssh_user = os.getenv("SSH_USER")
ssh_password = os.getenv("SSH_PASSWORD")  # Asegúrate de usar la contraseña correcta

# Establecer túnel SSH
def create_ssh_tunnel():
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=('richarchipanapeceros.mysql.pythonanywhere-services.com', 3306)
    )
    tunnel.start()  # Inicia el túnel SSH
    return tunnel

# Conexión a la base de datos MySQL
def connect_to_database():
    tunnel = create_ssh_tunnel()  # Inicia el túnel SSH
    connection = pymysql.connect(
        user=db_user,
        passwd=db_password,
        host='127.0.0.1',  # Usamos localhost debido al túnel SSH
        port=tunnel.local_bind_port,  # Usamos el puerto local del túnel
        db=db_name
    )
    return connection, tunnel  # Regresa tanto la conexión como el túnel para cerrarlo más tarde

# Crear conexión a la base de datos y configurar SQLAlchemy
connection, tunnel = connect_to_database()

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@127.0.0.1:{tunnel.local_bind_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
#db = SQLAlchemy(app)
db.init_app(app)

with app.app_context():
    db.create_all() 
@app.route('/buscar_cliente/<correo>', methods=['GET'])
def buscar_cliente(correo):
    try:
        # Buscar el cliente por correo
        cliente = Cliente.query.filter_by(correo=correo).first()

        if cliente:
            return jsonify({'id_cliente': cliente.id_cliente}), 200
        else:
            return jsonify({'error': 'Cliente no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Ruta para agregar registros a la tabla 'perfiles'
@app.route('/agregar_perfil', methods=['POST'])
def agregar_perfil():
    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()

    # Verificar que se recibieron los datos correctamente
    if 'nombre_perfil' not in data:
        return jsonify({"error": "El campo 'nombre_perfil' es requerido"}), 400

    # Crear una nueva instancia del modelo Perfil
    nuevo_perfil = Perfil(nombre_perfil=data['nombre_perfil'])

    try:
        # Agregar el nuevo perfil a la sesión
        db.session.add(nuevo_perfil)
        db.session.commit()  # Confirmar los cambios en la base de datos

        return jsonify({"message": "Perfil agregado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()  # Deshacer la transacción si algo sale mal
        return jsonify({"error": "Hubo un error al agregar el perfil", "details": str(e)}), 500

@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():
    try:
        # Obtener los datos del pedido desde el cuerpo de la solicitud
        data = request.get_json()
        
        id_cliente = data.get('id_cliente')  # Ya lo obtienes del frontend
        total = float(data.get('total'))
        detalles = data.get('detalles')
        
        # Crear un nuevo pedido
        nuevo_pedido = Pedido(id_cliente=id_cliente, total=total,id_status_pedido=1,id_canal_distribucion=1)
        db.session.add(nuevo_pedido)
        db.session.commit()  # Insertar el pedido y obtener el id_pedido generado

        # Insertar los detalles del pedido
        for detalle in detalles:
            id_producto = detalle.get('id_producto')
            cantidad = detalle.get('cantidad')
            precio = float(detalle.get('precio'))
            
            
            nuevo_detalle = DetallePedido(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=id_producto,
                cantidad=cantidad,
                precio=precio
            )
            db.session.add(nuevo_detalle)
            db.session.commit()

        
        
        return jsonify({'message': 'Pedido agregado con éxito', 'id_pedido': nuevo_pedido.id_pedido}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route("/platos", methods=["GET"])
def obtener_platos():
    try:
        # Consulta a la base de datos para obtener todos los platos
        platos = Plato.query.all()

        # Convertimos la lista de platos en un diccionario de datos
        platos_data = [
            {
                "id_plato": plato.id_plato,
                "nombre": plato.nombre,
                "descPlato": plato.descPlato,
                "precioVenta": plato.precioVenta,
                "dcto": plato.dcto,
                "imagen": plato.imagen,
                "constante": plato.constante,
                "disponible": plato.disponible,
                "id_tipo_plato": plato.id_tipo_plato,
            }
            for plato in platos
        ]

        # Devolvemos la respuesta como JSON
        return jsonify(platos_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    try:
        # Obtener los datos del cliente desde el cuerpo de la solicitud
        data = request.get_json()

        nombre = data.get('nombre')
        direccion = data.get('direccion')
        correo = data.get('correo')
        id_perfil = data.get('id_perfil')

        # Verificar que los datos sean válidos
        if not nombre or not direccion or not correo:
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400
        if not es_correo_valido(correo):
            return jsonify({'error': 'Correo no válido'}), 400

        # Validar que el cliente no exista ya en la base de datos
        if Cliente.query.filter_by(correo=correo).first():
            return jsonify({'error': 'El correo ya ha sido registrado'}), 400

        # Crear una nueva instancia del cliente
        nuevo_cliente = Cliente(nombre=nombre, direccionEnvio=direccion, correo=correo, id_perfil=id_perfil)

        # Insertar el cliente en la base de datos
        db.session.add(nuevo_cliente)
        db.session.commit()

        return jsonify({'message': 'Cliente agregado con éxito', 'id_cliente': nuevo_cliente.id_cliente}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/cargar_platos", methods=["GET"])
def cargar_platos():
    # Definir la ruta del archivo JSON
    STATIC_FOLDER = "static"  # Cambia esto si la carpeta está en otro lugar
    path = os.path.join(STATIC_FOLDER, "platos.json")

    try:
        # Abrir y cargar el archivo JSON
        with open(path, "r", encoding="utf-8") as f:
            platos_data = json.load(f)

        # Agregar los platos a la base de datos
        for plato_data in platos_data:
            plato = Plato(
                nombre=plato_data["nombre"],
                descPlato=plato_data["descPlato"],
                dcto=plato_data["dcto"],
                precioVenta=plato_data["precioVenta"],
                precioCompra=0,
                imagen=plato_data["imagen"],
                id_tipo_plato=plato_data["id_tipo_plato"],
            )
            db.session.add(plato)
            db.session.commit()

        # Confirmar los cambios en la base de datos
        db.session.commit()
        return jsonify({"message": "Platos cargados exitosamente!"}), 200

    except FileNotFoundError:
        return jsonify({"error": "Archivo respuestas.json no encontrado"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al cargar los platos", "details": str(e)}), 500

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")


# Crear la carpeta 'static' si no existe
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)


@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    text = request.json.get("text")  # Corregido para obtener el texto del JSON

    if not text:
        return {"error": "No text provided"}, 400

    try:
        # Generar el archivo de audio en la carpeta 'static'
        audio_file = os.path.join(STATIC_FOLDER, "audio.mp3")
        tts = gTTS(text, lang="es")
        tts.save(audio_file)
        # El archivo de audio estará accesible desde '/static/audio.mp3'
        return {"message": "Audio generated", "file": "/static/audio.mp3"}
    except Exception as e:
        return {"error": f"Error generating audio: {str(e)}"}, 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)


@app.route("/")
def inicio():
    # Cargar ofertas desde un archivo JSON en la carpeta static
    path = os.path.join(STATIC_FOLDER, "ofertas.json")
    with open(path, "r", encoding="utf-8") as f:
        ofertas = json.load(f)
    return render_template("inicio.html", productos=ofertas)

@app.route("/chat", methods=["POST"])
def chat():

    # Cargar el archivo respuestas.json
    path = os.path.join(STATIC_FOLDER, "respuestas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            respuestas = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Archivo respuestas.json no encontrado"}), 500

    # Obtener el mensaje del usuario y normalizarlo
    user_message = normalizar_texto(request.json.get("message", ""))
    user_id = request.json.get("user_id")

    # Si no hay user_id, generar uno nuevo
    if not user_id:
        user_id = str(uuid.uuid4())

    # Manejo de estado del usuario
    if user_id not in conversacion_estado:
        conversacion_estado[user_id] = {
            "estado": "estado_inicial",
            "last_updated": datetime.now(),
        }
    else:
        conversacion_estado[user_id]["last_updated"] = datetime.now()

    estado_actual = conversacion_estado[user_id]["estado"]

    # Log para depuración
    app.logger.info(
        f"User ID: {user_id}, Estado actual: {estado_actual}, Mensaje original: {user_message}"
    )

    # Obtener las opciones correspondientes al estado actual
    respuesta = respuestas.get(estado_actual, {"mensaje": "Error", "opciones": []})

    # Normalizar las opciones para compararlas con el mensaje del usuario
    opciones_normalizadas = [
        normalizar_texto(opcion) for opcion in respuesta.get("opciones", [])
    ]
    app.logger.warning(f"Mensaje no reconocido: {opciones_normalizadas}")
    app.logger.warning(f"Mensaje no reconocido: {user_message}")

    # Verificar si el mensaje del usuario coincide con una opción válida
    if user_message in opciones_normalizadas:
        # Actualizar el estado según el mensaje del usuario
        if user_message == "ver menú":
            conversacion_estado[user_id]["estado"] = "ver_menu"
        elif user_message == "ver horario":
            conversacion_estado[user_id]["estado"] = "ver_horario"
        elif user_message == "volver al inicio":
            conversacion_estado[user_id]["estado"] = "estado_inicial"
        elif user_message == "hacer un pedido":
            conversacion_estado[user_id]["estado"] = "hacer_pedido"
        elif user_message == "ver ofertas":
            conversacion_estado[user_id]["estado"] = "ver_ofertas"
        elif user_message == "informacion de contacto":
            conversacion_estado[user_id]["estado"] = "informacion_contacto"

        # Actualizar la respuesta según el nuevo estado
        estado_actual = conversacion_estado[user_id]["estado"]
        respuesta = respuestas.get(estado_actual, {"mensaje": "Error", "opciones": []})
    else:
        app.logger.warning(f"Mensaje no reconocido: {user_message}")
        respuesta = {
            "mensaje": "Lo siento, no entendí tu mensaje. Por favor, selecciona una opción válida.",
            "opciones": respuesta.get("opciones", []),
        }
    # Retornar la respuesta al frontend
    if estado_actual == "ver_menu":
        detalles = respuesta.get("detalles", [])
        # Concatenar las ofertas, asegurando que los saltos de línea sean bien interpretados
        ofertas_concatenadas = ""
        for oferta in detalles:
            ofertas_concatenadas += (
                f"📌 *{oferta['titulo']}*:{oferta['descripcion']}\n\n"
            )
        # Aseguramos que las ofertas concatenadas se agreguen correctamente al mensaje
        respuesta["mensaje"] = f"{respuesta['mensaje']}\n\n{ofertas_concatenadas}"
    # Generar mensaje dinámico para "ver_ofertas"
    if estado_actual == "ver_ofertas":
        detalles = respuesta.get("detalles", [])
        ofertas_concatenadas = "\n\n".join(
            [
                f"📌 *{oferta['titulo']}*\n{oferta['descripcion']}\n*Válido hasta:* {oferta['valido_hasta']}"
                for oferta in detalles
            ]
        )
        respuesta["mensaje"] = f"{respuesta['mensaje']}\n\n{ofertas_concatenadas}"
    if estado_actual == "ver_horario":
        detalles = respuesta.get("detalles", [])
        horarios_concatenados = "\n\n".join(
            [f" ⌚*{oferta['dia']}*\n{oferta['horario']}" for oferta in detalles]
        )
        respuesta["mensaje"] = f"{respuesta['mensaje']}\n\n{horarios_concatenados}"
    return jsonify(
        {
            "user_id": user_id,
            "response": respuesta["mensaje"],
            "options": respuesta.get("opciones", []),
        }
    )


@app.route("/mostrar-ruta")
def mostrar_ruta():

    return render_template("mostrar-ruta.html", api_key_google=api_key_google)


@app.route("/quienes-somos")
def quienes_somos():

    return render_template("quienes-somos.html")


@app.route("/nuestros-clientes")
def stories():

    return render_template("stories.html")


@app.route("/ruleta-premios")
def ruleta():
    return render_template("ruleta.html")

# Ruta para guardar el código del premio en la sesión
@app.route("/guardar_codigo/<codigo>")
def guardar_codigo(codigo):
    # Guardamos el código del premio en la sesión
    session['codigo'] = codigo
    return "", 204  # Responder vacío con código de estado 204


# Ruta para la página de la carta
@app.route("/nuestra-carta")
def carta():
    # Obtener el código del premio desde la URL y guardarlo en la sesión
    codigo_premio = request.args.get('codigo', 0)  # Si no hay código, se asigna 0
    session['codigo'] = codigo_premio  # Guardamos el código en la sesión

    # Pasar el código de premio a la plantilla
    return render_template("carta.html",  codigo_premio=codigo_premio)

@app.route("/premios")
def premios():
    return jsonify(
        {
            "premios": [
                {"codigo": 10, "premio": "10% de descuento"},
                {"codigo": 15, "premio": "15% de descuento"},
                {"codigo": 20, "premio": "20% de descuento"},
                {"codigo": 25, "premio": "25% de descuento"},
                {"codigo": 30, "premio": "30% de descuento"},
                {"codigo": 0, "premio": "No tienes premio"},
                {"codigo": 35, "premio": "35% de descuento"}
            ]
        }
    )

# Ejecutar la aplicación
if __name__ == '__main__':
    try:
        app.run(debug=True)  # Ejecuta Flask
    finally:
        connection.close()  # Asegúrate de cerrar la conexión cuando termines
        tunnel.stop()  # Cierra el túnel SSH cuando finalices la ejecución
