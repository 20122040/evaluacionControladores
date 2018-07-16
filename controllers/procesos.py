from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
import xlrd
from models.Controlador import Persona, Proceso, LaborPorProceso
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
import json
import time

#########################################################################################
### EN ESTA LIBRERIA SE ENCUENTRAN LAS FUNCIONES QUE HACEN QUERYS A LA TABLA PROCESO. ###
#########################################################################################

def obtenerProcesos():
  query = Proceso.query.add_columns(
      Proceso.nombre,
      Proceso.idproceso,
      Proceso.fecha,
      Proceso.es_ultimo
    )
  return query

def getCantidadProcesos():
  return Proceso.query.count()

def getUltimoProceso():
  query = Proceso.query.filter_by(es_ultimo=1).first()
  return query

def getProcesoPorId(idproceso):
  query = Proceso.query.filter_by(idproceso=idproceso).first()
  return query

def obtenerProcesosControlador(codigo):
  #consultar bd y devolver data de la forma
  joinQuery = (
    LaborPorProceso.query.join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
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
      LaborPorProceso.codigo == codigo,
    )
  )
  return joinQuery