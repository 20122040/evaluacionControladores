def isNaN(num):
  return num!=num

def writeToCoordinadores(writer,coordinadores_data,errores,opt=0):
  header = ['N°','Código','Apellidos y Nombres','Apellido Paterno','Apellido Materno','Nombre','Labor','Piso','Aula de Coordinación']
  bold = writer.add_format({'bold': True})

  worksheet = writer.add_worksheet('COORDINADORES')
  worksheet.write('A1','COORDINADORES Y ASISTENTES DE PABELLÓN',bold)
  col=0
  for h in header:
    worksheet.write(3,col,h,bold)
    col+=1

  row = 4
  for cod in coordinadores_data['Código']:
    if(isNaN(cod)):
      if(opt==1):
        errores.append("Hay un Coordinador sin código")
      return
    else:
      worksheet.write(row,1,str(cod).zfill(8))
      row+=1

  row = 4
  for fullname in coordinadores_data['Apellidos y nombres']:
    if(isNaN(fullname)):
      worksheet.write(row,2,'-')
      row+=1
    else:
      worksheet.write(row,2,fullname)
      row+=1

  row = 4
  for apellidoPaterno in coordinadores_data['Primer apellido']:
    if(isNaN(apellidoPaterno)):
      worksheet.write(row,3,'-')
      row+=1
    else:
      worksheet.write(row,3,apellidoPaterno)
      row+=1

  row = 4
  for apellidoMaterno in coordinadores_data['Segundo apellido']:
    if(isNaN(apellidoMaterno)):
      worksheet.write(row,4,'-')
      row+=1
    else:
      worksheet.write(row,4,apellidoMaterno)
      row+=1

  row = 4
  for names in coordinadores_data['Nombres']:
    if(isNaN(names)):
      worksheet.write(row,5,'-')
      row+=1
    else:
      worksheet.write(row,5,names)
      row+=1

  row = 4
  for labor in coordinadores_data['LABOR']:
    if(isNaN(labor)):
      errores.append("Hay un coordinador sin labor")
      return
    else:
      worksheet.write(row,6,labor)
      row+=1

  row = 4
  for piso in coordinadores_data['PISO']:
    if(isNaN(piso)):
      worksheet.write(row,7,'-')
      row+=1
    else:
      worksheet.write(row,7,piso)
      row+=1

  row = 4
  for aula in coordinadores_data['AULA DE COORDINACIÓN']:
    if(isNaN(aula)):
      errores.append("Hay un coordinador sin aula de coordinación")
      return
    else:
      worksheet.write(row,8,aula)
      row+=1

def writeToControladores(writer,controladores_data,errores,opt=0):
  header = ['N°','Código','Apellidos y Nombres','Primer Apellido','Segundo Apellido','Nombres','Labor','AULA EXAMEN','PISO','AULA DE COORDINACIÓN']
  bold = writer.add_format({'bold': True})

  worksheet = writer.add_worksheet('CONTROLADORES')
  col=0
  for h in header:
    worksheet.write(0,col,h,bold)
    col+=1

  row = 1
  for cod in controladores_data['Código']:
    if(isNaN(cod)):
      if(opt==1):
        errores.append("Hay un Controlador sin código")
      return
    else:
      worksheet.write(row,1,str(cod).zfill(8))
      row+=1

  row = 1
  for fullname in controladores_data['Apellidos y nombres']:
    if(isNaN(fullname)):
      worksheet.write(row,2,'-')
      row+=1
    else:
      worksheet.write(row,2,fullname)
      row+=1

  row = 1
  for apellidoPaterno in controladores_data['Primer apellido']:
    if(isNaN(apellidoPaterno)):
      worksheet.write(row,3,'-')
      row+=1
    else:
      worksheet.write(row,3,apellidoPaterno)
      row+=1

  row = 1
  for apellidoMaterno in controladores_data['Segundo apellido']:
    if(isNaN(apellidoMaterno)):
      worksheet.write(row,4,'-')
      row+=1
    else:
      worksheet.write(row,4,apellidoMaterno)
      row+=1

  row = 1
  for names in controladores_data['Nombres']:
    if(isNaN(names)):
      worksheet.write(row,5,'-')
      row+=1
    else:
      worksheet.write(row,5,names)
      row+=1

  row = 1
  for aula_examen in controladores_data['AULA']:
    if(isNaN(aula_examen)):
      errores.append("Un controlador no tiene aula de examen asignada")
      return
    else:
      worksheet.write(row,7,aula_examen)
      row+=1

  row = 1
  for piso in controladores_data['PISO']:
    if(isNaN(piso)):
      worksheet.write(row,8,"-")
      row+=1
    else:
      worksheet.write(row,8,piso)
      row+=1

  row = 1
  for aula_coord in controladores_data['AULA DE COORDINACIÓN']:
    if (isNaN(aula_coord)):
      errores.append('No se podrá generar la base para Access sin haber corregido los errores.')
      return
    else:
      worksheet.write(row,9,aula_coord)
      row+=1

def writeToBaseParaExportar(writer,coordinadores_data,controladores_data,errores):
  header = ['Código','Apellido Paterno','Apellido Materno','Nombres','Aula','Es coordinador','codigo Coordinador','Aula coordinación','Apoyo OCAI','Asistente OCAI']
  bold = writer.add_format({'bold': True})

  aulasCoord = []
  codsCoord = []

  worksheet = writer.add_worksheet('PARA EXPORTAR')
  col=0
  for h in header:
    worksheet.write(0,col,h,bold)
    col+=1

  ##################################################
  #    Primero se escribiran los COORDINADORES     #
  ##################################################
  nCoordinadores = 0
  row = 1
  for cod in coordinadores_data['Código']:
    if(isNaN(cod)):
      errores.append("No se pudo generar el access")
      return
    else:
      worksheet.write(row,0,str(cod).zfill(8))
      row+=1
      nCoordinadores+=1

  row = 1
  for apellidoPaterno in coordinadores_data['Primer apellido']:
    if(isNaN(apellidoPaterno)):
      worksheet.write(row,1,'-')
      row+=1
    else:
      worksheet.write(row,1,apellidoPaterno)
      row+=1

  row = 1
  for apellidoMaterno in coordinadores_data['Segundo apellido']:
    if(isNaN(apellidoMaterno)):
      worksheet.write(row,2,'-')
      row+=1
    else:
      worksheet.write(row,2,apellidoMaterno)
      row+=1

  row = 1
  for names in coordinadores_data['Nombres']:
    if(isNaN(names)):
      worksheet.write(row,3,'-')
      row+=1
    else:
      worksheet.write(row,3,names)
      row+=1

  row = 1
  for aula_examen in coordinadores_data['AULA DE COORDINACIÓN']:
    if(isNaN(aula_examen)):
      errores.append("No se podrá generar la base para Access sin haber corregido los errores.")
      return
    else:
      worksheet.write(row,4,aula_examen)
      row+=1

  row = 1
  for labor in coordinadores_data['LABOR']:
    if('COORDINADOR' in labor):
      worksheet.write(row,5,'VERDADERO') #Coord
      worksheet.write(row,8,'FALSO') #Apoyo
      worksheet.write(row,9,'FALSO') #Asistente
      codsCoord.append(str(coordinadores_data['Código'][row-1]).zfill(8))
      aulasCoord.append(coordinadores_data['AULA DE COORDINACIÓN'][row-1])
    elif ('APOYO' in labor):
      worksheet.write(row,5,'FALSO') #Coord
      worksheet.write(row,8,'VERDADERO') #Apoyo
      worksheet.write(row,9,'FALSO') #Asistente
    elif ('ASISTENTE' in labor):
      worksheet.write(row,5,'FALSO') #Coord
      worksheet.write(row,8,'FALSO') #Apoyo
      worksheet.write(row,9,'VERDADERO') #Asistente
    row+=1

  row = 1
  for aula_coord in coordinadores_data['AULA DE COORDINACIÓN']:
    #Aquí se llenan las columnas 6 y 7 de Código de Coord y Aula de Coord
    if(isNaN(aula_coord)):
      errores.append("No se podrá generar la base para Access sin haber corregido los errores.")
      return
    else:    
      i = aulasCoord.index(aula_coord)
      if(i>=0):
        worksheet.write(row,6,codsCoord[i])
        worksheet.write(row,7,aula_coord)
        row+=1
      else:
        errores.append("No hay aula de coordinación disponible para este Asistente/Apoyo OCAI")


  ##################################################
  #     Ahora se escribiran los CONTROLADORES      #
  ##################################################
  row = nCoordinadores + 1
  for cod in controladores_data['Código']:
    worksheet.write(row,0,str(cod).zfill(8))
    #Aquí todos tienen estos campos como FALSO
    worksheet.write(row,5,'FALSO') #Coord
    worksheet.write(row,8,'FALSO') #Apoyo
    worksheet.write(row,9,'FALSO') #Asistente
    row+=1

  row = nCoordinadores + 1
  for apellidoPaterno in controladores_data['Primer apellido']:
    if(isNaN(apellidoPaterno)):
      worksheet.write(row,1,'-')
      row+=1
    else:
      worksheet.write(row,1,apellidoPaterno)
      row+=1

  row = nCoordinadores + 1
  for apellidoMaterno in controladores_data['Segundo apellido']:
    if(isNaN(apellidoMaterno)):
      worksheet.write(row,2,'-')
      row+=1
    else:
      worksheet.write(row,2,apellidoMaterno)
      row+=1
  
  row = nCoordinadores + 1
  for names in controladores_data['Nombres']:
    if(isNaN(names)):
      worksheet.write(row,3,'-')
      row+=1
    else:
      worksheet.write(row,3,names)
      row+=1

  row = nCoordinadores + 1
  for aula_examen in controladores_data['AULA']:
    if(isNaN(aula_examen)):
      errores.append("No se podrá generar la base para Access sin haber corregido los errores.")
      return
    else:
      worksheet.write(row,4,aula_examen)
      row+=1

  row = nCoordinadores + 1
  for aula_coord in controladores_data['AULA DE COORDINACIÓN']:
    #Aquí se llenan las columnas 6 y 7 de Código de Coord y Aula de Coord
    if (isNaN(aula_coord)):
      errores.append("No se podrá generar la base para Access sin haber corregido los errores.")
      return
    else:
      i = aulasCoord.index(aula_coord)
      if(i>=0):
        worksheet.write(row,6,codsCoord[i])
        worksheet.write(row,7,aula_coord)
        row+=1
      else:
        errores.append("Hay un controlador sin aula de coordinación definida en la pestaña Coordinadores")
  #print(codsCoord)
  #print(aulasCoord)