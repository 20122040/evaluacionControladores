from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
import xlrd
from models.Controlador import Persona, Proceso, LaborPorProceso
from controllers import funciones, reportes, procesos, personas
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
import json
import time
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

@mod_evaluacion.route("/pantallaImportar")
def importar2():
  return render_template("importar.tpl.html")


@mod_evaluacion.route("/importar",methods=["POST"])
def importar():
  file = request.form.get('file', '')
  print(file)
  #Abrir el workbook y definir la hoja
  book = xlrd.open_workbook(file)
  #sheet = book.sheet_by_name("Hoja 1")
  sheet = book.sheet_by_index(0)
  #Crear un loop FOR para iterar en cada fila del archivo XLS empezando en la fila 2
  for r in range(1,sheet.nrows):
    codigo = sheet.cell(r,0).value
    nombres = sheet.cell(r,1).value
    correo = sheet.cell(r,2).value
    nuevo_controlador = personas.getPersonaSola(codigo);
    if nuevo_controlador is None:
      print("No se encontró código")
      controlador = Persona(codigo,nombres,correo,0,0)
      db.session.add(controlador)
    else:
      print("Se encontró código")
      nuevo_controlador.nombres = nombres
      nuevo_controlador.correo = correo
      nuevo_controlador.nro_convocatorias = 0
      nuevo_controlador.nro_asistencias = 0
    db.session.commit()

  print("")
  print("All Done! Bye, for now!")
  columns = str(sheet.ncols)
  rows = str(sheet.nrows)
  print("I just imported " + rows + "records to the db")

  return json.dumps(True)


@mod_evaluacion.route("/procesarJSON/",methods=["POST"])
def procesarJSON():
  codigo = request.form.get('codigo', '')
  calificacion = request.form.get('calificacion', '')
  observaciones = request.form.get('observaciones', '')
  #print(codigo + " " + calificacion + " " +observaciones)
  controlador = personas.getControlador(codigo)
  if controlador is not None:
    #print(controlador.codigo)
    controlador.calificacion = calificacion
    controlador.obs_proceso = observaciones
    db.session.commit()
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONObs/",methods=["POST"])
def procesarJSONObs():
  codigo = request.form.get('codigo', '')
  observaciones = request.form.get('observaciones', '')
  #print(codigo[1] + " " + calificacion[1] + " " +observaciones[1])
  controlador = personas.getControlador(codigo)
  if controlador is not None:
    #print(controlador.codigo)
    controlador.obs_capacitacion = observaciones
    db.session.commit()
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONEditar/",methods=["POST"])
def procesarJSONEditar():
  print("Estoy aquí")
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
  persona = funciones.getPersonaSola(codigo)
  print(codigo + "\n" + proceso)
  print(name + "\n" + aula)
  if controlador is not None:
    print("Encontré controlador")
    persona.nombres = name
    persona.correo = email
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
    #controlador.labor = request.form.get('labor','')
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

@mod_evaluacion.route("/procesarJSONNuevo/",methods=["POST"])
def procesarJSONNuevo():
  #Agregando Persona
  codigo = request.form.get('codigo', '')
  name = request.form.get('name', '')
  email = request.form.get('email','')

  nuevo_controlador = funciones.getPersonaSola(codigo);

  if nuevo_controlador is not None:
    nuevo_controlador.nombres = name;
    nuevo_controlador.email = email;
    nuevo_controlador.nro_asistencias = 0;
    nuevo_controlador.nro_convocatorias = 0;
  else:
    controlador = Persona(codigo,name,email,0,0)
    db.session.add(controlador)
  db.session.commit()

  #Agregando Labor_Por_Proceso
  proceso = request.form.get('proceso','')  
  labor = request.form.get('labor','')
  aula = request.form.get('aula','')
  aula_coord = request.form.get('aula_coord','')
  cod_coord = request.form.get('cod_coord','')
  new_controlador = funciones.getPersonaEditar(codigo,proceso)
  if (new_controlador is not None):
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
    db.session.commit()
  else:
    if(labor=="CONTROLADOR"):
      lxp = LaborPorProceso(codigo,proceso,0,0,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','')
    elif(labor=="COORDINADOR"):
      lxp = LaborPorProceso(codigo,proceso,1,0,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','')
    elif(labor=="ASISTENTE"):
      lxp = LaborPorProceso(codigo,proceso,0,0,1,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','')
    elif(labor=="APOYO"): 
      lxp = LaborPorProceso(codigo,proceso,0,1,0,aula,aula_coord,'',datetime.now().date(),datetime.now().date(),None,None,cod_coord,'0','','','')
    #controlador.labor = request.form.get('labor','')
    db.session.add(lxp)
    db.session.commit()
  return json.dumps(True)

@mod_evaluacion.route("/procesarJSONAsist/",methods=["POST"])
def procesarJSONAsist():
  codigo = request.form.get('codigo', '')
  asistencia = request.form.get('asistencia', '')
  controlador = personas.getControlador(codigo)
  if controlador is not None:
    if(asistencia == "true"):
      controlador.hora_proceso = datetime.now().time()
    elif (asistencia == "false"):
      controlador.hora_proceso = None
    db.session.commit()
    time.sleep(1)
    return json.dumps(True)
  else:
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONAsistCap/",methods=["POST"])
def procesarJSONAsistCap():
  codigo = request.form.get('codigo', '')
  asistencia = request.form.get('asistencia', '')
  controlador = personas.getControlador(codigo)
  print("Estoy aquí, mi código es:")
  print(controlador.codigo);
  if controlador is not None:
    print("Se encontro controlador")
    print(codigo + " " + asistencia)
    if(asistencia == "true"):
      print("Entró al true")
      controlador.hora_capacitacion = datetime.now().time()
    elif (asistencia == "false"):
      controlador.hora_capacitacion = None
    db.session.commit()
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/evaluacion/")
def evaluacion():
  reg = funciones.getReporteControladores(1)
  asist = funciones.getAsistentes()
  apoyos = funciones.getApoyo()
  coordinadores = funciones.getCoordinadoresUltimoProceso()
  return render_template("evaluacion.tpl.html",registros = reg,asistentes = asist, apoyos = apoyos,coordinadores = coordinadores)

@mod_evaluacion.route("/01X9jK6g/")
def asistencia():
  reg = funciones.getReporteControladores(1)
  asist = funciones.getAsistentes()
  apoyo = funciones.getApoyo()
  return render_template("asistencia.tpl.html",registros = reg,asistentes = asist,apoyos = apoyo)

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
      procesos = procesos.obtenerProcesosControlador(codigo)
      return render_template('controlador_view.tpl.html',registro=reg,procesos=procesos)

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
