def writeToCoordinadores(writer,coordinadores_data):
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
    worksheet.write(row,1,str(cod).zfill(8))
    row+=1

  row = 4
  for fullname in coordinadores_data['Apellidos y nombres']:
    worksheet.write(row,2,fullname)
    row+=1

  row = 4
  for apellidoPaterno in coordinadores_data['Primer apellido']:
    worksheet.write(row,3,apellidoPaterno)
    row+=1

  row = 4
  for apellidoMaterno in coordinadores_data['Segundo apellido']:
    worksheet.write(row,4,apellidoMaterno)
    row+=1

  row = 4
  for names in coordinadores_data['Nombres']:
    worksheet.write(row,5,names)
    row+=1

  row = 4
  for labor in coordinadores_data['LABOR']:
    worksheet.write(row,6,labor)
    row+=1

  row = 4
  for piso in coordinadores_data['PISO']:
    worksheet.write(row,7,piso)
    row+=1

  row = 4
  for aula in coordinadores_data['AULA DE COORDINACIÓN']:
    worksheet.write(row,8,aula)
    row+=1

def writeToControladores(writer,controladores_data):
  header = ['N°','Código','Apellidos y Nombres','Primer Apellido','Segundo Apellido','Nombres','Labor','AULA EXAMEN','PISO','AULA DE COORDINACIÓN']
  bold = writer.add_format({'bold': True})

  worksheet = writer.add_worksheet('CONTROLADORES')
  col=0
  for h in header:
    worksheet.write(0,col,h,bold)
    col+=1

  row = 1
  for cod in controladores_data['Código']:
    worksheet.write(row,1,str(cod).zfill(8))
    row+=1

  row = 1
  for fullname in controladores_data['Apellidos y nombres']:
    worksheet.write(row,2,fullname)
    row+=1

  row = 1
  for apellidoPaterno in controladores_data['Primer apellido']:
    worksheet.write(row,3,apellidoPaterno)
    row+=1

  row = 1
  for apellidoMaterno in controladores_data['Segundo apellido']:
    worksheet.write(row,4,apellidoMaterno)
    row+=1

  row = 1
  for names in controladores_data['Nombres']:
    worksheet.write(row,5,names)
    row+=1

  row = 1
  for names in controladores_data['Nombres']:
    worksheet.write(row,6,names)
    row+=1

  row = 1
  for aula_examen in controladores_data['AULA']:
    worksheet.write(row,7,aula_examen)
    row+=1

  row = 1
  for piso in controladores_data['PISO']:
    worksheet.write(row,8,piso)
    row+=1

  row = 1
  for aula_coord in controladores_data['AULA DE COORDINACIÓN']:
    worksheet.write(row,9,aula_coord)
    row+=1

def writeToBaseParaExportar(writer,coordinadores_data,controladores_data):
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
    worksheet.write(row,0,str(cod).zfill(8))
    row+=1
    nCoordinadores+=1

  row = 1
  for apellidoPaterno in coordinadores_data['Primer apellido']:
    worksheet.write(row,1,apellidoPaterno)
    row+=1

  row = 1
  for apellidoMaterno in coordinadores_data['Segundo apellido']:
    worksheet.write(row,2,apellidoMaterno)
    row+=1
  
  row = 1
  for names in coordinadores_data['Nombres']:
    worksheet.write(row,3,names)
    row+=1

  row = 1
  for aula_examen in coordinadores_data['AULA DE COORDINACIÓN']:
    worksheet.write(row,4,aula_examen)
    row+=1

  row = 1
  for labor in coordinadores_data['LABOR']:
    if(labor in ['COORDINADOR DE PISO','COORDINADORA DE PISO']):
      worksheet.write(row,5,'VERDADERO') #Coord
      worksheet.write(row,8,'FALSO') #Apoyo
      worksheet.write(row,9,'FALSO') #Asistente
      codsCoord.append(str(coordinadores_data['Código'][row-1]).zfill(8))
      aulasCoord.append(coordinadores_data['AULA DE COORDINACIÓN'][row-1])
    elif (labor == 'APOYO COORDINACIÓN DE PISO'):
      worksheet.write(row,5,'FALSO') #Coord
      worksheet.write(row,8,'VERDADERO') #Apoyo
      worksheet.write(row,9,'FALSO') #Asistente
    elif (labor == 'ASISTENTE DE PISO'):
      worksheet.write(row,5,'FALSO') #Coord
      worksheet.write(row,8,'FALSO') #Apoyo
      worksheet.write(row,9,'VERDADERO') #Asistente
    row+=1

  row = 1
  for aula_coord in coordinadores_data['AULA DE COORDINACIÓN']:
    #Aquí se llenan las columnas 6 y 7 de Código de Coord y Aula de Coord
    i = aulasCoord.index(aula_coord)
    worksheet.write(row,6,codsCoord[i])
    worksheet.write(row,7,aula_coord)
    row+=1


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
    worksheet.write(row,1,apellidoPaterno)
    row+=1

  row = nCoordinadores + 1
  for apellidoMaterno in controladores_data['Segundo apellido']:
    worksheet.write(row,2,apellidoMaterno)
    row+=1
  
  row = nCoordinadores + 1
  for names in controladores_data['Nombres']:
    worksheet.write(row,3,names)
    row+=1

  row = nCoordinadores + 1
  for aula_examen in controladores_data['AULA']:
    worksheet.write(row,4,aula_examen)
    row+=1

  row = nCoordinadores + 1
  for aula_coord in controladores_data['AULA DE COORDINACIÓN']:
    #Aquí se llenan las columnas 6 y 7 de Código de Coord y Aula de Coord
    i = aulasCoord.index(aula_coord)
    worksheet.write(row,6,codsCoord[i])
    worksheet.write(row,7,aula_coord)
    row+=1
  #print(codsCoord)
  #print(aulasCoord)