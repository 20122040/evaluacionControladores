from app import db

class Persona(db.Model):
  codigo = db.Column(db.String(8), primary_key=True)
  nombres = db.Column(db.String(255))
  correo = db.Column(db.String(255))
  nro_convocatorias = db.Column(db.Integer)
  nro_asistencias = db.Column(db.Integer)
  procesos = db.relationship('LaborPorProceso',backref='persona',lazy='dynamic')

  def __init__(self,codigo,nombre,correo,nro_asistencias,nro_convocatorias):
    self.codigo = codigo
    self.nombres = nombre
    self.correo = correo
    self.nro_convocatorias = nro_convocatorias
    self.nro_asistencias = nro_asistencias

  def __repr__(self):
    return '<Persona %r>' % self.nombres
    
  def getAsDict(self,rel_level=0):
    result = {}
    result["codigo"]=self.codigo
    result["nombres"]=self.nombres
    result["correo"] = self.correo
    result["nro_convocatorias"] = self.nro_convocatorias
    result["nro_asistencias"] = self.nro_asistencias
    if rel_level > 0:
      result["procesos"] = [a.getAsDict(rel_level-1) for a in self.procesos]
    return result


class Proceso(db.Model):
  idproceso = db.Column(db.Integer,primary_key=True)
  nombre = db.Column(db.String(255))
  fecha = db.Column(db.Date)
  fecha_cap = db.Column(db.Date)
  es_ultimo = db.Column(db.Integer)
  personas = db.relationship('LaborPorProceso',backref='proceso',lazy='dynamic')

  def __init__(self,nombre,fecha,fecha_cap,es_ultimo):
    self.nombre = nombre
    self.fecha = fecha
    self.fecha_cap = fecha_cap
    self.es_ultimo = es_ultimo

  def __repr__(self):
    return '<Proceso %r>' % self.nombre
  
  def getAsDict(self,rel_level=0):
    result={}
    result["idproceso"] = self.idproceso
    result["nombre"] = self.nombre
    result["fecha"] = str(self.fecha)
    result["fecha_cap"] = str(self.fecha_cap)
    result["es_ultimo"] = self.es_ultimo
    if rel_level > 0:
      result["personas"] = [a.getAsDict(rel_level-1) for a in self.personas]
    return result

class LaborPorProceso(db.Model):
  id_lxp = db.Column(db.Integer,primary_key=True)
  codigo = db.Column(db.String(8), db.ForeignKey('persona.codigo'))#en Foreign key se usa el nombre de la tabla
  idproceso = db.Column(db.Integer,db.ForeignKey('proceso.idproceso'))#en Foreign key se usa el nombre de la tabla
  es_coord = db.Column(db.Integer)
  es_apoyo = db.Column(db.Integer)
  es_asistente = db.Column(db.Integer)
  aula = db.Column(db.String(10))
  aula_coord = db.Column(db.String(10))
  aula_capacitacion = db.Column(db.String(10))
  fecha_proceso = db.Column(db.Date)
  fecha_capacitacion = db.Column(db.Date)
  hora_proceso = db.Column(db.Time)
  hora_capacitacion = db.Column(db.Time)
  cod_coord = db.Column(db.String(8))
  calificacion = db.Column(db.String(10))
  obs_proceso = db.Column(db.String(255))
  obs_capacitacion = db.Column(db.String(255))
  obs_coordinacion = db.Column(db.String(255))
  password = db.Column(db.String(255))

  def __init__(self,codigo,idproceso,es_coord,es_apoyo,es_asistente,aula,aula_coord,aula_capacitacion,fecha_proceso,
              fecha_capacitacion,hora_proceso,hora_capacitacion,cod_coord,calificacion,obs_proceso,obs_capacitacion,obs_coordinacion,password):
    self.codigo = codigo
    self.idproceso = idproceso
    self.es_coord = es_coord
    self.es_apoyo = es_apoyo
    self.es_asistente = es_asistente
    self.aula = aula
    self.aula_coord = aula_coord
    self.aula_capacitacion = aula_capacitacion
    self.fecha_proceso = fecha_proceso
    self.fecha_capacitacion = fecha_capacitacion
    self.hora_proceso = hora_proceso
    self.hora_capacitacion = hora_capacitacion
    self.cod_coord = cod_coord
    self.calificacion = calificacion
    self.obs_proceso = obs_proceso
    self.obs_capacitacion = obs_capacitacion
    self.obs_coordinacion = obs_coordinacion
    self.password = password

  def __repr__(self):
    return '<Controlador %r>' % self.codigo

  def getAsDictEval(self,rel_level=0):
    result={}
    result["codigo"] = self.codigo
    result["idproceso"] = self.idproceso
    result["es_coord"] = self.es_coord
    result["es_apoyo"] = self.es_apoyo
    result["es_asistente"] = self.es_asistente
    result["aula"] = self.aula
    result["aula_coord"] = self.aula_coord
    result["aula_capacitacion"] = self.aula_capacitacion
    result["fecha_proceso"] = self.fecha_proceso
    result["fecha_capacitacion"] = self.fecha_capacitacion
    result["hora_proceso"] = self.hora_proceso
    result["hora_capacitacion"] = self.hora_capacitacion
    result["cod_coord"] = self.cod_coord
    result["calificacion"] = self.calificacion
    result["obs_proceso"] = self.obs_proceso
    result["obs_capacitacion"] = self.obs_capacitacion
    result["obs_coordinacion"] = self.obs_coordinacion
    result["password"] = self.password
    if rel_level > 0:
      result["persona"] = self.persona.getAsDict(rel_level-1)
      result["proceso"] = self.proceso.getAsDict(rel_level-1)
    else:
      result["persona"] = self.codigo
      result["proceso"] = self.idproceso
    return result
