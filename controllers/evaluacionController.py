import flask_excel as excel
import json
import time
import os
import xlsxwriter
import pandas as pd
#import xlrd

from flask import Flask, request, render_template, Blueprint, redirect, url_for
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
from models.Controlador import Persona, Proceso, LaborPorProceso
from controllers import funciones, reportes, procesos, personas, importar
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
from app import app, ALLOWED_EXTENSIONS
#Blueprint definition
mod_evaluacion = Blueprint('evaluacion', __name__)

@mod_evaluacion.route("/")
def example():
  return "Evaluación Controladores"

@mod_evaluacion.route("/exportarExcelAsistencia/",methods=['GET'])
def exportarExcelAsistencia():
  resultados = reportes.getReporteAsistencia()
  column_names = ['codigo', 'nombres','cod_coord','aula_capacitacion','hora_capacitacion','obs_capacitacion']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name="Reporte Capacitación")

@mod_evaluacion.route("/exportarExcelEvaluacion/",methods=['GET'])
def exportarExcelEvaluacion():
  resultados = reportes.getReporteEvaluacion()
  proceso = procesos.getUltimoProceso()
  nombreFile = "Evaluación de Colaboradores (" + proceso.nombre + " - " + str(proceso.fecha) + ")"
  column_names = ['codigo', 'nombres', 'aula','cod_coord','es_coord','es_apoyo','es_asistente','hora_proceso','calificacion','obs_proceso']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name=nombreFile)

@mod_evaluacion.route("/exportarExcelReporte/",methods=['GET'])
def exportarExcelReporte():
  resultados = reportes.getReporte()
  column_names = ['codigo', 'nombres', 'nombre','calificacion','obs_proceso','nro_convocatorias','nro_asistencias','correo']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name="Reporte General")

@mod_evaluacion.route("/reporte/")
def reporte():
  #actualizarDatos()
  reg = funciones.getReporteControladores()
  return render_template("reporte.tpl.html",registros = reg)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def añadirBD(arch_name):
  folder = "downloaded_files/"
  files = listdir(folder)

  for file in files:
    print("Leyendo: " + folder + file + "...\n")
    controladores_data = pd.read_excel(folder + file,'PARA EXPORTAR')
    #print(controladores_data)
    row = 1
    #Primero hacemos un import en la tabla personas
    for codigo in controladores_data['Código']:
      nombres = controladores_data['Apellido Paterno'][row-1] + " " + controladores_data['Apellido Materno'][row-1] + ", " + controladores_data['Nombres'][row-1] 
      nuevo_controlador = personas.getPersonaSola(codigo);
      if nuevo_controlador is None:
        print("No se encontró código")
        controlador = Persona(str(codigo).zfill(8),nombres,'',0,0)
        db.session.add(controlador)
      else:
        print("Se encontró código")
        nuevo_controlador.nombres = nombres
      db.session.commit()
      #Agregando Labor_Por_Proceso
      proceso = procesos.getUltimoProceso()
      es_coord = controladores_data['Es coordinador'][row-1]
      es_apoyo = controladores_data['Apoyo OCAI'][row-1]
      es_asistente = controladores_data['Asistente OCAI'][row-1]  
      aula = controladores_data['Aula'][row-1]
      aula_coord = controladores_data['Aula coordinación'][row-1]
      cod_coord = controladores_data['codigo Coordinador'][row-1]
      new_controlador = personas.getPersonaEditar(codigo,proceso.idproceso)
      #Si ya hay un controlador registrado con ese código en ese proceso
      if new_controlador is not None:
        new_controlador.aula = aula
        new_controlador.aula_coord = aula_coord
        new_controlador.cod_coord = str(cod_coord).zfill(8)
        new_controlador.es_coord = 0 if es_coord == 'FALSO' else 1
        new_controlador.es_apoyo = 0 if es_apoyo == 'FALSO' else 1
        new_controlador.es_asistente = 0 if es_asistente == 'FALSO' else 1
      else:
        lxp = LaborPorProceso(str(codigo).zfill(8),proceso.idproceso,0 if es_coord == 'FALSO' else 1,0 if es_apoyo == 'FALSO' else 1,0 if es_asistente == 'FALSO' else 1,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,str(cod_coord).zfill(8),'0','','','','')
        db.session.add(lxp)  
      db.session.commit()
      row = row + 1

  os.remove('downloaded_files/' + arch_name)

@mod_evaluacion.route("/pantallaImportar",methods=['GET','POST'])
def importar2():
  if request.method == 'GET':
    #solo mostrar el formulario
    errores = ['Descarga el formato de la base, <a href="/static/formato/'+ 'FORMATO LISTA CONTROLADORES Y COORDINADORES.xlsx' +'">Descargar el formato</a>']
    return render_template("importar.tpl.html",messages=errores)
  else:
    #Si es POST entonces se subió un archivo
    if 'archivos' in request.files: #verificar si se selecciono archivos
      files = request.files.to_dict(flat=False)['archivos']
      for f in files:
        if f and allowed_file(f.filename): #verificar que se subio xls o xlsx
          filename = secure_filename(f.filename) #crear nombre seguro para evitar XSS
          f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #guardar el archivo
    #Se procesan los archivos
    folder = "uploaded_files/"
    files = listdir(folder)

    proceso = procesos.getUltimoProceso()
    arch_name = 'Base para access ' + proceso.nombre + '.xlsx'
    arch_name.replace(' ','_')
    folder_base = "static/bases/"
    files_base = listdir(folder_base)
    if(len(files_base)!=0):
      os.remove('static/bases/' + arch_name)
    writer = xlsxwriter.Workbook('downloaded_files/'+arch_name)
    writer2 = xlsxwriter.Workbook('static/bases/'+arch_name)

    for file in files:
      print("Leyendo: " + folder + file + "...\n")
      coordinadores_data = pd.read_excel(folder + file,'COORDINADORES')
      #print(coordinadores_data)
      controladores_data = pd.read_excel(folder + file,'CONTROLADORES')
      importar.writeToCoordinadores(writer,coordinadores_data)
      importar.writeToControladores(writer,controladores_data)
      importar.writeToCoordinadores(writer2,coordinadores_data)
      importar.writeToControladores(writer2,controladores_data)
      worksheet = writer.add_worksheet('AULAS')
      worksheet = writer2.add_worksheet('AULAS')
      importar.writeToBaseParaExportar(writer,coordinadores_data,controladores_data)
      importar.writeToBaseParaExportar(writer2,coordinadores_data,controladores_data)
      
    writer.close()
    writer2.close()

    #Se eliminan los archivos
    for file in files:
      if(file[file.find("."):] in [".xls",".xlsx"]):
        os.remove(folder + file)
    errores = ['Desde aquí puede descargar la base para access, <a href="/static/bases/'+ arch_name +'">Descargar base para access</a>']
  
    añadirBD(arch_name)

  
    #errores = ['Desde aquí puede descargar la base para access, <a href="/downloaded_files/'+ arch_name +'">Descargar base para access</a>']
    
    return render_template('importar.tpl.html',messages=errores)

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
    db.session.commit()
    return json.dumps(True)
  else:
    print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONEditarPersona/",methods=["POST"])
def procesarJSONEditarPersona():
  codigo = request.form.get('codigo', '')
  name = request.form.get('name', '')
  email = request.form.get('email','')

  person= personas.getPersonaSola(codigo)
  if person is not None:
    person.nombres = name
    person.correo = email
    db.session.commit()
    return json.dumps(True)
  else:
    print("No se encontró el Controlador")
    return json.dumps(False)

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
    controlador = Persona(codigo,name,email,0,0)
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
  return render_template("evaluacion.tpl.html",registros = reg,asistentes = asist, apoyos = apoyos,coordinadores = coordinadores)

@mod_evaluacion.route("/asistencia/")
def asistencia2():
  reg = funciones.getControladoresCapacitacion()
  asist = funciones.getAsistentes()
  apoyo = funciones.getApoyo()
  aulas = funciones.getAulas()
  return render_template("asistencia2.tpl.html",registros = reg,asistentes = asist,apoyos = apoyo,aulas = aulas)

@mod_evaluacion.route('/verControlador/<codigo>')
def verControlador(codigo=None):
    if (codigo == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = personas.obtenerControladorPorProceso(codigo)
      proc = procesos.obtenerProcesosControlador(codigo)
      return render_template('controlador_view.tpl.html',registro=reg,procesos=proc)

@mod_evaluacion.route('/editarControlador/<codigo>/<idproceso>')
def editarControlador(codigo=None,idproceso=None):
    if (idproceso == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = personas.obtenerControladorPorProceso(codigo,idproceso)
      return render_template('controlador_edit.tpl.html',registro=reg)

@mod_evaluacion.route('/nuevoControlador/')
def nuevoControlador():
  pro = procesos.obtenerProcesos()
  return render_template('controlador_new.tpl.html',procesos=pro)

@mod_evaluacion.route('/nuevoProceso/')
def nuevoProceso():
  pro = procesos.obtenerProcesos()
  return render_template('proceso_new.tpl.html',procesos=pro)

@mod_evaluacion.route('/administrador/')
def administrador():
  cantPersonas = personas.getCantidadPersonas()
  cantProcesos = procesos.getCantidadProcesos()
  cantControladores = personas.getCantidadControladores()
  return render_template('administrador.tpl.html',nPer=cantPersonas,nProc=cantProcesos,nCont=cantControladores)

@mod_evaluacion.route('/persona/')
def persona():
  reg = funciones.getAllWorkers()
  return render_template('persona_index.tpl.html',registros=reg)

@mod_evaluacion.route('/editarPersona/<codigo>')
def editarPersona(codigo=None):
  reg = personas.getPersonaSola(codigo)
  return render_template('persona_edit.tpl.html',registro=reg)