import sys
import MySQLdb
from itertools import *
from datetime import datetime, timedelta
import random
from tabulate import tabulate


def consulta_horario_ant(d):
   #print("consultando horario anterior....\n")
   db = conectar_db()
   date = d
   sql = f"SELECT * FROM horario WHERE fecha_horario = '{date}'"
   cursor = db.cursor(MySQLdb.cursors.DictCursor)
   try:
      cursor.execute(sql)
      dic_horario_ant = cursor.fetchall() 
   except:
      print("Error en la consulta")

   db.close()
   
   return dic_horario_ant 

def consulta_disponibilidad(numDia):
   
   db = conectar_db()
   sql = f'SELECT * FROM disponibilidad WHERE (apertura_1 = TRUE OR apertura_2 = 1 OR intermedio_1 = 1 OR intermedio_2 = 1 OR intermedio_3 = 1 or cierre_2 = 1 OR cierre_1 = 1 OR desc_mat = 1 OR desc_ves = 1) AND id_dia = {numDia};'
   cursor = db.cursor(MySQLdb.cursors.DictCursor)
   try:
      cursor.execute(sql)
      disponibilidad = cursor.fetchall() 
   except:
      print("Error en la consulta")

   db.close()
   
   return disponibilidad


def conectar_db():
   
   try:
      db = MySQLdb.connect("localhost","administrador","password","employee_schedule" )
   except MySQLdb.Error as e:
      print("No puedo conectar a la base de datos:",e)
      sys.exit(1)
   
   #print("Conexión correcta a base de datos...")
   return db

def agregar_empleado():
   print("funcion para agregar empleado a bd")

def listar_empleados():
   
   db = conectar_db()

   sql = 'SELECT * FROM empleados;'
   cursor = db.cursor(MySQLdb.cursors.DictCursor)
   try:
      cursor.execute(sql)
      dic_empleados = cursor.fetchall() 
   except:
      print("Error en la consulta")

   db.close()
   
   total_colaboradores = len(dic_empleados)

   contador_ft= 0 
   contador_fm= 0 
   contador_rot= 0 


   for e in dic_empleados:
      if e['tipo_turno'] == 'ft':
         contador_ft += 1
      if e['tipo_turno'] == 'fm':
         contador_fm += 1 
      if e['tipo_turno'] == 'rot':
         contador_rot += 1  
   
   return [dic_empleados, contador_fm, contador_ft, contador_rot, total_colaboradores] 

def definir_turnos(num_empleados, porcentaje_tmatutino, porcentaje_tvespertino):

   listaTurnos = []

   total_colaboradores = num_empleados

   colab_tmatutino = round(total_colaboradores * porcentaje_tmatutino)
   colab_tvespertino = round(total_colaboradores * porcentaje_tvespertino)

   dif = (colab_tmatutino+colab_tvespertino)- total_colaboradores 

   if dif > 0: colab_tvespertino = colab_tvespertino - dif
   if (colab_tmatutino+ colab_tvespertino) != total_colaboradores : print("error al calcular los porcentajes, configure nuevamente")

   descansos_mat = repartir_descansos(colab_tmatutino)
   descansos_ves = repartir_descansos(colab_tvespertino)

   for i in range(1,8):

      apertura_1 = round((colab_tmatutino-descansos_mat.get(i))*0.3)
      apertura_2 = round((colab_tmatutino- descansos_mat.get(i)-apertura_1)*0.5)
      apertura_3 = colab_tmatutino- descansos_mat.get(i)-apertura_1-apertura_2
      intermedio_1 = colab_tmatutino- descansos_mat.get(i)-apertura_1-apertura_2-apertura_3
      
      cierre_2 = round((colab_tvespertino-descansos_ves.get(i))*0.3)
      cierre_1 = round((colab_tvespertino- descansos_ves.get(i)-cierre_2)*0.5)
      intermedio_3 = colab_tvespertino- descansos_ves.get(i)-cierre_2-cierre_1
      intermedio_2 = colab_tvespertino- descansos_ves.get(i)-cierre_2-cierre_1 - intermedio_3

      dict_turnos = {
      "id_dia": i,
      "apertura_1": apertura_1,
      "apertura_2": apertura_2,
      "apertura_3": apertura_3,
      "intermedio_1": intermedio_1,
      "intermedio_2": intermedio_2,
      "intermedio_3": intermedio_3,
      "cierre_1": cierre_1,
      "cierre_2": cierre_2,
      "desc_mat": descansos_mat.get(i),
      "desc_ves": descansos_ves.get(i)}

      listaTurnos.append(dict_turnos)

   return listaTurnos

def repartir_descansos(numero):
   contador = 0
   descansos = {4: 0, 3: 0, 5: 0, 1:0, 2: 0, 6:0, 7:0}  #cada numero significa el dia de la semana p.e. 1 = lunes 
            ## se utiliza la libreria itertools para iterar el diccionario n veces
   for d in cycle(descansos):
      descansos[d] += 1
      contador += 1
  
      if contador == numero: break      
   
   return descansos

def asignar_descansos(dic_empleados):
    """
    Asigna un día de descanso a cada colaborador.
    """
    """ dias_semana = [1, 2, 3, 4, 5, 6, 7]  # Lunes = 1, ..., Domingo = 7
    descansos = {}

    for empleado in dic_empleados:
        descanso = random.choice(dias_semana)
        descansos[empleado['id_empleado']] = descanso

    return descansos  """

def calcular_fecha(dia, mes, ano):

   
   ## establecer fecha del horario a realizar y calcular la fecha del horario anterior
   
   ano = int(ano)
   mes = int(mes)
   dia = int(dia)

   fecha_horario_actual = datetime(ano, mes, dia)
   delta = timedelta(days=7)
   fecha_horario =  fecha_horario_actual- delta
   fecha_horario_anterior = fecha_horario.strftime("%Y-%m-%d")

   print("Fecha horario actual:", fecha_horario_actual.strftime("%Y-%m-%d"))
   print("Fecha horario anterior:", fecha_horario_anterior)

   return fecha_horario_anterior

def asignar_horarios(lista_turnos, disponibilidad, tipo_turno, listaHorarios, dia, lista_turnos_descansos, descansos_por_empleado):
   

   disp_fijo = [d for d in disponibilidad if d.get(tipo_turno) == 2]
   
   disp_rot = [d for d in disponibilidad if d.get(tipo_turno) == 1]

   while(lista_turnos_descansos[tipo_turno]>0):
         
         #print(f"asignando horario para {tipo_turno}...", lista_turnos_descansos[tipo_turno])
         

         if len(disp_fijo)>0: #comprobar si existen elementos en la lista
            seleccion = random.choice(disp_fijo) #escoge un elemento al azar
            idSeleccion  = seleccion.get('id_empleado')
            disp_fijo = [d for d in disp_fijo if d['id_empleado'] != idSeleccion] # Quitar el empleado seleccionado de la lista
         elif len(disp_rot)>0:
            seleccion = random.choice(disp_rot)
            idSeleccion = seleccion.get('id_empleado') 
            disp_rot = [d for d in disp_rot if d['id_empleado'] != idSeleccion] # Quitar el empleado seleccionado de la lista
         else:
            #print("No hay colaboradores disponibles para turno rotativo..")
            break  # Salimos si no hay más colaboradores

         # Si el colaborador ya tiene un descanso asignado, no se le asigna turno para ese día
         if descansos_por_empleado.get(idSeleccion) == dia:
            print(f"Empleado {idSeleccion} tiene descanso en el día {dia}, asignando descanso.")
            # Determinar si es un descanso matutino o vespertino
            id_turno = 'desc_mat' if tipo_turno.startswith('apertura') or tipo_turno.startswith('intermedio_1') else 'desc_ves'

            horario = {
               "id_horario": 0, 
               "id_empleado": idSeleccion,
               "id_dia": dia,
               "id_turno": tipo_turno, #aqui se asigna el descanso, mat o vesp
               "fecha_horario": "2024-01-01"
               }   
            #print(horario)   
            listaHorarios.append(horario)
            
            lista_turnos_descansos[tipo_turno]-=1 
            continue
         
         # Asignar un turno al empleado si no tiene descanso
         horario = {
               "id_horario": 0, 
               "id_empleado": idSeleccion,
               "id_dia": dia,
               "id_turno": tipo_turno,  # Mantener el turno original si no es descanso
               "fecha_horario": "2024-01-01"
         }
         listaHorarios.append(horario)
      
         # Reducir la cantidad de turnos restantes por asignar
         lista_turnos_descansos[tipo_turno] -= 1

         # Si el empleado aún no tiene un descanso asignado, asignárselo aleatoriamente
         if idSeleccion not in descansos_por_empleado:
               descansos_por_empleado[idSeleccion] = random.choice(range(1, 8))  # Asignar un día de descanso aleatorio
               print(f"Asignando descanso al empleado {idSeleccion} para el día {descansos_por_empleado[idSeleccion]}")
         

def generar_horario():

   listaHorarios = [] #En esta lista se guardaran  el horario de cada colaborador 
   valores = listar_empleados() #obtener valores de la funcion 
   dic_empleados, contador_fm, contador_ft, contador_rot, total_colaboradores = valores #desempaquetar variables de la funcion listar_emplados()
   
   # Crear un diccionario para guardar los descansos asignados por empleado
   descansos_por_empleado = {}

   lista_turnos = definir_turnos(total_colaboradores, 0.35, 0.65) ## contiene descanso por dia, colab tmat, colab tvesp
   fecha_ant  = calcular_fecha("08", "09", "2024") #sustituir por variables para poder cambiarlas a necesidad del usuario
   horario_anterior = consulta_horario_ant(fecha_ant)

   
   
   for dia in range(1,8):
      disponibilidad = consulta_disponibilidad(dia) ## insertar cmo parametro el dia de la semana que se necesita consultar
      lista_tipos_turno = ['desc_mat', 'desc_ves','cierre_2', 'cierre_1','apertura_1','apertura_2', 'apertura_3', 'intermedio_1', 'intermedio_2', 'intermedio_3']
      lista_turnos_descansos = next((d for d in lista_turnos if d.get('id_dia') == dia), None) #extraer diccionario con los turnos del dia actual en la iteracion
      
      for l in lista_tipos_turno: 
         #empleados_disponibles = [e for e in disponibilidad if empleados_descansos.get(e['id_empleado']) != dia]  # excluye empleados en su día de descanso
         asignar_horarios(lista_turnos, disponibilidad, l, listaHorarios, dia, lista_turnos_descansos, descansos_por_empleado)
      
      

   
   print(tabulate(listaHorarios, headers='keys'))   





#calcular_fecha()
#listar_empleados()
generar_horario()
#definir_turnos(0.4, 0.6) 

#consulta_horario_ant('2024-09-01')

