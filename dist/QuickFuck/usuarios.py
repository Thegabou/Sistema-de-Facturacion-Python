class usuario():
    def __init__(self,nombre,contrseña):
        self.nombre=nombre
        self.contraseña=contrseña
        self.intentos=3
        self.conectado=False
    
    def ingresar(self, contraseña=None):
        if contraseña==None:
            contra=input("Ingrese su Contraseña: ")
        else:
            contra=contraseña
        if contra==self.contraseña:
            print("Password ingresado con exito!!")
            self.conectado=True
            return True
        else:
            self.intentos-=1
            if self.intentos>0:
                print("Contraseña incorrecta\nPorfavor verifique los datos ingresados!")
                if contraseña!=None:
                    return False
                self.ingresar()
            else:
                print("No se pudo iniciar sesion!\nAdios....")
   
    def offline(self):
        if self.conectado:
            print("Se cerro la sesion con exito!!")
            self.conectado=False
        else:
            print("Error... No se a iniciado sesion aun")
