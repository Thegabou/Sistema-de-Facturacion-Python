import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import random
import string

# Obtener los estilos de muestra de ReportLab
styles = getSampleStyleSheet()


class MailManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    @staticmethod
    def get_instance(smtp_server, smtp_port, username, password):
        if not MailManager._instance:
            MailManager._instance = MailManager(smtp_server, smtp_port, username, password)
        return MailManager._instance

    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_mail(self, sender, recipient, subject, message, attachment):
        # Crear el objeto del correo electrónico
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        # Agregar el contenido del correo
        body = message
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo PDF
        pdf_attachment = MIMEApplication(open(attachment, 'rb').read())
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=attachment)
        msg.attach(pdf_attachment)

        # Crear la conexión segura con el servidor SMTP
        context = smtplib.SMTP(self.smtp_server, self.smtp_port)
        context.starttls()
        context.login(self.username, self.password)

        # Enviar el correo electrónico
        context.sendmail(sender, recipient, msg.as_string())

        # Cerrar la conexión con el servidor SMTP
        context.quit()

class Cliente:
    def __init__(self, nombre='', direccion='', ruc='', correo_electronico=''):
        self.nombre = nombre
        self.direccion = direccion
        self.ruc = ruc
        self.correo_electronico = correo_electronico

class Producto:
    def __init__(self, codigo, nombre, cantidad, precio_unitario):
        self.codigo = codigo
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

class Venta:
    def __init__(self, cliente=None, productos=None):
        self.cliente = cliente
        self.productos = productos
        self.fecha_venta = datetime.now()

    def subtotal(self):
        subtotal = 0
        for producto in self.productos:
            subtotal += producto.precio_unitario * producto.cantidad
        return subtotal

    def total(self):
        total = 0
        for producto in self.productos:
            total += producto.precio_unitario * producto.cantidad
        return total
    
    def generar_identificador(self, ref_ventas):
        nombre_cliente = self.cliente.nombre.replace(" ", "").lower()
        ruc_cliente = self.cliente.ruc.replace("-", "")
        caracteres_aleatorios = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        identificador = f"{nombre_cliente}_{ruc_cliente}_{caracteres_aleatorios}"

        # Verificar si el identificador ya existe en la base de datos
        while ref_ventas.child(identificador).get() is not None:
            caracteres_aleatorios = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            identificador = f"{nombre_cliente}_{ruc_cliente}_{caracteres_aleatorios}"

        return identificador

def generar_factura(venta, mail_manager, firebase_manager):
    identificador = firebase_manager.generar_identificador_unico(venta)+".pdf"
    # Crear un objeto PDF
    doc = SimpleDocTemplate(identificador, pagesize=letter)

    # Crear la tabla de productos
    data = [['Código', 'Nombre', 'Cantidad', 'Precio Unitario']]
    for producto in venta.productos:
        data.append([producto.codigo, producto.nombre, producto.cantidad, producto.precio_unitario])

    # Establecer el estilo de la tabla
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
    ])

    # Crear la tabla y aplicar el estilo
    table = Table(data)
    table.setStyle(table_style)

    # Crear la lista de elementos para el PDF
    elements = []

    # Agregar los datos del cliente
    elements.append(Paragraph(f"<b>Nombre:</b> {venta.cliente.nombre}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Dirección:</b> {venta.cliente.direccion}", styles["Normal"]))
    elements.append(Paragraph(f"<b>RUC:</b> {venta.cliente.ruc}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Correo Electrónico:</b> {venta.cliente.correo_electronico}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha de Venta:</b> {venta.fecha_venta.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 12))  # Espacio en blanco

    # Agregar la tabla de productos
    data = [['Código', 'Nombre', 'Cantidad', 'Precio Unitario']]
    for producto in venta.productos:
        data.append([producto.codigo, producto.nombre, producto.cantidad, producto.precio_unitario])

    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 12))  # Espacio en blanco

    # Agregar subtotal y total
    elements.append(Paragraph(f"<b>Subtotal:</b> {venta.subtotal()}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Total:</b> {venta.total()}", styles["Normal"]))


    # Guardar el archivo PDF
    doc.build(elements)

    # Enviar el correo electrónico con el archivo PDF adjunto
    mensaje = '''
    Estimado cliente,

    ¡Gracias por elegir nuestros productos! Adjuntamos la factura de venta correspondiente a su reciente compra. Si tiene alguna pregunta o necesita asistencia adicional, no dude en ponerse en contacto con nuestro equipo de atención al cliente.
    Esperamos que disfrute de sus nuevos productos y que vuelva a contar con nosotros en futuras compras.
    Atentamente, Quickfuck INDUSTRIES.
    '''
    mail_manager.send_mail('gabocastro2003@gmail.com', venta.cliente.correo_electronico, 'Factura',mensaje, identificador)
