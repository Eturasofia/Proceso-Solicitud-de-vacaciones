# Chat bot que gestiona el proceso de 'Gestion de vacaciones'

#Definir funciones para el uso de la base de datos

#Primera funcion: confirmar que el legajo exista
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import csv
from datetime import datetime

def confirmar_legajo(legajo):
    with open ("colaboradores.csv", "r") as archivo:
        lector_de_archivo = csv.reader(archivo, delimiter=";")
        next(lector_de_archivo)
        for fila in lector_de_archivo:
            if fila[0].strip() == legajo.strip():
                return fila
    print("Vaqui: Legajo no encontrado, ingrese nuevamente.")
    return None

#Funcion para calcular la cantidad de dias que desea tomarse

def calcular_dias(fecha_inicio, fecha_fin):
    try:
        inicio = datetime.strptime(fecha_inicio.strip(), "%d/%m/%Y")
        fin = datetime.strptime(fecha_fin.strip(),"%d/%m/%Y")
        cantidad = fin - inicio 
        return cantidad.days + 1
    except ValueError as e:
        return None

#funcion para verificar que no se cruce con un colaborador de otra area

def chequear_area(area, fecha_inicio, fecha_fin):
    with open ("ausencias.csv" , "r") as archivo:
        leer = csv.reader(archivo, delimiter=";")
        next(leer)
        for fila in leer:
            if len(fila) > 2 and fila[2]:
                  if fila[2] == area:
                    ausencia_inicio = datetime.strptime(fila[3], "%Y-%m-%d")
                    ausencia_fin = datetime.strptime(fila[4], "%Y-%m-%d")
                    inicio = datetime.strptime(fecha_inicio,"%d/%m/%Y")
                    fin = datetime.strptime(fecha_fin, "%d/%m/%Y")
                    if inicio <= ausencia_fin and fin >= ausencia_inicio:
                       return True
    return False

#Funcion para guardar el estado de la solicitud.

def registrar_solicitud(legajo, nombre, fecha_inicio, fecha_fin, dias, estado):
    with open("solicitudes.csv", "a") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow([legajo, nombre, fecha_inicio, fecha_fin, dias, estado])


#Codigo principal. 
#Iniciamos con la variable que guarda el estado del proceso
estado = "INICIO"

while True:
    #Inicio de chat, saludo y primera indicacion
    mensaje_usuario = input("")
    if mensaje_usuario.strip() == "": #Aseguramos no permtiir espacios en blanco 
        print("Vaqui: No ingresaste nada, por favor intentá de nuevo.")
        continue
    if estado == "INICIO":
        print("Bienvenido al sistema de vacaciones, mi nombre es Vaqui y te acompañare en todo el proceso")
        print("Ingrese su legajo:")
        estado = "ESPERANDO LEGAJO"
    
    elif estado == "ESPERANDO LEGAJO":
        legajo = mensaje_usuario
        colaborador = confirmar_legajo(legajo) #verificamos el legajo
        if colaborador is not None: #
            print(f"Vaqui: Hola {colaborador[1]}, Tenes {colaborador[3]} dias disponibles")
            print("Vaqui: En que fecha desea iniciar sus vacaciones: (el formato valido es dd/mm/aaaa)")
            estado = "ESPERANDO FECHA DE INICIO"
    #Guardamos fecha de inicio y corrobora que sea en formato correcto.
    elif estado == "ESPERANDO FECHA DE INICIO":
        fecha_inicio = mensaje_usuario
        try:
            datetime.strptime(fecha_inicio, "%d/%m/%Y")
            print("Vaqui: Ahora ingresa la fecha de finalizacion:")
            estado = "ESPERANDO FECHA DE FIN" 
        except ValueError:
            print("Vaqui: Formato incorrecto, ingresa la fecha así: DD/MM/AAAA")
            estado = "ESPERANDO FECHA DE INICIO"
    #Guardamos fecha de fin y calculamos la cantidad de dia que desea tomar
    elif estado == "ESPERANDO FECHA DE FIN":
        fecha_fin = mensaje_usuario
        dias = calcular_dias(fecha_inicio, fecha_fin)
        if dias is None:
            print("Vaqui: Formato de fecha incorrecto, ingresa la fecha de fin nuevamente:")
            estado = "ESPERANDO FECHA DE FIN"
        elif dias <= 0:
            print("Vaqui: Ingrese una fecha posterior a la fecha de inicio.")
            estado = "ESPERANDO FECHA DE FIN"
         #Verificamos si tiene saldo suficiente   
        elif dias > int(colaborador[3]):
            print("Vaqui: No tenés saldo suficiente. Solicitud rechazada.") 
            estado = "FIN"
            break
        elif dias > 15:
            print("Vaqui: Tu solicitud supera los 15 días, se deriva a Gerencia.")
            registrar_solicitud(colaborador[0], colaborador[1], fecha_inicio, fecha_fin, dias, "Pendiente") #Deja en pendiente si la solicitud supera los 15 dias
            estado = "FIN"
            break
        else:
            if chequear_area(colaborador[2], fecha_inicio, fecha_fin): #Verifica si alguien de su area ya esta de vacaciones para no supoerponer
                print("Vaqui: Hay un compañero de tu área de licencia, se deriva a Gerencia.") 
                registrar_solicitud(colaborador[0], colaborador[1], fecha_inicio, fecha_fin, dias, "Pendiente")
                estado = "FIN"
                break
            else:
                print("Vaqui: Tu solicitud fue aprobada automaticamente!")
                registrar_solicitud(colaborador[0], colaborador[1], fecha_inicio, fecha_fin, dias, "Aprobada")
                with open("ausencias.csv", "a") as archivo: #guarda las vacaciones aprobadas.
                    escritor = csv.writer(archivo, delimiter=";")
                    inicio_csv = datetime.strptime(fecha_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
                    fin_csv = datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")
                    escritor.writerow([colaborador[0], colaborador[1], colaborador[2], inicio_csv, fin_csv])
                estado = "FIN"
    elif estado == "FIN": #bloque que cierra el chat.
          print("Vaqui: Gracias por usar el sistema de vacaciones. ¡Hasta la próxima!")
          break

