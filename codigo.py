import tkinter as tk
from random import randint


#Observador del cambio de estado de las casillas
class Observador:
    def __init__(self, casilla, ventana, meta):
        self.casilla = casilla         #Casilla a analizar junto con su estado
        self.ventana = ventana
        self.dimensionesOriginales = None
        self.meta = meta


    def actualizar(self, contador):
        if self.casilla.mina:
            self.notificarPerder()   #Si el estado "mina" de la casilla es True, se notifica que el jugador perdió
        elif contador == self.meta:
            self.notificarGanar()    #Si se llegó a la meta de casillas descubiertas se notifica que el jugador ganó


    #Muestra en pantalla que el jugador ganó
    def notificarPerder(self):
        if self.dimensionesOriginales is None:
            self.dimensionesOriginales = (self.ventana.winfo_width(), self.ventana.winfo_height())
        for widget in self.ventana.winfo_children():
            widget.destroy()

        self.ventana.geometry(f"{self.dimensionesOriginales[0]}x{self.dimensionesOriginales[1]}")
        contenedor = tk.Frame(self.ventana)
        contenedor.pack(expand=True)
        #Mensaje a mostrar
        mensajePerdida = tk.Label(contenedor, text="¡Perdiste! Has pisado una mina", font=("Helvetica", 16))
        mensajePerdida.pack(pady=10)
        #Boton para cerrar la ventana por completo y terminar con el juego
        botonCerrar = tk.Button(contenedor, text="Cerrar", command=self.cerrarVentana)
        botonCerrar.pack(pady=10)

    #Muestra en pantalla que el jugador perdió
    def notificarGanar(self):
        if self.dimensionesOriginales is None:
            self.dimensionesOriginales = (self.ventana.winfo_width(), self.ventana.winfo_height())
        for widget in self.ventana.winfo_children():
            widget.destroy()
        self.ventana.geometry(f"{self.dimensionesOriginales[0]}x{self.dimensionesOriginales[1]}")
        contenedor = tk.Frame(self.ventana)
        contenedor.pack(expand=True)
        mensajeGanar = tk.Label(contenedor, text="¡Ganaste!", font=("Helvetica", 16))
        mensajeGanar.pack(pady=10)
        botonCerrar = tk.Button(contenedor, text="Cerrar", command=self.cerrarVentana)
        botonCerrar.pack(pady=10)

    #Destruir la ventana por completo
    def cerrarVentana(self):
        self.ventana.destroy()

#Represemtacion de cada casilla, ya sea mina o no
class Casilla:
    def __init__(self, observador=None, mina=False):
        self.mina = mina          #Booleano que indica si la casilla es mina o no --> True: Es mina, False: No lo es
        self.cantidad = None      #Entero que representa la cantidad de minas adyacentes a la casilla
        self.presionada = False   #Booleano que indica si la casilla ha sido presionada --> True : Presionada , False : NO presionada
        self.observadores = []    #Lista de observadores de la casilla y sus estados
        self.contador = 0         #Contador que representa el numero de casilla presionada, es decir, si se presionaron 8 antes y despues esta, toma el valor de 9

        if observador:
            self.registrarObservador(observador)

    #Agregar un observador a la casilla
    def registrarObservador(self, observador):
        self.observadores.append(observador)

    #Notificar el cambio de un estado a todos los observadores de la casilla
    def notificarObservadores(self):
        for observador in self.observadores:
            observador.actualizar(self.contador)

    #Cambiar la cantidad de minas adyacentes
    def setCantidad(self, cantidad):
        if not self.mina:
            self.cantidad = cantidad
        else:
            print("No se puede establecer la cantidad en una casilla con mina.")

    #Camabiar estado de "No presionada" a "Presionada"
    def setEstado(self):
        self.presionada = True
        self.notificarObservadores() #Implementacion de patron de diseño observer

    #Cambiar el numero de mina presionada
    def setContador(self, contador):
        self.contador = contador
        self.notificarObservadores() #Implementacion de patron de diseño observer


#Interfaz grafica para desplegear el tablero de juego y poder interactuar con el usuario
class InterfazGrafica:

    #Implementacion del patron de diseño Singleton

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, tablero, ventana):
        if not hasattr(self, 'initialized'):
            self.tablero = tablero             #Tablero que guarda las casillas y sus atributos
            self.ventana = ventana             #Ventana principal en la que se despliega el contenido
            self.ventana.title("Buscaminas")
            self.primerClick = False           #Da a conocer si se ha dado o no el primer click por parte del usuario
            self.botonesTablero = []           #Lista con los botones del tablero
            self.observadores = []             #Lista en que se almacenan todos los observadores de cada casilla
            self.contadorGanar = 0             #Contador que permite saber cuantas casillas han sido descubiertas para poder ganar
            self.meta = tablero.filas * tablero.columnas - tablero.cantidadMinas   #Cantidad de casillas a descubrir para ganar
            self.inicializarInterfaz()
            self.initialized = True

    
    #Permite dar inicio a la interfaz y agregar los observadores a cada casilla
    def inicializarInterfaz(self):
        for fila in range(self.tablero.filas):
            filaBotones = []
            for columna in range(self.tablero.columnas):

                #Permite añadir un observador a cada casilla del tablero
                casilla = self.tablero.matrizTablero[fila][columna]
                observador = Observador(casilla, self.ventana, self.meta)  
                self.observadores.append(observador)  
                casilla.registrarObservador(observador)

                boton = tk.Button(self.ventana, text="", width=5, height=2)

                #Click izquierdo --> muestra el contenido de la casilla con el metodo mostrarContenido
                boton.bind("<Button-1>", lambda event, f=fila, c=columna: self.mostrarContenido(f, c))

                #Click derecho --> pone bandera sobre la casilla con la funciones ponerBandera
                boton.bind("<Button-3>", lambda event, f=fila, c=columna: self.ponerBandera(f, c))

                boton.grid(row=fila, column=columna)
                filaBotones.append(boton)

            self.botonesTablero.append(filaBotones)

    #Pone el mensaje de mina cuando se da clik derecho
    def ponerBandera(self, fila, columna):
        self.botonesTablero[fila][columna].config(text="Mina")

    #Muestra el contenido de la Casilla cuando se da click izquierdo
    def mostrarContenido(self, fila, columna):
        casilla = self.tablero.matrizTablero[fila][columna]

        #Si la Casilla aun no ha sido presionada se pone como presionada y se aumenta 1 al contador
        #que se analiza en caso de ganar
        if not self.tablero.matrizTablero[fila][columna].presionada:
            self.tablero.matrizTablero[fila][columna].setEstado()
            if not casilla.mina:
                self.contadorGanar = self.contadorGanar + 1
                self.cambiarColorCasilla(fila, columna)

        #Se descubre la "Casilla" con su cantidad de minas alrededor
        if not casilla.mina and casilla.cantidad != 0:
            textoMostrar = f"{casilla.cantidad}"
            self.botonesTablero[fila][columna].config(text=textoMostrar)

            #En caso de ser el primer click se muestran todas las casillas vacias y se muestra el contenido de las adyacentes
            #Una vez que ya se dio click esto no volverá a suceder
            if not self.primerClick:
                self.primerClick = True
                self.mostrarVacias()
                self.mostrarContenidoCasillasAdyacentes(fila, columna)
            self.cambiarColorCasilla(fila, columna)

        self.tablero.matrizTablero[fila][columna].setContador(self.contadorGanar)

    #Permite mostrar el contenido de las casillas vacias, es decir, las que no poseen ninguna mina adyacente
    def mostrarVacias(self):
        for fila in range(self.tablero.filas):
            for columna in range(self.tablero.columnas):
                casilla = self.tablero.matrizTablero[fila][columna]
                if casilla.cantidad == 0 and not casilla.mina and not casilla.presionada:
                    self.cambiarColorCasilla(fila, columna)                   #Muestra el contenido en pantalla
                    self.tablero.matrizTablero[fila][columna].setEstado()     #Cambia el estado de la casilla a presionada
                    self.contadorGanar = self.contadorGanar + 1

    #Muestra el contenido de las casillas adyacentes a una casilla presionada
    def mostrarContenidoCasillasAdyacentes(self, fila, columna):
        for i in range(max(0, fila - 1), min(self.tablero.filas, fila + 2)):
            for j in range(max(0, columna - 1), min(self.tablero.columnas, columna + 2)):
                # Evita mostrar la casilla actual
                if i != fila or j != columna:
                    casilla = self.tablero.matrizTablero[i][j]
                    if casilla.cantidad != 0 and casilla.cantidad is not None:
                        textoMostrar = f"{casilla.cantidad}"
                        self.botonesTablero[i][j].config(text=textoMostrar)
                        self.cambiarColorCasilla(i, j)
                        self.tablero.matrizTablero[i][j].setEstado()    #Se cambia el estado de las casillas adyacentes a presionadas
                        self.contadorGanar = self.contadorGanar + 1


    #Permite cambiar el color de la casilla para mostrar esta en pantalla
    def cambiarColorCasilla(self, fila, columna):
        casilla = self.tablero.matrizTablero[fila][columna]
        cantidad = casilla.cantidad

        colores = {
            0: '#f9f9b5',
            1: '#b5f9f0',
            2: '#e7c6fe',
            3: '#c9fec6',
            4: '#fec6c6',
            # En un futuro se podrian agregar mas colores
        }

        color = colores.get(cantidad, 'white')

        # Cambiar el color de la casilla al presionarla
        self.botonesTablero[fila][columna].config(bg=color)

    def mostrarTablero(self):
        self.ventana.mainloop()

#Tablero se encuentra por detras de la interfaz grafica, este se compone de casillas
class Tablero:
    def __init__(self, filas, columnas, cantidadMinas):
        self.filas = filas       #Cantidad de filas del tablero
        self.columnas = columnas #Cantidad de columnas del tablero
        self.cantidadMinas = cantidadMinas #Cantidad de minas del tablero
        self.matrizTablero = [[Casilla(observador=None) for _ in range(columnas)] for _ in range(filas)] #Matriz compuesta de objetos "Casilla"
        self.colocarMinas()
        self.colocarCantidades()

    #Permite colocar minas en posiciones aleatorias del tablero con "randint"
    def colocarMinas(self):
        for _ in range(self.cantidadMinas):
            fila = randint(0, self.filas - 1)
            columna = randint(0, self.columnas - 1)

            while self.matrizTablero[fila][columna].mina:
                fila = randint(0, self.filas - 1)
                columna = randint(0, self.columnas - 1)

            self.matrizTablero[fila][columna].mina = True #Una casilla con su atributo "mina" en "True" se reconoce como mina


    #Permite colocar las cantidad de minas adyacentes a cada casilla dentro del tablero, este numero con pone en el atributo "cantidad"
    #de cada objeto "Casilla"
    def colocarCantidades(self):
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if not self.matrizTablero[fila][columna].mina:
                    cantidadAlrededor = self.contarMinasAlrededor(fila, columna)
                    self.matrizTablero[fila][columna].setCantidad(cantidadAlrededor)


    #Permite contar la cantidad de minas adyacentes a cada Casilla para hacer uso de esta informacion posteriormente
    def contarMinasAlrededor(self, fila, columna):
        cantidad = 0
        for i in range(max(0, fila - 1), min(self.filas, fila + 2)):
            for j in range(max(0, columna - 1), min(self.columnas, columna + 2)):
                if self.matrizTablero[i][j].mina:
                    cantidad += 1
        return cantidad


#Menu para seleccionar la dificultad del juego, es decir, el tamaño del tablero
class MenuInicio:

    #Implementación del patron de diseño singleton el cual permite instanciar una clase una sola
    #vez dentro del codigo

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ventana):
        if not hasattr(self, 'initialized'):
            self.ventana = ventana        #Ventana en la que se despliega el mensaje y las opciones en forma de botones
            self.ventana.title("Inicio")
            self.mostrarMensajeInicial()
            self.initialized = True       #Inicializado en True se traduce como que se ha creado una instancia de la clase


    #Permite mostrar mensaje de dificultad y desplegar los botones para seleccionar la dificultad dentro del juego.
    def mostrarMensajeInicial(self):
        mensaje = tk.Label(self.ventana, text="Selecciona la dificultad:")
        mensaje.pack()

        opciones = [5, 10, 15, 20]

        #Despliegue de botones de opciones
        for opcion in opciones:
            boton = tk.Button(self.ventana, text=f"{opcion}x{opcion}", command=lambda o=opcion: self.iniciarJuego(o))
            boton.pack()

    #Inicio de juego y su interfaz grafica, con las opciones seleccionadas en el MenuInicio respecto al tamaño del tablero
    def iniciarJuego(self, dimensiones):
        self.ventana.destroy()
        cantidadMinas = dimensiones
        tablero = Tablero(dimensiones, dimensiones, cantidadMinas) #Creacion del tablero del "nxn" con "n" minas en su interior
        ventanaPrincipal = tk.Tk()
        interfaz = InterfazGrafica(tablero, ventanaPrincipal)
        interfaz.mostrarTablero()


if __name__ == "__main__":
    ventanaSeleccion = tk.Tk()
    seleccion = MenuInicio(ventanaSeleccion)
    ventanaSeleccion.mainloop()
    






