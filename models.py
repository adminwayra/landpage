from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Tabla para tipos de platos
class TipoPlato(db.Model):
    __tablename__ = 'tipo_platos'
    
    id_tipo_plato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_tipo_plato = db.Column(db.String(50), nullable=False)

    platos = db.relationship('Plato', back_populates='tipo_plato', lazy=True)

    def __repr__(self):
        return f"<TipoPlato {self.nombre_tipo_plato}>"

# Tabla para canales de distribución
class CanalDistribucion(db.Model):
    __tablename__ = 'canales_distribucion'
    
    id_canal_distribucion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_canal = db.Column(db.String(50), nullable=False)

    pedidos = db.relationship('Pedido', back_populates='canal_distribucion', lazy=True)

    def __repr__(self):
        return f"<CanalDistribucion {self.nombre_canal}>"

# Modificación de la tabla Plato para agregar la relación con TipoPlato
class Plato(db.Model):
    __tablename__ = 'plato'

    id_plato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descPlato = db.Column(db.String(500), nullable=True)
    dcto = db.Column(db.Integer, nullable=False, default=0)
    precioVenta = db.Column(db.Float, nullable=False)
    precioCompra = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    disponible = db.Column(db.Boolean, default=True)
    constante = db.Column(db.Boolean, default=False)

    # Clave foránea para el tipo de plato
    id_tipo_plato = db.Column(db.Integer, db.ForeignKey('tipo_platos.id_tipo_plato'), nullable=False)
    tipo_plato = db.relationship('TipoPlato', back_populates='platos', lazy=True)
    detalle_pedidos = db.relationship('DetallePedido', back_populates='plato', lazy=True)
    

    def __init__(self, nombre, descPlato, dcto, precioVenta, precioCompra,imagen=None, disponible=True, constante=False, id_tipo_plato=None):
        self.nombre = nombre
        self.descPlato = descPlato
        self.dcto = dcto
        self.precioVenta = precioVenta
        self.precioCompra = precioCompra
        self.imagen = imagen
        self.disponible = disponible
        self.constante = constante
        self.id_tipo_plato = id_tipo_plato

    def __repr__(self):
        return f"<Plato {self.nombre}>"

# Tabla para estados de pedidos
class StatusPedido(db.Model):
    __tablename__ = 'status_pedido'
    
    id_status_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_estado = db.Column(db.String(50), nullable=False)

    pedidos = db.relationship('Pedido', back_populates='status_pedido', lazy=True)

    def __repr__(self):
        return f"<StatusPedido {self.nombre_estado}>"

# Modificación de la tabla Pedido para agregar la relación con StatusPedido y CanalDistribucion
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'))
    fecha_pedido = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    total = db.Column(db.Float)

    id_status_pedido = db.Column(db.Integer, db.ForeignKey('status_pedido.id_status_pedido'), nullable=False)
    id_canal_distribucion = db.Column(db.Integer, db.ForeignKey('canales_distribucion.id_canal_distribucion'), nullable=False)

    # Relación con los detalles del pedido
    detalles = db.relationship('DetallePedido', back_populates='pedido', lazy=True, cascade='all, delete-orphan')

    # Relaciones con el estado de pedido y canal de distribución
    canal_distribucion = db.relationship('CanalDistribucion', back_populates='pedidos', lazy=True)
    status_pedido = db.relationship('StatusPedido', back_populates='pedidos', lazy=True)    

    def __repr__(self):
        return f"<Pedido id_pedido={self.id_pedido}, estado={self.status_pedido.nombre_estado}, canal={self.canal_distribucion.nombre_canal}>"
   



class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedidos'

    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)

    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('plato.id_plato'), nullable=False)

    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    pedido = db.relationship('Pedido', back_populates='detalles', lazy=True)
    plato = db.relationship('Plato', back_populates='detalle_pedidos', lazy=True)

    def __repr__(self):
        return f"<DetallePedido id_detalle={self.id_detalle}, id_pedido={self.id_pedido}, id_producto={self.id_producto}>"

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccionEnvio = db.Column(db.String(255), nullable=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfiles.id_perfil'), nullable=False)
    
    perfil = db.relationship('Perfil', back_populates='clientes', lazy=True)

    def __repr__(self):
        return f"<Cliente id_cliente={self.id_cliente}, nombre={self.nombre}, correo={self.correo}>"

class Perfil(db.Model):
    __tablename__ = 'perfiles'
    
    id_perfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_perfil = db.Column(db.String(50), nullable=False)
    
    clientes = db.relationship('Cliente', back_populates='perfil', lazy=True)
    
    def __repr__(self):
        return f"<Perfil id_perfil={self.id_perfil}, nombre_perfil={self.nombre_perfil}>"
