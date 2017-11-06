from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
import xlrd
from models.Controlador import Persona, Proceso, LaborPorProceso
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
import json
import time

######################################################################################
### EN ESTA LIBRERIA SE ENCUENTRAN LAS FUNCIONES QUE SE USAN PARA EXPORTAR A EXCEL ###
######################################################################################

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
    ))

  joinQuery = joinQuery.filter(
                          and_(LaborPorProceso.es_coord == 0,
                          LaborPorProceso.es_apoyo == 0,
                          LaborPorProceso.es_asistente == 0))
  return joinQuery.all()