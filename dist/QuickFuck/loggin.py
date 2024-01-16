from tkinter import Tk, Label, Entry, StringVar, ttk, PhotoImage
from PIL import ImageTk, Image
from tkinter import messagebox as Messagebox
from FirebaseManager import *
from interfaz import SistemApp


class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password

page_log = Tk()
sus=StringVar()
among=StringVar()

def okloggin():
    username = sus.get()
    print(f"Login with username {username}")
    password = among.get()
    print(f"Login with pass {password}")
    ref = db.reference('users')
    users = ref.get()

    if users:
        if username in users:
            stored_password = users[username]['Password']
            if password == stored_password:
                firebase_manager.current_user=username
                Messagebox.showinfo("Conectado", "Sesión iniciada con éxito :D")
                page_log.destroy()
                SistemApp().run()
            else:
                Messagebox.showerror("Error", "Contraseña incorrecta... verificar los datos")
        else:
            Messagebox.showerror("Error", "No existen usuarios registrados con ese nombre")
    else:
        Messagebox.showerror("Error", "No existen usuarios registrados en la base de datos")


   

def registroU():
   name=sus.get()
   passw=among.get()
   newUser=User(name,passw)
   firebase_manager.guardar_usuario(newUser)
   Messagebox.showinfo("Exitoso!", f"El registro de usuario fue exitoso bienvenido {name}")
   name=sus.set("")
   passw=among.set("")

def loggin():
    page_log.title("Gabo's Quickfuck")
    page_log.resizable(False, False)
    page_log.configure(bg="white")
    original_imagen = Image.open("Usuario.jpg")
    nwpoto= original_imagen.resize((700,500))
    poto = ImageTk.PhotoImage(nwpoto)
        
    lb = Label(page_log, image = poto)
    lb.pack()
    lb.place(x=0, y=0)

    tits =Label(page_log, text="Ingrese sus Datos", font=("Helvetica", 15), bg="white")
    tits.place(x=380, y=0)

    lb_usuario=Label(page_log, text="Usuario", font=("Helvetica", 15 ), bg="white")
    lb_usuario.place(x=250, y=220)


    lb_contra=Label(page_log, text="Contraseña", font=("Helvetica", 15), background="white")
    lb_contra.place(x=250, y=300)

    sus.set("")
    entrada_sus=Entry(page_log, textvariable=sus)
    entrada_sus.place(x=250, y=250)

    among.set("")
    entrada_among=Entry(page_log, textvariable=among, show="*")
    entrada_among.place(x=250, y=330)

    but_user=ttk.Button(page_log, text="Iniciar Sesion", command=okloggin)
    but_user.place(x=350, y=400)

    but_reg=ttk.Button(page_log, text="Registrar", command=registroU)
    but_reg.place(x=250,y=400)

    page_log.geometry("700x500")
    page_log.wm_geometry("+400+100")

    page_log.mainloop()


if __name__=="__main__":
    firebase_manager = FirebaseManager.get_instance("quickfuck-credentials.json", "https://quickfuck-bd-default-rtdb.firebaseio.com/")
    loggin()