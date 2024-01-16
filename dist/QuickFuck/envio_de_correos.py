from FirebaseManager import FirebaseManager
from mail_factous import MailManager, Cliente, Producto, Venta, generar_factura
class email_send():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    firebase_manager = FirebaseManager.get_instance("quickfuck-credentials.json", "https://quickfuck-bd-default-rtdb.firebaseio.com/")

    venta = Venta(cliente, productos)

    # Configuración para el servidor SMTP de Outlook
    outlook_manager = MailManager('smtp.office365.com', 587, 'gabocastro2003@gmail.com', 'Gabriel159753!')

    # Generar la factura y enviarla por correo
    generar_factura(venta, outlook_manager, firebase_manager)

    # Registrar la venta en la base de datos
    firebase_manager.registrar_venta(venta)

