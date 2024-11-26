import uuid
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_marshmallow import Marshmallow
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime
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
    precio = db.Column(db.Float(precision=2))

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
    __tablename__ = 'producto_compra'  # Especifica explícitamente el nombre de la tabla
    Productoid = db.Column(db.String(255), db.ForeignKey('producto.id'), primary_key=True)
    Compraid = db.Column(db.String(255), db.ForeignKey('compra.id'), primary_key=True)

#User_Compra
class users_compra(db.Model):
    __tablename__ = 'users_compra'  # Especifica explícitamente el nombre de la tabla

    Userid = db.Column(db.String(255), db.ForeignKey('users.id'), primary_key=True)  # Asegúrate de que 'users.id' sea correcto
    Compraid = db.Column(db.String(255), db.ForeignKey('compra.id'), primary_key=True)  # Asegúrate de que 'compra.id' sea correcto
    usuario = db.relationship('Users', backref=db.backref('compras', lazy=True))
    compra = db.relationship('Compra', backref=db.backref('usuarios', lazy=True))

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
    precio = ma.auto_field()

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
#-------------------------------------------------------------
@app.route('/historial_compras/<username>', methods=['GET'])
def historial_compras(username):
    try:
        # Ejecutar la consulta SQL para obtener el historial de compras del usuario
        result = db.session.execute(
            text("""
                SELECT c.id AS compra_id, 
                       c.fecha_compra, 
                       c.total_compra, 
                       c.presup_compra
                FROM compra c
                JOIN users_compra uc ON c.id = uc.compraid
                JOIN users u ON u.id = uc.userid
                WHERE u.username = :username;
            """),
            {"username": username}  # Pasar el username como parámetro
        ).fetchall()

        # Verificar si hay resultados
        if not result:
            return jsonify({"message": "No se encontraron compras para este usuario", "status": "error"}), 404

        # Convertir el resultado en una lista de diccionarios
        result_list = []
        for row in result:
            compra_id = row[0]
            fecha_compra = row[1]
            total_compra = row[2]
            presup_compra = row[3]
            
            # Verificar si fecha_compra es un objeto datetime y convertirla a string
            if isinstance(fecha_compra, datetime):
                fecha_compra_str = fecha_compra.strftime('%Y-%m-%d'), #Obtenemos solamente en año, mes, dia
            else:
                # Si no es un datetime (en caso de que sea timedelta o nulo), lo manejamos de forma segura
                fecha_compra_str = str(fecha_compra)

            result_list.append({
                "compra_id": compra_id,
                "fecha_compra": fecha_compra_str,
                "total_compra": total_compra,
                "presup_compra": presup_compra
            })

        # Devolver el historial de compras como respuesta JSON
        return jsonify({
            "message": "Historial de compras obtenido con éxito",
            "status": "success",
            "compras": result_list
        })

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500


@app.route('/confirmar_compra', methods=['POST'])
def confirmar_compra():
    try:
        # Obtener los datos de la compra desde el JSON de la petición
        data = request.get_json()
        
        # Validar la información requerida en la compra
        username = data.get('username')
        productos = data.get('productos')  # Se espera una lista de productos con id y cantidad
        total_compra = data.get('total_compra')
        presup_compra = data.get('presup_compra')
        
        if not username or not productos or not total_compra or not presup_compra:
            return jsonify({"message": "Faltan datos requeridos", "status": "error"}), 400
        
        # Crear la compra
        nueva_compra = Compra(
            fecha_compra=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_compra=total_compra,
            presup_compra=presup_compra
        )
        db.session.add(nueva_compra)
        db.session.commit()
        
        # Asociar la compra con el usuario
        usuario = Users.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({"message": "Usuario no encontrado", "status": "error"}), 404
        
        nueva_compra_usuario = users_compra(
            Userid=usuario.id,
            Compraid=nueva_compra.id
        )
        db.session.add(nueva_compra_usuario)
        
        # Asociar los productos a la compra
        for producto in productos:
            producto_id = producto.get('id')
            cantidad = producto.get('cantidad')
            
            producto_db = Producto.query.filter_by(id=producto_id).first()
            if not producto_db:
                return jsonify({"message": f"Producto con ID {producto_id} no encontrado", "status": "error"}), 404
            
            # Insertar relación Producto_Compra
            nuevo_producto_compra = Producto_Compra(
                Productoid=producto_db.id,
                Compraid=nueva_compra.id
            )
            db.session.add(nuevo_producto_compra)

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Serializar la respuesta
        result = CompraSchema().dump(nueva_compra)
        
        return jsonify({
            "message": "Compra confirmada con éxito",
            "status": "success",
            "compra": result
        }), 201

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
