from flask import Flask, request, render_template, Blueprint, redirect, url_for
import flask_excel as excel
import xlrd
from models.Controlador import Persona, Proceso, LaborPorProceso
from datetime import datetime
from app import db
from sqlalchemy import or_, and_
import json
import time

#################################################################################
### EN ESTA LIBRERIA SE ENCUENTRAN LAS FUNCIONES QUE DEVUELVEN SOLO UN VALOR. ###
#################################################################################

def getPersonaSola(codigo):
  query = Persona.query.filter_by(codigo=codigo).first()
  return query

def getPersonaEditar(codigo,proceso):
  joinQuery = LaborPorProceso.query.join(Proceso,LaborPorProceso.idproceso==Proceso.idproceso)
  joinQuery = joinQuery.filter(
                and_(LaborPorProceso.codigo == codigo,
                    LaborPorProceso.idproceso == proceso)
              )              
  return joinQuery.first()

def getControlador(codigo):
  joinQuery = LaborPorProceso.query.join(Proceso,LaborPorProceso.idproceso==Proceso.idproceso)
  joinQuery = joinQuery.filter(
                and_(LaborPorProceso.codigo == codigo,
                Proceso.es_ultimo == 1)
              )              
  return joinQuery.first()

def obtenerControladorPorProceso(codigo,idproceso=0):
  #consultar bd y devolver data de la forma
  joinQuery = (
    Persona.query.join(LaborPorProceso,LaborPorProceso.codigo==Persona.codigo).join(Proceso,Proceso.idproceso == LaborPorProceso.idproceso)
    .add_columns(
      Persona.codigo,
      Persona.nombres,
      Persona.nro_asistencias,
      Persona.nro_convocatorias,
      Persona.correo,
      Proceso.nombre,
      LaborPorProceso.es_coord,
      LaborPorProceso.idproceso,
      LaborPorProceso.es_apoyo,
      LaborPorProceso.es_asistente,
      LaborPorProceso.aula,
      LaborPorProceso.aula_coord,
      LaborPorProceso.cod_coord,
      LaborPorProceso.calificacion,
      LaborPorProceso.obs_proceso
    ))

  if(idproceso == 0):
    joinQuery = joinQuery.filter(
                      Persona.codigo == codigo)
  else:
    joinQuery = joinQuery.filter(
                     and_(Persona.codigo == codigo,
                          LaborPorProceso.idproceso == idproceso))

  return joinQuery.first()