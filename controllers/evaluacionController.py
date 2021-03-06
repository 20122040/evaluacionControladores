import flask_excel as excel
import json
import time
import os
import xlsxwriter
import pandas as pd
import math
import bcrypt
from urllib.parse import quote_plus
#import xlrd

from flask import Flask, request, render_template, Blueprint, redirect, url_for
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
from models.Controlador import Persona, Proceso, LaborPorProceso, User
from controllers import funciones, reportes, procesos, personas, importar
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
from app import app, ALLOWED_EXTENSIONS
#Blueprint definition
mod_evaluacion = Blueprint('evaluacion', __name__)

@mod_evaluacion.route("/")
def example():
  #print(validate_login(request))
  return "Evaluación Controladores"

def validate_login(request):
  username_cookie = request.cookies.get('username')
  #print(username_cookie)
  if (username_cookie is None) or (username_cookie == ''):
    return False
  
  userAndHash = username_cookie.split('|')
  if len(userAndHash) != 2:
    return False

  if not bcrypt.checkpw((userAndHash[0]+ app.config['SECRET_KEY']).encode('utf-8'),userAndHash[1].encode('utf-8')):
    return False

  return True

@mod_evaluacion.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'GET':
    return render_template('login.tpl.html')
  else:
    destination = request.args.get('dest', '/')
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(user=username).first()

    if user is not None:
      #userSecret =(password + app.config['SECRET_KEY']).encode('utf-8')
      upass = user.password
      #print(upass)
      #if bcrypt.checkpw(userSecret,upass.encode('utf-8')): 
      if (password == upass):
        resp = redirect(destination)
        hashed = bcrypt.hashpw((username+ app.config['SECRET_KEY']).encode('utf-8'),bcrypt.gensalt())
        resp.set_cookie('username',username+'|'+ hashed.decode('utf-8'))
        return resp
    return render_template('login.tpl.html',messages=['El usuario y/o la contraseña son incorrectos'])

@mod_evaluacion.route('/logout',methods=['GET'])
def logout():
  resp = redirect('/login')
  resp.set_cookie('username','')
  return resp

def quitarEspacios(cadena):
  cadena = cadena.replace(' ','')
  cadena = cadena.replace('°','')
  cadena = cadena.replace('á','a')
  cadena = cadena.replace('é','e')
  cadena = cadena.replace('í','i')
  cadena = cadena.replace('ó','o')
  cadena = cadena.replace('ú','u')
  return cadena

@mod_evaluacion.route("/exportarExcelAsistencia/",methods=['GET','POST'])
def exportarExcelAsistencia():
  if (validate_login(request)):
    proc = procesos.obtenerProcesos()
    if request.method == 'GET':
      return render_template('exportar_capacitacion.tpl.html',procesos=proc)
    else:
      proceso_select = request.form['proceso-select']
      #print("Este es el select " + str(proceso_select))
      resultados = reportes.getReporteAsistencia(proceso_select)
      procX = procesos.getProcesoPorId(proceso_select)
      codigos=[]
      nombres=[]
      correos=[]
      aula=[]
      labor=[]
      hora=[]
      asistio=[]
      obs=[]
      column_names = ['codigo', 'nombres','correo','LaborPUCP','aula_capacitacion','hora_capacitacion','obs_capacitacion']
      for res in resultados:
        codigos.append(res.codigo)
        nombres.append(res.nombres)
        correos.append(res.correo)
        labor.append(res.tipoPersona)
        aula.append(res.aula_capacitacion)
        hora.append(res.hora_capacitacion)
        if(res.hora_capacitacion is not None):
          asistio.append("SI")
        else:
          asistio.append("NO")
        obs.append(res.obs_capacitacion)
      d = {'Código': codigos, 'Nombres': nombres, 'Correo':correos, 'LaborPUCP':labor,'Aula de Capacitación': aula, 'Hora Capacitación':hora, '¿Asistió?':asistio, 'Observaciones': obs} 
      df = pd.DataFrame(data=d,columns=['Código','Nombres','Correo','Labor PUCP','Aula de Capacitación','Hora Capacitación','¿Asistió?','Observaciones'])

      file_name = "ReporteDeAsistencia-" + quitarEspacios(procX.nombre) + "(" + datetime.now().strftime('%d-%m-%Y-%H_%M_%S') + ").xlsx"
      #writer = pd.ExcelWriter('/var/www/asistenciaControladores/asistenciaPucp/static/reportes/'+file_name)
      writer = pd.ExcelWriter('static/reportes/'+file_name)
      df.to_excel(writer,sheet_name='Hoja 1',index=False)
      writer.save()
      m = ['Descargar reporte de asistencia a capacitación, <a href="/static/reportes/'+ file_name +'">Descargar</a>']
      return render_template('exportar_capacitacion.tpl.html',procesos=proc,messages=m)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route("/exportarExcelEvaluacion/",methods=['GET','POST'])
def exportarExcelEvaluacion():
  if (validate_login(request)):
    proc = procesos.obtenerProcesos()
    if request.method == 'GET':
      return render_template('exportar_evaluacion.tpl.html',procesos=proc)
    else:
      proceso_select = request.form['proceso-select']
      resultados = reportes.getReporteEvaluacion(proceso_select)
      procX = procesos.getProcesoPorId(proceso_select)
      codigos=[]
      nombres=[]
      correos=[]
      labor=[]
      proceso_names=[]
      es_coord=[]
      es_apoyo=[]
      es_asistente=[]
      aulas=[]
      aulas_coord=[]
      fechas=[]
      codigos_coord=[]
      calificaciones=[]
      observaciones=[]
      asistio=[]
      asistio_cap=[]
      for res in resultados:
        codigos.append(res.codigo)
        nombres.append(res.nombres)
        correos.append(res.correo)
        labor.append(res.tipoPersona)
        proceso_names.append(res.nombre)
        if(res.es_coord == 1):
          es_coord.append("VERDADERO")
          es_asistente.append("FALSO")
          es_apoyo.append("FALSO")
        elif(res.es_apoyo == 1):
          es_coord.append("FALSO")
          es_asistente.append("FALSO")
          es_apoyo.append("VERDADERO")
        elif(res.es_asistente == 1):
          es_coord.append("FALSO")
          es_asistente.append("VERDADERO")
          es_apoyo.append("FALSO")
        else:
          es_coord.append("FALSO")
          es_asistente.append("FALSO")
          es_apoyo.append("FALSO")
        aulas.append(res.aula)
        aulas_coord.append(res.aula_coord)
        if(res.hora_proceso is not None):
          asistio.append("SI")
        else:
          asistio.append("NO")
        if(res.calificacion == '0'):
          calificaciones.append("-")
        else: 
          calificaciones.append(res.calificacion)
        observaciones.append(res.obs_proceso)
        fechas.append(res.fecha)
        codigos_coord.append(res.cod_coord)
        if(res.hora_capacitacion is not None):
          asistio_cap.append("SI")
        else:
          asistio_cap.append("NO")


      d = {'Codigo': codigos, 'Nombres': nombres, 'Correo':correos, 'Labor PUCP':labor, 'Proceso':proceso_names, 'Es Coordinador':es_coord, 'Es Apoyo':es_apoyo, 
      'Es Asistente':es_asistente, 'Aula': aulas, 'Aula de Coordinacion':aulas_coord, 'Fecha del Proceso':fechas, 'Asistio al proceso':asistio, 
      'Asistio a la capacitacion':asistio_cap, 'Codigo de Coordinador':codigos_coord, 'Calificacion':calificaciones, 'Observaciones':observaciones} 
      df = pd.DataFrame(data=d,columns=['Codigo','Nombres','Correo','Labor PUCP','Proceso','Es Coordinador','Es Apoyo','Es Asistente','Aula',
        'Aula de Coordinacion','Fecha del Proceso','Asistio al proceso','Asistio a la capacitacion','Codigo de Coordinador',
        'Calificacion','Observaciones'])
    
      file_name = "EvaluacionDeColaboradores-" + quitarEspacios(procX.nombre) + "(" + datetime.now().strftime('%d-%m-%Y-%H_%M_%S') + ").xlsx"
      #writer = pd.ExcelWriter('/var/www/asistenciaControladores/asistenciaPucp/static/reportes/'+file_name)
      writer = pd.ExcelWriter('static/reportes/'+file_name)
      df.to_excel(writer,sheet_name='Hoja 1',index=False)
      writer.save()
      m = ['Descargar reporte de evaluación de controladores, <a href="/static/reportes/'+ file_name +'">Descargar</a>']
      return render_template('exportar_evaluacion.tpl.html',procesos=proc,messages=m)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route("/reporte/", methods=['GET','POST'])
def reporte():
  if (validate_login(request)):
    #actualizarDatos()
    if request.method == 'GET':
      reg = funciones.getReporteControladores()
      return render_template("reporte.tpl.html",registros = reg)
    else:
      codigo = request.form.get('codigo', '')
      idproceso = request.form.get('idproceso', '')
      cont = personas.getPersonaEditar(codigo,idproceso)
      db.session.delete(cont)
      db.session.commit()
      reg = funciones.getReporteControladores()
      return render_template("reporte.tpl.html",registros = reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getCorreo(codigo,controladores_data,coordinadores_data):
  #coordinadores_data['Código'] = coordinadores_data['Código'].astype(str)
  #coordinadores_data['Código'] = coordinadores_data['Código'].apply(lambda x: x.zfill(8))

  controladores_data['Código'] = controladores_data['Código'].astype(str)
  controladores_data['Código'] = controladores_data['Código'].apply(lambda x: x.zfill(8))

  codigo = str(codigo).zfill(8)
  correo = coordinadores_data["Correo electrónico"].loc[(coordinadores_data["Código"].astype(str).apply(lambda x: x.zfill(8))==codigo)]
  if (len(correo)!=0):
    return correo.values[0]
  else:
    correo = controladores_data["Correo electrónico"].loc[(controladores_data["Código"].astype(str).apply(lambda x: x.zfill(8))==codigo)]
    if (len(correo)!=0):
      return correo.values[0]
    else:
      return "No hay correos"

def getAulaCapacitacion(codigo,controladores_data,coordinadores_data):
  #coordinadores_data['Código'] = coordinadores_data['Código'].astype(str)
  #coordinadores_data['Código'] = coordinadores_data['Código'].apply(lambda x: x.zfill(8))

  controladores_data['Código'] = controladores_data['Código'].astype(str)
  controladores_data['Código'] = controladores_data['Código'].apply(lambda x: x.zfill(8))

  codigo = str(codigo).zfill(8)
  
  aula = coordinadores_data["CAPACITACIÓN"].loc[(controladores_data["Código"].astype(str).apply(lambda x: x.zfill(8))==codigo)]  
  if (len(aula)!=0):
    return aula.values[0]
  else:
    aula = controladores_data["CAPACITACIÓN"].loc[(controladores_data["Código"].astype(str).apply(lambda x: x.zfill(8))==codigo)]
    if (len(aula)!=0):
      return aula.values[0]
    else:
      return "Sin aula"

def añadirBD(arch_name,controladores_data,coordinadores_data,proceso_select):
  #folder = "/var/www/asistenciaControladores/asistenciaPucp/downloaded_files/"
  folder = "downloaded_files/"
  files = listdir(folder)

  for file in files:
    print("Leyendo: " + folder + file + "...\n")
    personas_data = pd.read_excel(folder + file,'PARA EXPORTAR')
    #print(controladores_data)
    row = 1
    #Primero hacemos un import en la tabla personas
    for codigo in personas_data['Código']:
      nombres = personas_data['Apellido Paterno'][row-1] + " " + personas_data['Apellido Materno'][row-1] + ", " + personas_data['Nombres'][row-1] 
      correo = getCorreo(codigo,controladores_data,coordinadores_data)
      nuevo_controlador = personas.getPersonaSola(codigo);
      if nuevo_controlador is None:
        print("No se encontró código")
        controlador = Persona(str(codigo).zfill(8),nombres,correo,'',0,0)
        db.session.add(controlador)
      else:
        print("Se encontró código")
        nuevo_controlador.nombres = nombres
        nuevo_controlador.correo = correo
      db.session.commit()
      #Agregando Labor_Por_Proceso
      proceso = procesos.getProcesoPorId(proceso_select)
      es_coord = personas_data['Es coordinador'][row-1]
      es_apoyo = personas_data['Apoyo OCAI'][row-1]
      es_asistente = personas_data['Asistente OCAI'][row-1]  
      aula = personas_data['Aula'][row-1]
      aula_coord = personas_data['Aula coordinación'][row-1]
      cod_coord = personas_data['codigo Coordinador'][row-1]
      new_controlador = personas.getPersonaEditar(codigo,proceso.idproceso)
      aula_capacitacion = getAulaCapacitacion(codigo,controladores_data,coordinadores_data)
      #Si ya hay un controlador registrado con ese código en ese proceso
      if new_controlador is not None:
        new_controlador.aula = aula
        new_controlador.aula_coord = aula_coord
        new_controlador.cod_coord = str(cod_coord).zfill(8)
        new_controlador.es_coord = 0 if es_coord == 'FALSO' else 1
        new_controlador.es_apoyo = 0 if es_apoyo == 'FALSO' else 1
        new_controlador.es_asistente = 0 if es_asistente == 'FALSO' else 1
        new_controlador.aula_capacitacion = aula_capacitacion
      else:
        lxp = LaborPorProceso(str(codigo).zfill(8),proceso.idproceso,0 if es_coord == 'FALSO' else 1,0 if es_apoyo == 'FALSO' else 1,0 if es_asistente == 'FALSO' else 1,aula,aula_coord,aula_capacitacion,datetime.now().date(),datetime.now().date(),None,None,str(cod_coord).zfill(8),'0','','','','')
        db.session.add(lxp)  
      db.session.commit()
      row = row + 1
  #os.remove('/var/www/asistenciaControladores/asistenciaPucp/downloaded_files/' + arch_name)
  os.remove('downloaded_files/' + arch_name)

def guardarReserva(reserva_data,errores,proceso_select):
  row=1
  for codigo in reserva_data['Código']:
    nombres = reserva_data['Primer apellido'][row-1] + " " + reserva_data['Segundo apellido'][row-1] + ", " + reserva_data['Nombres'][row-1]
    #Revisar si la persona ya existe o no
    controladorR = personas.getPersonaSola(codigo);
    if controladorR is None:
      controladorR = Persona(str(codigo).zfill(8),nombres,'','',0,0)
      db.session.add(controladorR)
    else:
      controladorR.nombres = nombres
    db.session.commit()

    #Agregando Labor_Por_Proceso
    proceso = procesos.getProcesoPorId(proceso_select)
    
    aula = reserva_data['AULA'][row-1]
    aula_coord = reserva_data['AULA DE COORDINACIÓN'][row-1]

    #Esto aun no está listo desde aquí...
    coordinador = personas.getCoordinador(aula_coord,proceso.idproceso)

    new_controladorR = personas.getPersonaEditar(codigo,proceso.idproceso)

    #Si ya hay un controlador registrado con ese código en ese proceso
    if new_controladorR is not None:
      new_controladorR.aula = aula
      new_controladorR.aula_coord = aula_coord
      new_controladorR.cod_coord = str(coordinador.codigo).zfill(8)
      new_controladorR.es_coord = 0
      new_controladorR.es_apoyo = 0
      new_controladorR.es_asistente = 0
    else:
      lxp = LaborPorProceso(str(codigo).zfill(8),proceso.idproceso,0,0,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,str(coordinador.codigo).zfill(8),'0','','','','')
      db.session.add(lxp)  
    db.session.commit()
    row = row + 1
    #print(codigo)

@mod_evaluacion.route("/pantallaSubirReserva/",methods=['GET','POST'])
def importarReserva():
  if (validate_login(request)):
    proc = procesos.obtenerProcesos()
    if request.method == 'GET':
      #solo mostrar el formulario
      errores = ['Descarga el formato de la base <a href="/static/formato/' + 'FORMATO CONTROLADORES DE RESERVA.xlsx' + '">Descargar el formato</a>']
      return render_template("importarReserva.tpl.html",procesos=proc,messages=errores)
    else:
      #Si es POST entonces se subió un archivo
      proceso_select = request.form['proceso-select']
      procX = procesos.getProcesoPorId(proceso_select)
      if 'archivos' in request.files:
        files = request.files.to_dict(flat=False)['archivos']
        for f in files:
          if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

      #folder = "/var/www/asistenciaControladores/asistenciaPucp/uploaded_files/"
      folder = "uploaded_files/"
      files = listdir(folder)

      errores=[]
      for file in files:
        print("Leyendo: " + folder + file + "...\n")
        reserva_data = pd.read_excel(folder + file,'CONTROLADORES')
        #reserva_data
      #print(reserva_data['Código'][0])
      guardarReserva(reserva_data,errores,proceso_select)
      #Se eliminan los archivos
      for file in files:
        if(file[file.find("."):] in [".xls",".xlsx"]):
          os.remove(folder + file)

      if len(errores)==0:
        errores.append('Se importó con éxito a los controladores de reserva')
      
      return render_template('importar.tpl.html',procesos=proc,messages=errores)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route("/pantallaImportar",methods=['GET','POST'])
def importar2():
  if (validate_login(request)):
    proc = procesos.obtenerProcesos()
    if request.method == 'GET':
      #solo mostrar el formulario
      errores = ['Descarga el formato de la base, <a href="/static/formato/'+ 'FORMATO LISTA CONTROLADORES Y COORDINADORES.xlsx' +'">Descargar el formato</a>']
      return render_template("importar.tpl.html",procesos=proc,messages=errores)
    else:
      #Si es POST entonces se subió un archivo
      proceso_select = request.form['proceso-select']
      procX = procesos.getProcesoPorId(proceso_select)
      if 'archivos' in request.files: #verificar si se selecciono archivos
        files = request.files.to_dict(flat=False)['archivos']
        for f in files:
          if f and allowed_file(f.filename): #verificar que se subio xls o xlsx
            filename = secure_filename(f.filename) #crear nombre seguro para evitar XSS
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #guardar el archivo
      #Se procesan los archivos
      #folder = "/var/www/asistenciaControladores/asistenciaPucp/uploaded_files/"
      folder = "uploaded_files/"
      files = listdir(folder)

      arch_name = 'BaseParaAccess' + quitarEspacios(procX.nombre) + '.xlsx'
      #arch_name.replace(' ','_')
      #folder_base = "/var/www/asistenciaControladores/asistenciaPucp/static/bases/"
      folder_base = "static/bases/"
      files_base = listdir(folder_base)
      #if(len(files_base)!=0):
      #  os.remove('static/bases/' + arch_name)
      #writer = xlsxwriter.Workbook('/var/www/asistenciaControladores/asistenciaPucp/downloaded_files/'+arch_name)
      #writer2 = xlsxwriter.Workbook('/var/www/asistenciaControladores/asistenciaPucp/static/bases/'+arch_name)
      writer = xlsxwriter.Workbook('downloaded_files/'+arch_name)
      writer2 = xlsxwriter.Workbook('static/bases/'+arch_name)

      errores=[]
      for file in files:
        print("Leyendo: " + folder + file + "...\n")
        coordinadores_data = pd.read_excel(folder + file,'COORDINADORES')
        #print(coordinadores_data)
        controladores_data = pd.read_excel(folder + file,'CONTROLADORES')
        importar.writeToCoordinadores(writer,coordinadores_data,errores,1)
        importar.writeToControladores(writer,controladores_data,errores,1)
        importar.writeToCoordinadores(writer2,coordinadores_data,errores,0)
        importar.writeToControladores(writer2,controladores_data,errores,0)
        worksheet = writer.add_worksheet('AULAS')
        worksheet = writer2.add_worksheet('AULAS')
        importar.writeToBaseParaExportar(writer,coordinadores_data,controladores_data,errores)
        importar.writeToBaseParaExportar(writer2,coordinadores_data,controladores_data,errores)
        
      writer.close()
      writer2.close()

      #Se eliminan los archivos
      for file in files:
        if(file[file.find("."):] in [".xls",".xlsx"]):
          os.remove(folder + file)
      
      if (len(errores)==0):
        añadirBD(arch_name,controladores_data,coordinadores_data,proceso_select)
        #errores = ['Desde aquí puede descargar la base para access, <a href="/downloaded_files/'+ arch_name +'">Descargar base para access</a>'
        errores.append(['Desde aquí puede descargar la base para access, <a href="/static/bases/'+ arch_name +'">Descargar base para access</a>'])
      return render_template('importar.tpl.html',procesos=proc,messages=errores)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route("/procesarJSON/",methods=["POST"])
def procesarJSON():
  codigo = request.form.get('codigo', '')
  calificacion = request.form.get('calificacion', '')
  observaciones = request.form.get('observaciones', '')
  observacionesCoordinacion = request.form.get('observacionesCoordinacion','')
  asistencia = request.form.get('asistencia','')
  option = request.form.get('option','')
  #print(codigo + " " + calificacion + " " +observaciones)
  controlador = personas.getControlador(codigo)
  if controlador is not None:
    #print(controlador.codigo)
    if(option == '1'):
      controlador.calificacion = calificacion
      controlador.obs_proceso = observaciones
      controlador.obs_coordinacion = observacionesCoordinacion
    else:
      controlador.obs_capacitacion = observaciones
    if(asistencia == "true"):
      if(option == '1'):
        if(controlador.hora_proceso is None):
          controlador.hora_proceso = datetime.now().time()
      else:
        controlador.hora_capacitacion = datetime.now().time()
    elif (asistencia == "false"):
      if(option == '1'):
        controlador.hora_proceso = None
      else:
        controlador.hora_capacitacion = None
    db.session.commit()
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONEditar/",methods=["POST"])
def procesarJSONEditar():
  #print("Estoy aquí")
  codigo = request.form.get('codigo', '')
  proceso = request.form.get('proceso','')
  name = request.form.get('name', '')
  email = request.form.get('email','')
  labor = request.form.get('labor','')
  aula = request.form.get('aula','')
  aula_coord = request.form.get('aula_coord','')
  cod_coord = request.form.get('cod_coord','')
  calificacion = request.form.get('calificacion','')
  obs_proceso = request.form.get('obs_proceso','')
  password = request.form.get('password','')

  controlador = personas.getPersonaEditar(codigo,proceso)
  person= personas.getPersonaSola(codigo)
  #print(codigo + "\n" + proceso)
  #print(name + "\n" + aula)
  if controlador is not None:
    #print("Encontré controlador")
    person.nombres = name
    person.correo = email
    if(labor=="CONTROLADOR"):
      controlador.es_coord = 0
      controlador.es_apoyo = 0
      controlador.es_asistente = 0
    elif(labor=="COORDINADOR"):
      controlador.es_coord = 1
      controlador.es_apoyo = 0
      controlador.es_asistente = 0
    elif(labor=="ASISTENTE"):
      controlador.es_coord = 0
      controlador.es_apoyo = 0
      controlador.es_asistente = 1
    elif(labor=="APOYO"):
      controlador.es_coord = 0
      controlador.es_apoyo = 1
      controlador.es_asistente = 0
    controlador.aula = aula
    controlador.aula_coord = aula_coord
    controlador.cod_coord = cod_coord
    controlador.calificacion = calificacion
    controlador.obs_proceso = obs_proceso
    controlador.password = password
    db.session.commit()
    return json.dumps(True)
  else:
    print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONNuevoPersona/",methods=["POST"])
def procesarJSONNuevoPersona():
  codigoPUCP = request.form.get('codigoPUCP', '')
  name = request.form.get('name', '')
  email = request.form.get('email','')
  tipo = request.form.get('tipo','')

  person = personas.getPersonaSola(codigoPUCP)
  if person is not None:
    person.nombres = name
    person.correo = email
    person.tipoPersona = tipo
  else:
    controlador = Persona(str(codigoPUCP).zfill(8),name,email,tipo,0,0)
    db.session.add(controlador)
    #print("No se encontró el Controlador")    
  db.session.commit()
  return json.dumps(False)

@mod_evaluacion.route("/procesarJSONEditarPersona/",methods=["POST"])
def procesarJSONEditarPersona():
  codigo = request.form.get('codigo', '')
  name = request.form.get('name', '')
  email = request.form.get('email','')
  tipo = request.form.get('tipo','')

  person= personas.getPersonaSola(codigo)
  if person is not None:
    person.nombres = name
    person.correo = email
    person.tipoPersona = tipo
    db.session.commit()
    return json.dumps(True)
  else:
    print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONEditarProceso/",methods=["POST"])
def procesarJSONEditarProceso():
  #Agregando Persona
  idproceso = request.form.get('idproceso', '')
  name = request.form.get('name', '')
  fecha_proc = request.form.get('fecha_proc','')
  fecha_cap = request.form.get('fecha_cap','')
  vigencia = request.form.get('vigencia','')

  fecha_proc = None if fecha_proc=='' else fecha_proc
  fecha_cap = None if fecha_cap=='' else fecha_cap

  proc = procesos.getProcesoPorId(idproceso)
  if proc is not None:
    proc.nombre = name
    proc.fecha = fecha_proc
    proc.fecha_cap = fecha_cap
    proc.es_ultimo = vigencia  
    db.session.commit()
    return json.dumps(True)    
  else:
    print("No se encontró el proceso")
    return json.dumps(True)

@mod_evaluacion.route("/procesarJSONNuevoProceso/",methods=["POST"])
def procesarJSONNuevoProceso():
  #Agregando Proceso
  idproceso = request.form.get('idproceso', '')
  name = request.form.get('name', '')
  fecha_proc = request.form.get('fecha_proc','')
  fecha_cap = request.form.get('fecha_cap','')
  vigencia = request.form.get('vigencia','')

  fecha_proc = None if fecha_proc=='' else fecha_proc
  fecha_cap = None if fecha_cap=='' else fecha_cap

  nuevo_proceso = Proceso(idproceso,name,fecha_proc,fecha_cap,vigencia)  

  db.session.add(nuevo_proceso)  
  db.session.commit()
  return json.dumps(True)    

@mod_evaluacion.route("/procesarJSONNuevo/",methods=["POST"])
def procesarJSONNuevo():
  #Agregando Persona
  codigo = request.form.get('codigo', '')
  name = request.form.get('name', '')
  email = request.form.get('email','')

  nuevo_controlador = personas.getPersonaSola(codigo);
  #Si ya hay un controlador en la tabla Persona con ese código
  if nuevo_controlador is not None:
    #Se actualizan los datos
    nuevo_controlador.nombres = name;
    nuevo_controlador.email = email;
    nuevo_controlador.nro_asistencias = 0;
    nuevo_controlador.nro_convocatorias = 0;
  else:
    #De lo contrario se crea a esa persona
    controlador = Persona(codigo,name,email,'',0,0)
    db.session.add(controlador)
  db.session.commit()

  #Agregando Labor_Por_Proceso
  proceso = request.form.get('proceso','')  
  labor = request.form.get('labor','')
  aula = request.form.get('aula','')
  aula_coord = request.form.get('aula_coord','')
  cod_coord = request.form.get('cod_coord','')
  new_controlador = personas.getPersonaEditar(codigo,proceso)
  #Si ya hay un controlador registrado con ese código.
  if new_controlador is not None:
    new_controlador.aula = aula;
    new_controlador.aula_coord = aula_coord;
    new_controlador.cod_coord = cod_coord; 
    if(labor=="CONTROLADOR"):
      new_controlador.es_coord = 0;
      new_controlador.es_apoyo = 0;
      new_controlador.es_asistente = 0;
    elif(labor=="COORDINADOR"):
      new_controlador.es_coord = 1;
      new_controlador.es_apoyo = 0;
      new_controlador.es_asistente = 0;
    elif(labor=="ASISTENTE"):
      new_controlador.es_coord = 0;
      new_controlador.es_apoyo = 0;
      new_controlador.es_asistente = 1;
    elif(labor=="APOYO"): 
      new_controlador.es_coord = 0;
      new_controlador.es_apoyo = 1;
      new_controlador.es_asistente = 0;
    #controlador.labor = request.form.get('labor','')
  else:
    if(labor=="CONTROLADOR"):
      lxp = LaborPorProceso(codigo,proceso,0,0,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','','')
    elif(labor=="COORDINADOR"):
      lxp = LaborPorProceso(codigo,proceso,1,0,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','','')
    elif(labor=="ASISTENTE"):
      lxp = LaborPorProceso(codigo,proceso,0,0,1,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','','')
    elif(labor=="APOYO"): 
      lxp = LaborPorProceso(codigo,proceso,0,1,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','','')
    #controlador.labor = request.form.get('labor','')
    db.session.add(lxp)  
  db.session.commit()
  return json.dumps(True)

@mod_evaluacion.route("/evaluacion/")
def evaluacion():
  reg = funciones.getReporteControladores(1)
  asist = funciones.getAsistentes()
  apoyos = funciones.getApoyo()
  coordinadores = funciones.getCoordinadoresUltimoProceso()
  username_cookie = request.cookies.get('username')
  if(username_cookie):
    userAndHash = username_cookie.split('|')
    user = User.query.filter_by(user=userAndHash[0]).first()
    if (user is not None):
      admin = user.administrador
    else:
      admin = 0
  else:
    admin = 0
  return render_template("evaluacion.tpl.html",registros = reg,asistentes = asist, apoyos = apoyos,coordinadores = coordinadores, admin = admin)


@mod_evaluacion.route("/asistencia/")
def asistencia2():
  reg = funciones.getControladoresCapacitacion()
  asist = funciones.getAsistentes()
  apoyo = funciones.getApoyo()
  aulas = funciones.getAulas()
  username_cookie = request.cookies.get('username')
  if(username_cookie):
    userAndHash = username_cookie.split('|')
    user = User.query.filter_by(user=userAndHash[0]).first()
    if (user is not None):
      admin = user.administrador
    else:
      admin = 0
  else:
    admin = 0
  return render_template("asistencia2.tpl.html",registros = reg,asistentes = asist,apoyos = apoyo,aulas = aulas,admin = admin)

@mod_evaluacion.route('/verControlador/<codigo>')
def verControlador(codigo=None):
  if (validate_login(request)):
    if (codigo == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = personas.obtenerControladorPorProceso(codigo)
      proc = procesos.obtenerProcesosControlador(codigo)
      return render_template('controlador_view.tpl.html',registro=reg,procesos=proc)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/editarControlador/<codigo>/<idproceso>')
def editarControlador(codigo=None,idproceso=None):
  if (validate_login(request)):
    if (idproceso == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = personas.obtenerControladorPorProceso(codigo,idproceso)
      return render_template('controlador_edit.tpl.html',registro=reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/nuevoControlador/')
def nuevoControlador():
  if (validate_login(request)):
    pro = procesos.obtenerProcesos()
    return render_template('controlador_new.tpl.html',procesos=pro)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/administrador/')
def administrador():
  #print(validate_login(request))
  if (validate_login(request)):
    cantPersonas = personas.getCantidadPersonas()
    cantProcesos = procesos.getCantidadProcesos()
    cantControladores = personas.getCantidadControladores()
    return render_template('administrador.tpl.html',nPer=cantPersonas,nProc=cantProcesos,nCont=cantControladores)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/persona/',methods=['GET','POST'])
def persona():
  if (validate_login(request)):
    if (request.method == 'GET'):
      reg = funciones.getAllWorkers()
      return render_template('persona_index.tpl.html',registros=reg)
    else:
      codigo = request.form.get('codigo', '')
      per = personas.getPersonaSola(codigo)
      db.session.delete(per)
      db.session.commit()
      reg = funciones.getAllWorkers()
      return render_template('persona_index.tpl.html',registros=reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/nuevoPersona/')
def nuevoPersona():
  if (validate_login(request)):
    return render_template('persona_new.tpl.html')
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/editarPersona/<codigo>')
def editarPersona(codigo=None):
  if (validate_login(request)):
    reg = personas.getPersonaSola(codigo)
    return render_template('persona_edit.tpl.html',registro=reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/verPersona/<codigo>')
def verPersona(codigo=None):
  if (validate_login(request)):
    if (codigo == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = personas.obtenerControladorPorProceso(codigo)
      proc = procesos.obtenerProcesosControlador(codigo)
      return render_template('persona_view.tpl.html',registro=reg,procesos=proc)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/proceso/', methods=['GET','POST'])
def proceso():
  if (validate_login(request)):
    if request.method == 'GET':
      reg = funciones.getAllProcesos()
      return render_template('procesos_index.tpl.html',registros=reg)
    else:
      idproceso = request.form.get('idproceso', '')
      proc = procesos.getProcesoPorId(idproceso)
      print(idproceso)
      db.session.delete(proc)
      db.session.commit()
      reg = funciones.getAllProcesos()
      return render_template('procesos_index.tpl.html',registros=reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/nuevoProceso/')
def nuevoProceso():
  if (validate_login(request)):
    pro = funciones.getAllProcesos()
    n = procesos.getCantidadProcesos()
    return render_template('proceso_new.tpl.html',procesos=pro,cant=n)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))

@mod_evaluacion.route('/editarProceso/<idproceso>')
def editarProceso(idproceso=None):
  if (validate_login(request)):
    reg = procesos.getProcesoPorId(idproceso)
    return render_template('proceso_edit.tpl.html',registro=reg)
  else:
    return redirect('login?dest=' + quote_plus(request.full_path))