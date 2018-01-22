from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
import xlrd
from models.Controlador import Persona, Proceso, LaborPorProceso
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
import json
import time

###################################################################################
### AQUI SE ENCUENTRAN TODAS LAS FUNCIONES QUE HACEN CONSULTAS DE MUCHOS DATOS. ###
###################################################################################

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

def getReporteControladores(opt=0):
  dt = datetime.now()
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      Persona.correo,
      Persona.nro_convocatorias,
      Persona.nro_asistencias,
      Proceso.nombre,
      Proceso.es_ultimo,
      LaborPorProceso.idproceso,
      LaborPorProceso.aula,
      LaborPorProceso.aula_coord,
      LaborPorProceso.fecha_proceso,
      LaborPorProceso.hora_proceso,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso,
      LaborPorProceso.cod_coord,
      LaborPorProceso.es_coord,
      LaborPorProceso.es_apoyo,
      LaborPorProceso.es_asistente,
      LaborPorProceso.obs_coordinacion,
    ))
  if(opt==0):
    joinQuery = joinQuery.filter(
      and_(LaborPorProceso.es_coord == 0,
      LaborPorProceso.es_apoyo == 0,
      LaborPorProceso.es_asistente == 0))
  else:
    joinQuery = joinQuery.filter(Proceso.es_ultimo == 1)

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

def getAllWorkers():
  return Persona.query.add_columns(
      Persona.codigo,
      Persona.nombres,
      Persona.correo,
      Persona.nro_convocatorias,
      Persona.nro_asistencias,
    )