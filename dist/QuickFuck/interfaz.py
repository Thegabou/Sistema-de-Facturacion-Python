from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from FirebaseManager import *
from datetime import datetime, timedelta
from kivy.clock import Clock
from mail_factous import *

firebase_manager = FirebaseManager.get_instance("quickfuck-credentials.json", "https://quickfuck-bd-default-rtdb.firebaseio.com/")
mail_manager = MailManager.get_instance('smtp.office365.com', 587, 'gabocastro2003@gmail.com', 'Gabriel159753!')
inventario=firebase_manager.obtener_inventario()

current_venta=Venta()
current_products=[]
current_client=Cliente()

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last=BooleanProperty(True)


class SelectableBox(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['num'].text= str(1+index)
        self.ids['nomb'].text= data['nombre'].capitalize()
        self.ids['cantidad'].text= str(data['cantidad'])
        self.ids['p_u'].text= str("{:.2f}".format(data['precio']))
        self.ids['p_t'].text= str("{:.2f}".format(data['precio_total']))
        return super(SelectableBox, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBox, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        print(f'selected index {index}, selected {is_selected}')
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
            rv.current_indexinview=index
        else:
            rv.data[index]['seleccionado']=False
        print(rv.data[index]['seleccionado'])

class SelectableBoxPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    articulo_data = {}

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.articulo_data = data 
        self.ids['codigo_'].text= data['codigo']
        self.ids['articulo_'].text= data['nombre'].capitalize()
        self.ids['cantidad_'].text= str(data['cantidad'])
        self.ids['precio_'].text= str("{:.2f}".format(data['precio']))
        return super(SelectableBoxPopup, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxPopup, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        print(f'popup selected {index} ')
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.change=None
        self.current_indexinview=-1

    def agregar_carrito(self, art):
        art['seleccionado']= False
        indice=-1
        if self.data:
            for g in range(len(self.data)):
                if art['codigo']==self.data[g]['codigo']:
                    indice=g
            if indice >=0:
                self.data[indice]['cantidad']+=1
                self.data[indice]['precio_total']=self.data[indice]['precio']*self.data[indice]['cantidad']
                self.refresh_from_data()
            else:
                self.data.append(art)
        else:
            self.data.append(art)
    
    def elemto_seleccionado(self):
        indice=-1
        print(indice)
        for i in range(len(self.data)):
            if self.data[indice]['seleccionado']:
                indice=i
                break
        print(f'selected index in True: {indice}')
        return indice
    
    def eliminar_art(self):
        indice=self.current_indexinview
        precio=0
        if indice>=0:
            self._layout_manager.deselect_node(self.layout_manager._last_selected_node)
            precio=self.data[indice]['precio_total']
            self.data.pop(indice)
            self.refresh_from_data()
        return precio

    def actualizar_articulo(self, valor):
        indice=self.current_indexinview
        if indice>=0:
            if valor==0:
                self.data.pop(indice)
                self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            else:
                self.data[indice]['cantidad']=valor
                self.data[indice]['precio_total']=self.data[indice]['precio'] * valor
            self.refresh_from_data()
            nuevo_total=0
            for data in self.data:
                nuevo_total+=data['precio_total']
            self.change(False, nuevo_total)


    def modificar_producto(self):
        #indice=self.elemto_seleccionado()
        indice=self.current_indexinview
        if indice>=0:
            pou=Cambiar_cantidad(self.data[indice], self.actualizar_articulo)
            pou.open()

class Cambiar_cantidad(Popup):
    def __init__(self, data,actualizar_articulo_cal,**kwargs):
        super(Cambiar_cantidad,self).__init__(**kwargs)
        self.data=data
        self.actualizar_articulo=actualizar_articulo_cal
        self.ids.new_cant_1.text= 'Productos: '+ self.data['nombre'].capitalize()
        self.ids.new_cant_2.text= 'Camtodad: '+ str(self.data['cantidad'])
    
    def validar_input(self, texto_input):
        try:
            nueva_cantidad=int(texto_input)
            self.ids.no_valido.text=''
            self.actualizar_articulo(nueva_cantidad)
            self.dismiss()
        except:
            self.ids.no_valido.text='Cantidad invalida!'
            

class Nombrepoppup(Popup):
    def __init__(self, nombre, agragar_call, **kwargs):
        super(Nombrepoppup, self).__init__(**kwargs)
        self.nombre=nombre
        self.agregar=agragar_call

    def mostrar_productos(self):
        self.open()
        print(self.nombre)
        for product in inventario:
            if self.nombre.lower() in  product['nombre'].lower():
                print(product)
                self.ids.rvf.agregar_carrito(product)
    
    
    def seleccionar(self):
        indice=self.ids.rvf.elemto_seleccionado()
        if indice>=0:
            articulo_=self.ids.rvf.data[indice]
            articulo={
                'codigo': articulo_['codigo'],
                'nombre': articulo_['nombre'],
                'precio': articulo_['precio'],
                'cantidad': 1,
                'cantidad_inventario': articulo_['cantidad'],
                'precio_total': articulo_['precio']
            }
            if callable(self.agregar):
                self.agregar(articulo)
            self.dismiss()

class Pagarpopup(Popup):
    def __init__(self,total, pagado_cal,**kwargs):
        super(Pagarpopup,self).__init__(**kwargs)
        self.pagado=pagado_cal
        self.total=total
        self.ids.total_lb.text='$ '+'{:.2f}'.format(self.total)
    
    def mostrar_cambio(self):
        recibir=self.ids.recibido_txi.text
        try:
            cambio=float(recibir)-float(self.total)
            if cambio>=0:
                self.ids.cambio_lb.text='$ '+'{:.2f}'.format(cambio)
                self.ids.pagar_bt.disabled= False
            else:
                self.ids.cambio_lb.text="Cambio por debajo de 0!"
        except:
            self.ids.cambio_lb.text="Cambio no valido"


    def terminar_pago(self):
        self.pagado()
        self.dismiss()

    def crear_user(self):
        uta=Crear_user_pop()
        uta.open()

    def cargar_cliente(self):
        ruc_cliente_buscado = self.ids.busacar_ci.text
        cliente_data = firebase_manager.obtener_cliente_por_ruc(ruc_cliente_buscado)
        if not cliente_data==None:
            self.ids.nombre_lb.text= cliente_data['Nombre']
            self.ids.ruc_cliente.text= cliente_data['RUC']
            self.ids.correo_cliente.text= cliente_data['Correo_Electronico']
            self.ids.Direccion_cliente.text=cliente_data['Direccion']
            global current_client
            current_client=Cliente(cliente_data['Nombre'], cliente_data['Direccion'], cliente_data['RUC'], cliente_data['Correo_Electronico'])
        else:
            self.ids.nombre_lb.text= 'No se encontro el cliente en la database!'

    def consumidor_user(self):
        self.ids.nombre_lb.text= 'CONSUMIDOR FINAL'
        self.ids.ruc_cliente.text= '9999999999'
        self.ids.correo_cliente.text= '------------------'
        self.ids.Direccion_cliente.text='------------------'
        global current_client
        current_client=Cliente('CONSUMIDOR FINAL', '9999999999', '------------------', 'nomail')

class Nuevacomprapoup(Popup):
    def __init__(self,nuevacompra_cal,**kwargs):
        super(Nuevacomprapoup, self).__init__(**kwargs)
        self.NewShop=nuevacompra_cal
        self.ids.simon.bind(on_release=self.dismiss)

class InventarioPoup(Popup):
    def __init__(self,**kwargs):
        super(InventarioPoup, self).__init__(**kwargs)
        self.codigo_producto = ''
        self.nombre_producto = ''
        self.precio_producto =  0.0
        self.cantidad_producto = 0


    def registrar_producto_db(self):
        self.codigo_producto=self.ids.codigo_p.text
        self.nombre_producto=self.ids.nombre_p.text
        self.precio_producto=float(self.ids.precio_p.text)
        self.cantidad_producto=int(self.ids.cantidad_p.text)
        producto_data = {
            'nombre': self.nombre_producto,
            'precio': self.precio_producto,
            'cantidad': self.cantidad_producto
        }

        firebase_manager.registrar_producto(self.codigo_producto, producto_data)
        global inventario
        inventario=firebase_manager.obtener_inventario()
        self.dismiss()
        
class Crear_user_pop(Popup):
    def __init__(self, **kwargs):
        super(Crear_user_pop, self).__init__(**kwargs)
        

    def registrar_cliente_db(self):
        nuevo_cliente_data = {
            'nombre': self.ids.nombre_cliente.text,
            'direccion': self.ids.direccion_cliente_tx.text,
            'ruc': self.ids.ruc_cliente.text,
            'correo_electronico': self.ids.correo_cliente.text
        }

        firebase_manager.agregar_cliente_firebase(nuevo_cliente_data)
        self.dismiss()



class VentasWindow(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.total=0.0
        self.ids.rvd.change=self.change
        self.ahora=datetime.now()
        self.ids.fecha.text=self.ahora.strftime('%d/%m/%y')
        Clock.schedule_interval(self.actualizar_hora, 1)
        self.ids.welcom_label.text=f'Bienvenido {firebase_manager.current_user}'
        

        
    def actualizar_hora(self, *args):
        self.ahora=self.ahora+timedelta(seconds=1)
        self.ids.hora.text=self.ahora.strftime('%H:%M:%S')

    def Pay(self):
        if self.ids.rvd.data:
            poup=Pagarpopup(self.total, self.pagado)
            poup.open()
        else:
            self.ids.error.text='No hay productos en el carrito'
        
    def NewShop(self, popupc=False):
        if popupc: 
            self.ids.rvd.data=[]
            self.total=0.0
            self.ids.sub_T.text='0.00'
            self.ids.Totalpro.text='0.00'
            self.ids.error.text=''
            self.ids.exito.text=''
            self.ids.codex.disabled= False
            self.ids.name_p.disabled= False
            self.ids.rvd.refresh_from_data()
        elif len(self.ids.rvd.data):    
            poupp=Nuevacomprapoup(self.NewShop)
            poupp.open()

    def name_prod(self, nombre):
        self.ids.name_p.text=''
        pop=Nombrepoppup(nombre, self.agregar)
        pop.mostrar_productos()

    def codex_prod(self, codigo):
        for producto in inventario:
            if codigo == producto['codigo']:
                articulo = {
                    'codigo': producto['codigo'],
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': 1,
                    'cantidad_inventario': producto['cantidad'],
                    'precio_total': producto['precio'],
                }
                print(articulo)
                self.agregar(articulo)
                self.ids.codex.text=''
                break

    def change(self, cambio=True, nuevo_total=None):
        if cambio:
            self.ids.rvd.modificar_producto()
        else:
            self.total=nuevo_total
            self.ids.sub_T.text='$ ' + "{:.2f}".format(self.total)
    
    def agregar(self, articulo):
        self.total += articulo['precio_total']  # Agregar el precio del nuevo producto al total
        self.ids.sub_T.text = '$ ' + "{:.2f}".format(self.total)
        self.ids.rvd.agregar_carrito(articulo)

    def pagado(self):
        self.ids.exito.text='Pago realizado con exito!'
        self.ids.Totalpro.text='$ '+'{:.2f}'.format(self.total)
        self.ids.codex.disabled= True
        self.ids.name_p.disabled= True
        nueva_cantidad=[]
        for producto in self.ids.rvd.data:
            global current_products
            current_products.append(Producto(producto['codigo'], producto['nombre'], producto['cantidad'], producto['precio']))
            cantidad=producto['cantidad_inventario']-producto['cantidad']
            if cantidad>=0:
                nueva_cantidad.append({'codigo': producto['codigo'],'cantidad': cantidad})
            else:
                nueva_cantidad.append({'codigo': producto['codigo'],'cantidad': 0})
        for cantidad in nueva_cantidad:
            firebase_manager.cambiar_cantidad_producto_db(cantidad)
        global inventario
        inventario = firebase_manager.obtener_inventario()
        self.registrar_venta()

    def registrar_venta(self):
        global current_venta
        current_venta=Venta(current_client,current_products)
        print(current_venta)
        if not current_client.correo_electronico=='nomail':
            generar_factura(current_venta, mail_manager, firebase_manager)

        firebase_manager.registrar_venta(current_venta)


    def deletd(self):
        meno=self.ids.rvd.eliminar_art()
        self.total-=meno
        self.ids.sub_T.text= '$ ' + "{:.2f}".format(self.total)

    def Salir(self):
        self.parent.close()
        
        
    def Inventario(self):
        inventori=InventarioPoup()
        inventori.open()

class SistemApp(App):
    def build(self):
        # Window.resizable=False
        Window.maximize()
        return VentasWindow()

        
# if __name__ == '__main__':
#     SistemApp().run()