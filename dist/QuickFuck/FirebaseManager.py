import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random
import string

class FirebaseManager:
    current_user=''
    _instance = None

    @staticmethod
    def get_instance(credentials_path, database_url):
        if not FirebaseManager._instance:
            FirebaseManager(credentials_path, database_url)
        return FirebaseManager._instance

    def __init__(self, credentials_path, database_url):
        if FirebaseManager._instance:
            raise Exception("FirebaseManager ya ha sido inicializado")

        self.credentials_path = credentials_path
        self.database_url = database_url
        self.initialize_app()
        FirebaseManager._instance = self

    def initialize_app(self):
        cred = credentials.Certificate(self.credentials_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': self.database_url
        })

    def generar_identificador_unico(self, venta):
        nombre_cliente = venta.cliente.nombre.replace(" ", "").lower()
        ruc_cliente = venta.cliente.ruc.replace("-", "")
        caracteres_aleatorios = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        identificador = f"{nombre_cliente}_{ruc_cliente}_{caracteres_aleatorios}"

        ref_ventas = db.reference('ventas')
        while ref_ventas.child(identificador).get() is not None:
            caracteres_aleatorios = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            identificador = f"{nombre_cliente}_{ruc_cliente}_{caracteres_aleatorios}"

        return identificador

    def registrar_venta(self, venta):
        ref_ventas = db.reference('ventas')
        identificador = self.generar_identificador_unico(venta)

        venta_data = {
            'cliente': {
                'nombre': venta.cliente.nombre,
                'direccion': venta.cliente.direccion,
                'ruc': venta.cliente.ruc,
                'correo_electronico': venta.cliente.correo_electronico
            },
            'productos': [{
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'cantidad': producto.cantidad,
                'precio_unitario': producto.precio_unitario,
            } for producto in venta.productos],
            'subtotal': venta.subtotal(),
            'total': venta.total(),
            'fecha_venta': venta.fecha_venta.strftime('%Y-%m-%d %H:%M:%S')
        }

        ref_ventas.child(identificador).set(venta_data)
        print("Venta registrada exitosamente en la base de datos.")
    
    def guardar_usuario(self, usuario):
        ref = db.reference('users')
        user_ref = ref.child(usuario.username)
        user_ref.set({
            'Password': usuario.password
        })
        print("Usuario registrado exitosamente en la base de datos.")
    
    def registrar_producto(self, codigo, producto_data):
        ref_productos = db.reference('productos')
        ref_producto = ref_productos.child(codigo)
        ref_producto.set(producto_data)
        print(f"Producto con código {codigo} registrado exitosamente en la base de datos.")

        ref_producto.set(producto_data)
        print("Producto registrado exitosamente en la base de datos.")

    def obtener_inventario(self):
        ref_productos = db.reference('productos')
        inventario = []
        productos_data = ref_productos.get()
        if productos_data is not None:
            for producto_id, producto_data in productos_data.items():
                inventario.append({
                    'codigo': producto_id,
                    'nombre': producto_data['nombre'],
                    'precio': producto_data['precio'],
                    'cantidad': producto_data['cantidad']
                })
        return inventario

    def cambiar_cantidad_producto_db(self, producto_data):
        ref_productos = db.reference('productos')
        codigo_producto = producto_data['codigo']
        ref_producto = ref_productos.child(codigo_producto)
        ref_cantidad=ref_producto.child('cantidad')
        ref_cantidad.set(producto_data['cantidad'])
        print(f"Producto con código {codigo_producto} registrado exitosamente en la base de datos.")


    def agregar_cliente_firebase(self, cliente_data):
        if not isinstance(cliente_data, dict):
            raise ValueError("El argumento debe ser un diccionario")

        if 'nombre' not in cliente_data or 'direccion' not in cliente_data or 'ruc' not in cliente_data or 'correo_electronico' not in cliente_data:
            raise ValueError("El diccionario debe contener las claves 'nombre', 'direccion', 'ruc' y 'correo_electronico'")

        ref_clientes = db.reference('clientes')
        cliente_ref = ref_clientes.child(cliente_data['ruc'])
        cliente_ref.set({
            'Nombre': cliente_data['nombre'],
            'Direccion': cliente_data['direccion'],
            'RUC': cliente_data['ruc'],
            'Correo_Electronico': cliente_data['correo_electronico']
        })
        print("Cliente registrado exitosamente en la base de datos.")

    def obtener_cliente_por_ruc(self, ruc_cliente):
        ref_clientes = db.reference('clientes')
        cliente_data = ref_clientes.child(ruc_cliente).get()

        if cliente_data:
            return cliente_data
        else:
            print(f"No se encontró ningún cliente con el RUC: {ruc_cliente}")
            return None