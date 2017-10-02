from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
from models.Controlador import Persona, Proceso, LaborPorProceso
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
  resultados = getReporteAsistencia()
  column_names = ['codigo', 'nombres','cod_coord','aula_capacitacion','hora_capacitacion','obs_capacitacion']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name="Reporte Capacitación")

@mod_evaluacion.route("/exportarExcelEvaluacion/",methods=['GET'])
def exportarExcelEvaluacion():
  resultados = getReporteEvaluacion()
  proceso = getUltimoProceso()
  nombreFile = "Evaluación de Colaboradores (" + proceso.nombre + " - " + str(proceso.fecha) + ")"
  column_names = ['codigo', 'nombres', 'aula','cod_coord','es_coord','es_apoyo','es_asistente','hora_proceso','calificacion','obs_proceso']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name=nombreFile)

@mod_evaluacion.route("/exportarExcelReporte/",methods=['GET'])
def exportarExcelReporte():
  resultados = getReporte()
  column_names = ['codigo', 'nombres', 'nombre','calificacion','obs_proceso','nro_convocatorias','nro_asistencias','correo']
  return excel.make_response_from_query_sets(resultados, column_names, "xls",file_name="Reporte General")

@mod_evaluacion.route("/reporte/")
def reporte():
  #actualizarDatos()
  reg = getReporteControladores()
  return render_template("reporte.tpl.html",registros = reg)

@mod_evaluacion.route("/importar/",methods=['GET', 'POST'])
def importar():
  reg = getReporteControladores()
  
  if request.method == 'POST':
    def person_init_func(row):
      p = Persona(nombres = row['nombres'])
      p.codigo = row['codigo'];
      return p

    def labor_init_func(row):
      p = Persona.query.filter_by(codigo=row['codigo']).first()
      l = LaborPorProceso(codigo = p.codigo,idproceso = row['idproceso'],aula =  row['aula'],cod_coord = row['cod_coord'])
      return l

    request.get_dict(field_name='file')
    
    return render_template("reporte.tpl.html",registros = reg)
  return render_template("importar.tpl.html")

@mod_evaluacion.route("/procesarJSON/",methods=["POST"])
def procesarJSON():
  codigo = request.form.get('codigo', '')
  calificacion = request.form.get('calificacion', '')
  observaciones = request.form.get('observaciones', '')
  #print(codigo[1] + " " + calificacion[1] + " " +observaciones[1])
  controlador = getControlador(codigo)
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
  controlador = getControlador(codigo)
  if controlador is not None:
    #print(controlador.codigo)
    controlador.obs_capacitacion = observaciones
    db.session.commit()
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)


@mod_evaluacion.route("/procesarJSONAsist/",methods=["POST"])
def procesarJSONAsist():
  codigo = request.form.get('codigo', '')
  asistencia = request.form.get('asistencia', '')
  controlador = getControlador(codigo)
  if controlador is not None:
    #print(controlador.codigo)
    #print(codigo + " " + asistencia)
    if(asistencia == "true"):
      controlador.hora_proceso = datetime.now().time()
    elif (asistencia == "false"):
      controlador.hora_proceso = None
    db.session.commit()
    time.sleep(1)
    return json.dumps(True)
  else:
    #print("No se encontró el Controlador")
    return json.dumps(False)

@mod_evaluacion.route("/procesarJSONAsistCap/",methods=["POST"])
def procesarJSONAsistCap():
  codigo = request.form.get('codigo', '')
  asistencia = request.form.get('asistencia', '')
  controlador = getControlador(codigo)
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

@mod_evaluacion.route("/buscarCoordinador/",methods=["GET"])
def buscarCoordinador():
  codigo = request.form.get('codigo', '')
  nombre = getCoordinador(codigo)
  if nombre is not None:
    return nombre
  else:
    return -1

@mod_evaluacion.route("/evaluacion/")
def evaluacion():
  reg = getTodo()
  asist = getAsistentes()
  apoyos = getApoyo()
  coordinadores = getCoordinadoresUltimoProceso()
  return render_template("evaluacion.tpl.html",registros = reg,asistentes = asist, apoyos = apoyos,coordinadores = coordinadores)

@mod_evaluacion.route("/01X9jK6g/")
def asistencia():
  reg = getTodo()
  asist = getAsistentes()
  apoyo = getApoyo()
  return render_template("asistencia.tpl.html",registros = reg,asistentes = asist,apoyos = apoyo)

@mod_evaluacion.route("/asistencia/")
def asistencia2():
  reg = getControladoresCapacitacion()
  asist = getAsistentes()
  apoyo = getApoyo()
  aulas = getAulas()
  return render_template("asistencia2.tpl.html",registros = reg,asistentes = asist,apoyos = apoyo,aulas = aulas)

@mod_evaluacion.route('/verControlador/<codigo>')
def verControlador(codigo=None):
    if (codigo == None):
      return render_template('Error.html', codigo=codigo)
    else:
      reg = obtenerControlador(codigo)
      procesos = obtenerProcesosControlador(codigo)
      return render_template('controlador_view.tpl.html',registro=reg,procesos=procesos)

def getCoordinadoresUltimoProceso():
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,LaborPorProceso.idproceso==Proceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.password,
    )
    .filter(
      and_(Proceso.es_ultimo == 1,
      LaborPorProceso.es_coord == 1)
    )
  )
  return joinQuery

def obtenerControlador(codigo):
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      Persona.nro_asistencias,
      Persona.nro_convocatorias,
      Persona.correo,
    )
    .filter(
      Persona.codigo == codigo,
    )
  )
  return joinQuery.first()

def obtenerProcesosControlador(codigo):
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Proceso.nombre,
      Proceso.fecha,
      Proceso.fecha_cap,
      LaborPorProceso.aula_capacitacion,
      LaborPorProceso.hora_capacitacion,
      LaborPorProceso.obs_capacitacion,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_coord,
      LaborPorProceso.aula,
    )
    .filter(
      Persona.codigo == codigo,
    )
  )
  return joinQuery

def getCoordinador(codigo):
  query = Persona.query.filter_by(codigo=codigo).first()
  #return joinQuery.all()
  if query:
      return query.nombre
  else:
    return None

def getControlador(codigo):
  joinQuery = LaborPorProceso.query.join(Proceso,LaborPorProceso.idproceso==Proceso.idproceso)
  joinQuery = joinQuery.filter(
                and_(LaborPorProceso.codigo == codigo,
                Proceso.es_ultimo == 1)
              )              
  return joinQuery.first()

def getControladores():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.aula,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_capacitacion,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_coord,
      LaborPorProceso.aula_capacitacion,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.hora_capacitacion,
    )
    .filter(
      and_(Proceso.fecha == datetime.now().date(),
      LaborPorProceso.es_coord == 0,
      LaborPorProceso.es_apoyo == 0,
      LaborPorProceso.es_asistente == 0)
    )
  )
  return joinQuery

def getControladoresCapacitacion():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso==LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.aula,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_capacitacion,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_coord,
      LaborPorProceso.aula_capacitacion,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.hora_capacitacion,
      LaborPorProceso.es_apoyo,
      LaborPorProceso.es_asistente,
      LaborPorProceso.es_coord,
    )
    .filter(
      and_(Proceso.es_ultimo == 1)
    )
  )
  return joinQuery


def getReporteAsistencia():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso==LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_capacitacion,
      LaborPorProceso.hora_capacitacion,
      LaborPorProceso.obs_capacitacion,
    )
    .filter(
      and_(Proceso.es_ultimo == 1,
      LaborPorProceso.es_coord == 0,
      LaborPorProceso.es_apoyo == 0,
      LaborPorProceso.es_asistente == 0)
    )
  )
  return joinQuery.all()

def getReporteEvaluacion():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.aula,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_coord,
      LaborPorProceso.es_coord,
      LaborPorProceso.es_apoyo,
      LaborPorProceso.es_asistente,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso,
    )
    .filter(
      and_(Proceso.es_ultimo == 1,
      LaborPorProceso.cod_coord != "")
    )
  )
  return joinQuery.all()

def getReporte():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      Proceso.nombre,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso,
      Persona.nro_convocatorias,
      Persona.nro_asistencias,
      Persona.correo
    )
    .filter(
      and_(LaborPorProceso.es_coord == 0,
      LaborPorProceso.es_apoyo == 0,
      LaborPorProceso.es_asistente == 0)
    )
  )
  return joinQuery.all()


def getReporteControladores():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.calificacion,
      LaborPorProceso.idproceso,
      Proceso.nombre,
      Persona.nro_convocatorias,
      Persona.nro_asistencias,
      Persona.correo,
    )
    .filter(
      and_(LaborPorProceso.es_coord == 0,
      LaborPorProceso.es_apoyo == 0,
      LaborPorProceso.es_asistente == 0)
    )
  )
  return joinQuery

def getAulas():
  query = LaborPorProceso.query.join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso).distinct(LaborPorProceso.aula_capacitacion).group_by(LaborPorProceso.aula_capacitacion).filter(Proceso.es_ultimo == 1)
  return query

def getAsistentes():
  dt = datetime.now()

  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo == Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.cod_coord,
    )
    .filter(
      and_(Proceso.es_ultimo == 1,
      LaborPorProceso.es_asistente == 1)
      )
  )
  return joinQuery

def getApoyo():
  dt = datetime.now()

  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo == Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.cod_coord,
    )
    .filter(
      and_(Proceso.es_ultimo == 1,
      LaborPorProceso.es_apoyo == 1)
      )
  )
  return joinQuery

def getTodo():
  dt = datetime.now()
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      LaborPorProceso.aula,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso,
      LaborPorProceso.cod_coord,
      LaborPorProceso.aula_coord,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.fecha_proceso,
      LaborPorProceso.es_coord,
      LaborPorProceso.es_apoyo,
      LaborPorProceso.es_asistente,
      Proceso.es_ultimo,
    )
    .filter(
      Proceso.es_ultimo == 1
    )
  )
  return joinQuery

def getAsistenciaTodosLosControladores():
  joinQuery = Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo)
  joinQuery = joinQuery.filter(
                and_(LaborPorProceso.es_coord == 0,
                LaborPorProceso.es_apoyo == 0,
                LaborPorProceso.es_asistente == 0, 
                LaborPorProceso.hora_proceso.isnot(None),)
              )
  return joinQuery

def getConvocatoriaTodosLosControladores():
  joinQuery = Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo)
  joinQuery = joinQuery.filter(
                and_(LaborPorProceso.es_coord == 0,
                LaborPorProceso.es_apoyo == 0,
                LaborPorProceso.es_asistente == 0)
              )
  return joinQuery

def getUltimoProceso():
  query = Proceso.query.filter_by(es_ultimo=1).first()
  return query


def actualizarDatos():
  controladores = getAsistenciaTodosLosControladores()
  print("query 1")
  #controlador = query.getAsDictEval(1)
  for controlador in controladores:
    controlador.nro_asistencias = controlador.nro_asistencias + 1

  controladores = getConvocatoriaTodosLosControladores()
  for controlador in controladores:
    controlador.nro_convocatorias = controlador.nro_convocatorias + 1
  db.session.commit()
  #controlador['persona']['nro_convocatorias'] = controlador['persona']['nro_convocatorias'] + 1
  #if(controlador['calificacion'] != "0"):
  #  controlador['persona']['nro_asistencias'] = controlador['persona']['nro_asistencias'] + 1


"""
def getRegistroAsistencia(codigo):
  joinQuery = RegistroAsistencia.query.join(Colegio,RegistroAsistencia.codigo==Colegio.codigo)
  joinQuery = joinQuery.filter(
                or_(Colegio.codigo==codigo),
                #RegistroAsistencia.fecha == datetime.now().date()
              )
  return joinQuery.first()

def getAsistencia():
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Controlador.query.join(RegistroAsistencia,RegistroAsistencia.codigo==Colegio.codigo)
    .add_columns(
      Controlador.codigo,
      Controladr.nombre,
      Controlador.aula
      Proceso.nombre,
      Proceso.fecha
    )
    .filter(
      Proceso.fecha = datetime.now()
    )
  )
  return joinQuery
 """