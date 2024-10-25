import uuid
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_marshmallow import Marshmallow
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
#-----------------------|----------------------------------------------------------------

load_dotenv()
app = Flask(__name__)

# Configuración de la URI de la base de datos

db_uri = os.getenv('DB_URI')

if not db_uri:
    raise ValueError("La variable de entorno DB_URI no está configurada")

# Inicializar SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Modelo User
class Users(db.Model):
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(255))
    apellidos = db.Column(db.String(255))
    correo = db.Column(db.String(255))
    password = db.Column(db.String(255))
    preferencias = db.Column(db.String(255))
    edad = db.Column(db.Integer, db.CheckConstraint('edad >= 0 AND edad <= 120'))

# Modelo Compra
class Compra(db.Model):
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha_compra = db.Column(db.Time)
    total_compra = db.Column(db.Float(precision=2))
    presup_compra = db.Column(db.Float(precision=2))



# Modelo Producto
class Producto(db.Model):
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255))
    marca = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    qtyunit = db.Column(db.String(255))
    tipUnit = db.Column(db.Integer)
    enlace_nube = db.Column(db.String(255))
    enlace_imagen = db.Column(db.String(255))

# Modelo Tienda
class Tienda(db.Model):
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255))
    direccion = db.Column(db.String(255))
    cadena = db.Column(db.String(255))

# Relaciones Producto_Comestible
class Producto_Comestible(db.Model):
    Productoid = db.Column(db.String(255), db.ForeignKey('producto.id'), primary_key=True)
    valorEnergetico = db.Column(db.String(255))
    grasasSaturadas = db.Column(db.String(255))
    proteina = db.Column(db.String(255))
    sal = db.Column(db.String(255))
    almidon = db.Column(db.String(255))
    vitaminas = db.Column(db.String(255))
    minerales = db.Column(db.String(255))
    preferencias = db.Column(db.String(255))

# Producto_Tienda
class Producto_Tienda(db.Model):
    Productoid = db.Column(db.String(255), db.ForeignKey('producto.id'), primary_key=True)
    Tiendaid = db.Column(db.String(255), db.ForeignKey('tienda.id'), primary_key=True)
    precio = db.Column(db.Float(precision=2))
# Producto_Compra
class Producto_Compra(db.Model):
    Productoid = db.Column(db.String(255), db.ForeignKey('producto.id'), primary_key=True)
    Compraid = db.Column(db.String(255), db.ForeignKey('compra.id'), primary_key=True)

#User_Compra
class User_Compra(db.Model):
    Userid = db.Column(db.String(255), db.ForeignKey('user.id'), primary_key=True)
    Compraid = db.Column(db.String(255), db.ForeignKey('compra.id'), primary_key=True)

# Esquema User
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Users

    id = ma.auto_field()
    username = ma.auto_field()
    nombre = ma.auto_field()
    apellidos = ma.auto_field()
    correo = ma.auto_field()
    password = ma.auto_field()
    preferencias = ma.auto_field()
    edad = ma.auto_field()

# Esquema Compra
class CompraSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Compra

    id = ma.auto_field()
    fecha_compra = ma.auto_field()
    total_compra = ma.auto_field()
    presup_compra = ma.auto_field()

# Esquema Producto
class ProductoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Producto

    id = ma.auto_field()
    nombre = ma.auto_field()
    marca = ma.auto_field()
    tipo = ma.auto_field()
    qtyunit = ma.auto_field()
    tipUnit = ma.auto_field()
    enlace_nube = ma.auto_field()
    enlace_imagen = ma.auto_field()

# Esquema Tienda
class TiendaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tienda

    id = ma.auto_field()
    nombre = ma.auto_field()
    direccion = ma.auto_field()
    cadena = ma.auto_field()


# Instancia del esquema para validar los datos de entrada
user_schema = UserSchema()
@app.route('/users', methods=['POST'])
def create_user():
    # Obtener y validar los datos JSON de la petición
    try:
        data = request.get_json()
        # Validar datos con el esquema de Marshmallow
        user_data = user_schema.load(data)
        # Crear un nuevo usuario
        nuevo_usuario = Users(
            username=user_data['username'],
            nombre=user_data.get('nombre'),
            apellidos=user_data.get('apellidos'),
            correo=user_data.get('correo'),
            password=generate_password_hash(user_data['password']),  # Hash de la contraseña
            preferencias=user_data.get('preferencias'),
            edad=user_data.get('edad')
        )
        # Guardar en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()
        # Serializar la respuesta con Marshmallow
        result = user_schema.dump(nuevo_usuario)
        return jsonify({"message": "Usuario creado con éxito", "status": "success", "user": result}), 201
    except ValidationError as err:
        return jsonify({"message": "Error de validación", "errors": err.messages, "status": "error"}), 400
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

# Ruta para el login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')

    # Verificar que el username y password estén presentes
    if not username or not password:
        return jsonify({"message": "Faltan datos requeridos", "status": "error"}), 400

    # Buscar al usuario por username
    user = Users.query.filter_by(username=username).first()

    # Verificar si el usuario existe
    if not user:
        return jsonify({"message": "Usuario no encontrado", "status": "error"}), 404

    # Verificar la contraseña
    if check_password_hash(user.password, password):
        # Aquí podrías generar un token de autenticación si es necesario
        return jsonify({"message": "Inicio de sesión exitoso", "status": "success", "user": {
            "id": user.id,
            "username": user.username,
            "nombre": user.nombre,
            "apellidos": user.apellidos,
            "correo": user.correo
        }}), 200
    else:
        return jsonify({"message": "Contraseña incorrecta", "status": "error"}), 401


#-------------------------------------------------------------------   
# Esquema Producto para serializar los datos
producto_schema = ProductoSchema()
@app.route('/producto/<string:product_id>', methods=['GET'])
def obtener_producto_por_id(product_id):
    try:
        # hola amigos aqui buscamos el id del producto
        producto = Producto.query.filter_by(id=product_id).first()
        if not producto:
            return jsonify({"message": "Producto no encontrado", "status": "error"}), 404
        result = producto_schema.dump(producto)
        return jsonify({"message": "Producto encontrado", "status": "success", "producto": result}), 200
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500      
#-------------------------------------------------------------------   
@app.route('/')
def index():
    return "hola"

@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        # Probar la conexión usando text()
        result = db.session.execute(text("SELECT 1")).fetchall()
        
        # Convertir el resultado a una lista de diccionarios
        result_list = [dict(row._mapping) for row in result]  # Acceder a los valores usando _mapping

        return jsonify({"message": "Conexión exitosa", "result": result_list})
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"})



if __name__ == '__main__':
    app.run(debug=True)
