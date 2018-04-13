"""
Script Name:  Script_UPRA_grouping_polygons_cumulative magnitude
Source Name: Cod_UPRA_grouping_polygons_cumulative magnitude.py
Version: ArcGIS 10.3 or ArcGIS 10.4
Author: Carlos Javier Delgado - UPRA - Grupo TIC - Analisis de Informacion
This script allows grouping of polygons as a cumulative magnitude of
a field and maximum value set by the user
Generalization
"""
#Importing modules
import arcpy,os,time,exceptions
arcpy.env.overwriteOutput = True

try:
	#Capture parameters entered by the user
	pGDBBorrador = arcpy.GetParameterAsText(0)
	pGDBFinal = arcpy.GetParameterAsText(1)
	pFeatureClassInicial = arcpy.GetParameterAsText(2)
	pFieldSeleccionado = arcpy.GetParameterAsText(3)
	pValorMaximo = arcpy.GetParameterAsText(4).replace(",",".")

	def principal():
		"""Funcion Principal"""
		capaFeatureInicial = arcpy.SearchCursor(pFeatureClassInicial)
		valoresTotalesCampo = []
		for m in capaFeatureInicial:
			valoresTotalesCampo.append(m.getValue(pFieldSeleccionado))

		if float(pValorMaximo) < float(min(valoresTotalesCampo)):
			arcpy.AddError("The maximum grouping value set by the user is less than the minimum value of the selected field. In this case the minimum value is " + str(min(valoresTotalesCampo)))
			arcpy.AddWarning("The grouping value must be greater than " + str(max(valoresTotalesCampo)))
		elif float(pValorMaximo) < float(max(valoresTotalesCampo)):
			arcpy.AddError("The maximum value set by the user grouping is less than the maximum value of the selected field. In this case the maximum value is " + str(max(valoresTotalesCampo)))
			arcpy.AddWarning("The grouping value must be greater than " + str(max(valoresTotalesCampo)))
		elif pGDBBorrador == pGDBFinal:
			arcpy.AddError("The GDB of partial data must be different to GDB of resulting final data.")
		else:
			valorInicial = 0
			rutasBloquesInteres = []
			generacionCopia(pGDBFinal,pFeatureClassInicial)
			funcionGeneracionGrupos(pGDBBorrador,pGDBFinal,pFeatureClassInicial,pFieldSeleccionado,valorInicial,pValorMaximo,rutasBloquesInteres)

	def generacionCopia(GDBFinal, fcInicial):
		"""Funcion auxiliar para generar una copia del Feature inicial"""
		copia_Original = GDBFinal +  "\\Union_Bloques_Grupos"
		arcpy.CopyFeatures_management(fcInicial, copia_Original, "", "0", "0", "0")
		arcpy.AddField_management(copia_Original, "Groups", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")			
			
			
	def funcionGeneracionGrupos(GDBBorrador,GDBFinal,fcInicial,campoSumatoria,valInicial,areaMax,aRutasFinales):
		"""Funcion para generar los poligonos extremos de la zona de estudio para empezar a radiar las zonas"""
		arcpy.env.workspace = GDBBorrador
		arcpy.env.overwriteOutput = 1
		dissolveZona = GDBBorrador + "\\Dissolve_Zona"
		poligonoLimiteDissolve = GDBBorrador + "\\Poligono_Limite_Dissolve"
		poligonoLimiteDissolveLay = "Poligono_Limite_Dissolve_Lay"
		laMesaLayer = "La_Mesa_Layer"
		poligonosExtremosTotales = GDBBorrador + "\\Poligonos_Extremos_Totales"
		poligonoPartida = GDBBorrador + "\\Poligono_Partida"
		tablaPruebaEstadisticas = GDBBorrador + "\\tabla_Prueba_Estadisticas"
		tablaEstadisticasFinalBloque = GDBBorrador + "\\tabla_Estadisticas_Final_Bloque"
		copia_Original = GDBFinal +  "\\Union_Bloques_Grupos"
		copia_Original_FL = "copia_Original_FL"
		
		#Adding identifier field and calculate the OBJECT ID
		arcpy.AddField_management(fcInicial, "Identificador", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
		arcpy.CalculateField_management(fcInicial, "Identificador", "!OBJECTID!", "PYTHON_9.3", "")
		#Add field to run dissolve and their respective calculation
		arcpy.AddField_management(fcInicial, "Campo_Dissolve", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
		arcpy.CalculateField_management(fcInicial, "Campo_Dissolve", "\"Dissolve\"", "PYTHON_9.3", "")
		#Feature Layer creation of the initial layer
		arcpy.MakeFeatureLayer_management(fcInicial, laMesaLayer, "", "", "")
		#Dissolve execution of the general area
		arcpy.Dissolve_management(fcInicial, dissolveZona, "Campo_Dissolve", "", "MULTI_PART", "DISSOLVE_LINES")
		#Minimum Bounding Geometry execution for the previously calculated Dissolve
		arcpy.MinimumBoundingGeometry_management(dissolveZona, poligonoLimiteDissolve, "CONVEX_HULL", "NONE", "", "MBG_FIELDS")
		#Feature Layer creation of geometry generated in the Minimum Bounding Geometry
		arcpy.MakeFeatureLayer_management(poligonoLimiteDissolve, poligonoLimiteDissolveLay, "", "", "")
		#Selection by location of polygons individually they are playing the geometry surrounding the initial zone
		arcpy.SelectLayerByLocation_management(laMesaLayer, "BOUNDARY_TOUCHES", poligonoLimiteDissolveLay, "", "NEW_SELECTION")
		arcpy.CopyFeatures_management(laMesaLayer, poligonosExtremosTotales, "", "0", "0", "0")

		#Process to set the cursor and arrangements starting polygon and other extreme polygons in the first iteration
		arcpy.Select_analysis(poligonosExtremosTotales, poligonoPartida, "OBJECTID = 1")
		#capaPuntoPartida = arcpy.SearchCursor(poligonoPartida)
		#capaPuntosTotalesPartida = arcpy.SearchCursor(poligonosExtremosTotales)
		#idPuntoPartida = []
		#poligonosTotalesPartida = []
		'''for g in capaPuntoPartida:
			idPuntoPartida.append(g.getValue("Identificador"))
			
		for g in capaPuntosTotalesPartida:
			poligonosTotalesPartida.append(g.getValue("Identificador"))'''
		
		idPuntoPartida = [row[0] for row in arcpy.da.SearchCursor(poligonoPartida, "Identificador")]
		poligonosTotalesPartida = [row[0] for row in arcpy.da.SearchCursor(poligonosExtremosTotales, "Identificador")]
				
		indiceOperadores = []
		#Flag iteration
		alternador = 0

		#Cyclical for the establishment of initial processing zones - Starts iteration
		for i in range(len(poligonosTotalesPartida)):
		
			#Iteration counter
			#arcpy.AddMessage("Iteration " + str(i))
			poligonosGeneradosIteracion = GDBBorrador + "\\Bloque_Grupo" + str(i)
			poligonosGeneradosIteracionFinal = GDBFinal + "\\Bloque_Grupo" + str(i + valInicial)
			if alternador == 0:
				#First iteration process
				alternador = 1
				arcpy.SelectLayerByAttribute_management(laMesaLayer, "NEW_SELECTION", "Identificador = "+str(poligonosTotalesPartida[i]))
				arcpy.SelectLayerByLocation_management(laMesaLayer, "BOUNDARY_TOUCHES", "", "", "ADD_TO_SELECTION")
				arcpy.Statistics_analysis(laMesaLayer, tablaPruebaEstadisticas, campoSumatoria + " SUM", "Identificador")
				#infoTabla1 = arcpy.SearchCursor(tablaPruebaEstadisticas)
				#infoTabla3 = arcpy.SearchCursor(tablaPruebaEstadisticas,"Identificador = "+str(poligonosTotalesPartida[i]))
				sumaAreas = []
				codigos = []
				areas = []
				valorAreaPoligonoInicial = 0
				'''for f in infoTabla1:
					sumaAreas.append(f.getValue("SUM_"+campoSumatoria))'''
				
				sumaAreas = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_"+campoSumatoria)]
				valorSumaTotal = sum(sumaAreas)
				valorAreaPoligonoInicial = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_"+campoSumatoria, where_clause="Identificador = "+str(poligonosTotalesPartida[i]))]
				
				'''for l in infoTabla3:
					valorAreaPoligonoInicial = l.getValue("SUM_" + campoSumatoria)'''
				
				#arcpy.AddMessage("Polygon base value: " + str(valorAreaPoligonoInicial))	
				valorInicial = valorSumaTotal
				diferenciaValores = 1
				while valorSumaTotal < int(areaMax):		
					if diferenciaValores != 0:
						#Process to continue adding adjacent fields to enter the range set by the user
						arcpy.SelectLayerByLocation_management(laMesaLayer, "BOUNDARY_TOUCHES", "", "", "ADD_TO_SELECTION")
						arcpy.Statistics_analysis(laMesaLayer, tablaPruebaEstadisticas, campoSumatoria+" SUM", "Identificador")
						#infoTabla = arcpy.SearchCursor(tablaPruebaEstadisticas)
						sumaAreas = []
						'''for f in infoTabla:
							sumaAreas.append(f.getValue("SUM_" + campoSumatoria))'''
						sumaAreas = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_" + campoSumatoria)]
						
						valorSumaTotal = sum(sumaAreas)	
						valorPosterior = valorSumaTotal
						diferenciaValores = valorPosterior - valorInicial
						valorInicial = valorPosterior
					else:
						break
						
				'''infoTabla2 = arcpy.SearchCursor(tablaPruebaEstadisticas,"Identificador <> "+str(poligonosTotalesPartida[i]))
				for h in infoTabla2:
					codigos.append(h.getValue("Identificador"))
					areas.append(h.getValue("SUM_" + campoSumatoria))'''
					
				with arcpy.da.SearchCursor(tablaPruebaEstadisticas, ["Identificador", "SUM_" + campoSumatoria], where_clause="Identificador <> "+str(poligonosTotalesPartida[i])) as cursor:
					for row in cursor:
						codigos.append(row[0])
						areas.append(row[1])
					
				while valorSumaTotal > int(areaMax):
					#Process to start subtracting the polygon with existing maximum area in the last generation of adjacent polygons
					vMax = max(areas)
					indiceMax = areas.index(vMax)
					areas.pop(indiceMax)
					codigos.pop(indiceMax)
					nuevaSuma = sum(areas)
					valorSumaTotal = valorAreaPoligonoInicial[0] + nuevaSuma
					
				cadenaCodigos = str(codigos)
				cadenaCodigos = cadenaCodigos.replace("[","(")
				cadenaCodigos = cadenaCodigos.replace("]",")")
				cadenaCodigos = cadenaCodigos.replace("u","")
				arcpy.SelectLayerByAttribute_management(laMesaLayer, "CLEAR_SELECTION")

				if cadenaCodigos == "()":
					arcpy.SelectLayerByAttribute_management(laMesaLayer, "NEW_SELECTION", "Identificador = " + str(poligonosTotalesPartida[i]))
				else:
					arcpy.SelectLayerByAttribute_management(laMesaLayer, "NEW_SELECTION", "Identificador IN " + cadenaCodigos + " or Identificador = " + str(poligonosTotalesPartida[i]))
				
				#Generating polygons and blocks
				arcpy.CopyFeatures_management(laMesaLayer, poligonosGeneradosIteracion, "", "0", "0", "0")
				
				arcpy.MakeFeatureLayer_management(copia_Original, copia_Original_FL, "", "", "")
				arcpy.SelectLayerByLocation_management(copia_Original_FL, 'ARE_IDENTICAL_TO', laMesaLayer, "", 'NEW_SELECTION', "")
				cadena_aux = "Bloque_Grupo" + str(i + valInicial)
				arcpy.CalculateField_management(copia_Original_FL, "Groups", '"'+cadena_aux+'"', "PYTHON_9.3", "")
				arcpy.SelectLayerByAttribute_management(copia_Original_FL, "CLEAR_SELECTION")
				
				#arcpy.CopyFeatures_management(poligonosGeneradosIteracion, poligonosGeneradosIteracionFinal, "", "0", "0", "0")
				aRutasFinales.append("Bloque_Grupo" + str(i + valInicial))
				arcpy.Statistics_analysis(laMesaLayer, tablaEstadisticasFinalBloque, campoSumatoria+ " SUM", "")
				#cursorTablaBloqueFinal = arcpy.SearchCursor(tablaEstadisticasFinalBloque)
				areasFinalBloque = []
				'''for f in cursorTablaBloqueFinal:
					areasFinalBloque.append(f.getValue("SUM_" + campoSumatoria))'''
				
				areasFinalBloque = [row[0] for row in arcpy.da.SearchCursor(tablaEstadisticasFinalBloque, "SUM_"+campoSumatoria)]
						
				#arcpy.AddMessage("The block ends with a value of " + str(sum(areasFinalBloque)))
				eraseFinalProsigue = GDBBorrador + "\\EraseIteracion" + str(i)
				arcpy.Erase_analysis(fcInicial, poligonosGeneradosIteracion, eraseFinalProsigue)
				indiceOperadores.append(i)
				
			else:
				#Other process iterations
				eraseFinalProsigueLayer = "eraseFinalProsigueLayer"
				arcpy.MakeFeatureLayer_management(eraseFinalProsigue, eraseFinalProsigueLayer, "", "", "")
				
				arcpy.SelectLayerByAttribute_management(eraseFinalProsigueLayer, "NEW_SELECTION", "Identificador = "+str(poligonosTotalesPartida[i]))
				numContadorSeleccionados = arcpy.GetCount_management(eraseFinalProsigueLayer)		
				if str(numContadorSeleccionados) == "0":
					#arcpy.AddMessage("The polygon already belongs to a group established")
					pass
				else:	
					arcpy.SelectLayerByLocation_management(eraseFinalProsigueLayer, "BOUNDARY_TOUCHES", "", "", "ADD_TO_SELECTION")
					arcpy.Statistics_analysis(eraseFinalProsigueLayer, tablaPruebaEstadisticas, campoSumatoria+" SUM", "Identificador")
					#infoTabla1 = arcpy.SearchCursor(tablaPruebaEstadisticas)
					#infoTabla3 = arcpy.SearchCursor(tablaPruebaEstadisticas,"Identificador = "+str(poligonosTotalesPartida[i]))
					sumaAreas = []
					codigos = []
					areas = []
					valorAreaPoligonoInicial = 0
					'''for f in infoTabla1:
						sumaAreas.append(f.getValue("SUM_" + campoSumatoria))'''
						
					sumaAreas = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_"+campoSumatoria)]
					valorSumaTotal = sum(sumaAreas)
					valorAreaPoligonoInicial = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_"+campoSumatoria, where_clause="Identificador = "+str(poligonosTotalesPartida[i]))]

					'''for l in infoTabla3:
						valorAreaPoligonoInicial = l.getValue("SUM_" + campoSumatoria)'''

					#arcpy.AddMessage("Polygon base value: " + str(valorAreaPoligonoInicial))	
					valorInicial = valorSumaTotal
					diferenciaValores = 1
					while valorSumaTotal < int(areaMax):
						if diferenciaValores != 0:
							#Process to continue adding adjacent fields to enter the range set by the user
							arcpy.SelectLayerByLocation_management(eraseFinalProsigueLayer, "BOUNDARY_TOUCHES", "", "", "ADD_TO_SELECTION")
							arcpy.Statistics_analysis(eraseFinalProsigueLayer, tablaPruebaEstadisticas, campoSumatoria+" SUM", "Identificador")
							#infoTabla = arcpy.SearchCursor(tablaPruebaEstadisticas)
							sumaAreas = []
							'''for f in infoTabla:
								sumaAreas.append(f.getValue("SUM_" + campoSumatoria))'''
							sumaAreas = [row[0] for row in arcpy.da.SearchCursor(tablaPruebaEstadisticas, "SUM_" + campoSumatoria)]
							
							valorSumaTotal = sum(sumaAreas)	
							valorPosterior = valorSumaTotal
							diferenciaValores = valorPosterior - valorInicial
							valorInicial = valorPosterior						
						else:
							break
							
					'''infoTabla2 = arcpy.SearchCursor(tablaPruebaEstadisticas,"Identificador <> "+str(poligonosTotalesPartida[i]))
					for h in infoTabla2:
						codigos.append(h.getValue("Identificador"))
						areas.append(h.getValue("SUM_" + campoSumatoria))'''
						
					with arcpy.da.SearchCursor(tablaPruebaEstadisticas, ["Identificador", "SUM_" + campoSumatoria], where_clause="Identificador <> "+str(poligonosTotalesPartida[i])) as cursor:
						for row in cursor:
							codigos.append(row[0])
							areas.append(row[1])
						
					while valorSumaTotal > int(areaMax):
						#Process to start subtracting the polygon with existing maximum area in the last 
						vMax = max(areas)
						indiceMax = areas.index(vMax)
						areas.pop(indiceMax)
						codigos.pop(indiceMax)
						nuevaSuma = sum(areas)
						valorSumaTotal = valorAreaPoligonoInicial[0] + nuevaSuma
					
					cadenaCodigos = str(codigos)
					cadenaCodigos = cadenaCodigos.replace("[","(")
					cadenaCodigos = cadenaCodigos.replace("]",")")
					cadenaCodigos = cadenaCodigos.replace("u","")	
					arcpy.SelectLayerByAttribute_management(eraseFinalProsigueLayer, "CLEAR_SELECTION")
					
					if cadenaCodigos == "()":
						arcpy.SelectLayerByAttribute_management(eraseFinalProsigueLayer, "NEW_SELECTION", "Identificador = " + str(poligonosTotalesPartida[i]))
					else:
						arcpy.SelectLayerByAttribute_management(eraseFinalProsigueLayer, "NEW_SELECTION", "Identificador IN " + cadenaCodigos + " or Identificador = " + str(poligonosTotalesPartida[i]))
					
					#Generating polygons end blocks
					arcpy.CopyFeatures_management(eraseFinalProsigueLayer, poligonosGeneradosIteracion, "", "0", "0", "0")
					
					arcpy.MakeFeatureLayer_management(copia_Original, copia_Original_FL, "", "", "")
					arcpy.SelectLayerByLocation_management(copia_Original_FL, 'ARE_IDENTICAL_TO', eraseFinalProsigueLayer, "", 'NEW_SELECTION', "")
					cadena_aux = "Bloque_Grupo" + str(i + valInicial)
					arcpy.CalculateField_management(copia_Original_FL, "Groups", '"'+cadena_aux+'"', "PYTHON_9.3", "")
					arcpy.SelectLayerByAttribute_management(copia_Original_FL, "CLEAR_SELECTION")
					
					#arcpy.CopyFeatures_management(poligonosGeneradosIteracion, poligonosGeneradosIteracionFinal, "", "0", "0", "0")
					aRutasFinales.append("Bloque_Grupo" + str(i + valInicial))
					arcpy.Statistics_analysis(eraseFinalProsigueLayer, tablaEstadisticasFinalBloque, campoSumatoria +" SUM", "")
					#cursorTablaBloqueFinal = arcpy.SearchCursor(tablaEstadisticasFinalBloque)
					areasFinalBloque = []
					'''for f in cursorTablaBloqueFinal:
						areasFinalBloque.append(f.getValue("SUM_" + campoSumatoria))'''
						
					areasFinalBloque = [row[0] for row in arcpy.da.SearchCursor(tablaEstadisticasFinalBloque, "SUM_"+campoSumatoria)]
							
					#arcpy.AddMessage("The block ends with a value of " + str(sum(areasFinalBloque)))
					eraseFinalProsigue = GDBBorrador + "\\EraseIteracion" + str(i)
					indiceOperadores.append(i)
					longIndiceOperadores = len(indiceOperadores)
					arcpy.Erase_analysis(GDBBorrador+"\\EraseIteracion" + str(indiceOperadores[longIndiceOperadores-2]),poligonosGeneradosIteracion,eraseFinalProsigue)
			
		longIndiceOperadores = len(indiceOperadores)
		ultimoValor = indiceOperadores[longIndiceOperadores-1]
		
		numEvalFuncion = int(arcpy.arcpy.GetCount_management(GDBBorrador+"\\EraseIteracion" + str(indiceOperadores[longIndiceOperadores-1])).getOutput(0))
		arcpy.AddMessage("Remain to process the following polygons: " + str(numEvalFuncion))
		if numEvalFuncion != 0:
			copiaEraseFinal = GDBFinal +"\\Ultimo_Erase"
			arcpy.CopyFeatures_management(GDBBorrador+"\\EraseIteracion" + str(indiceOperadores[longIndiceOperadores-1]), copiaEraseFinal, "", "0", "0", "0")
			arcpy.env.workspace = GDBBorrador
			ultimoValor = ultimoValor + valInicial + 1
			for fc in arcpy.ListFeatureClasses("*", "ALL"):
				arcpy.Delete_management(fc)
		 
			for ta in arcpy.ListTables("*", "ALL"):
				arcpy.Delete_management(ta)
			
			valFac = ultimoValor
			#arcpy.AddMessage("Begins new generation of origin polygons and subsequent iterations " + str(valFac))
			funcionGeneracionGrupos(pGDBBorrador,pGDBFinal,copiaEraseFinal,pFieldSeleccionado,valFac,pValorMaximo,aRutasFinales)	
		
		else:
			arcpy.env.workspace = GDBFinal
			arcpy.Delete_management("Ultimo_Erase")		
			capaSalidaGeneralizacion = generalization(GDBFinal+"\\Union_Bloques_Grupos")
			arcpy.SetParameterAsText(5, capaSalidaGeneralizacion)
			numeroGrupos(GDBFinal+"\\Union_Bloques_Grupos", "Groups", "Reclas_Groups", "Reclas_Groups_2")
			genEstad_Finales(GDBFinal+"\\Union_Bloques_Grupos", campoSumatoria, GDBFinal)
			
	def generalization(featureInsumo):
		"""Funcion para generalizar el resultado"""
		arcpy.AddMessage("Generalization Process")

		arcpy.CalculateAdjacentFields_cartography(featureInsumo, "Groups")
		arcpy.AddField_management(featureInsumo, "Reclas_Groups", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
		arcpy.CalculateField_management(featureInsumo, "Groups_N", "validacion( !Groups_N! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal\\n  ")
		arcpy.CalculateField_management(featureInsumo, "Groups_SE", "validacion( !Groups_SE! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Groups_NE", "validacion( !Groups_NE! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")															
		arcpy.CalculateField_management(featureInsumo, "Groups_NW", "validacion( !Groups_NW! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Groups_W", "validacion( !Groups_W! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Groups_S", "validacion( !Groups_S! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Groups_E", "validacion( !Groups_E! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Groups_SW", "validacion( !Groups_SW! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups", "calculo_Pesos( !Groups_NW! , !Groups_N! , !Groups_NE! , !Groups_W! , !Groups_E! , !Groups_SW! , !Groups_S! , !Groups_SE!, !Groups! )", "PYTHON_9.3", "def calculo_Pesos(valor1, valor2, valor3, valor4, valor5, valor6, valor7,valor8, zona):\\n import arcpy\\n valorFinal = \"\"\\n aValores = []\\n aValores.append( valor1)\\n aValores.append( valor2)\\n aValores.append( valor3)\\n aValores.append( valor4)\\n aValores.append( valor5)\\n aValores.append( valor6)\\n aValores.append( valor7)\\n aValores.append( valor8)\\n\\n aConteos = []\\n aConteos.append(aValores.count( valor1 ))\\n aConteos.append(aValores.count( valor2))\\n aConteos.append(aValores.count( valor3))\\n aConteos.append(aValores.count( valor4))\\n aConteos.append(aValores.count( valor5 ))\\n aConteos.append(aValores.count( valor6))\\n aConteos.append(aValores.count( valor7))\\n aConteos.append(aValores.count( valor8))\\n\\n aDefinicion = []\\n aDefinicion.append(aValores.count( valor1 ))\\n aDefinicion.append(aValores.count( valor2))\\n aDefinicion.append(aValores.count( valor3))\\n aDefinicion.append(aValores.count( valor4))\\n aDefinicion.append(aValores.count( valor5 ))\\n aDefinicion.append(aValores.count( valor6))\\n aDefinicion.append(aValores.count( valor7))\\n aDefinicion.append(aValores.count( valor8))\\n\\n aConteos.sort()\\n aConteos.reverse()\\n valorEvaluacion = aConteos[0]\\n \\n indice = aDefinicion.index(valorEvaluacion)\\n valorOriginal = aValores[indice]\\n \\n if valorEvaluacion >= 6 and str(valorOriginal) != '0' and str(zona) != \"None\":\\n  valorFinal = str(valorOriginal)\\n elif valorEvaluacion >= 5 and str(valorOriginal) != '0' and str(zona) == \"None\":\\n  valorFinal = str(valorOriginal)\\n elif str(valorOriginal) == '0' and str(zona) != \"None\":\\n  valorFinal = str(zona)\\n elif str(zona) == \"None\":\\n  valorFinal = \"Indeterminados\"\\n else:\\n  valorFinal = str(zona)\\n\\n return valorFinal")
		arcpy.DeleteField_management(featureInsumo, 'Groups_NW;Groups_N;Groups_NE;Groups_W;Groups_E;Groups_SW;Groups_S;Groups_SE')

		arcpy.CalculateAdjacentFields_cartography(featureInsumo, "Reclas_Groups")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_N", "validacion( !Reclas_Groups_N! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal\\n  ")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_SE", "validacion( !Reclas_Groups_SE! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_NE", "validacion( !Reclas_Groups_NE! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")															
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_NW", "validacion( !Reclas_Groups_NW! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_W", "validacion( !Reclas_Groups_W! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_S", "validacion( !Reclas_Groups_S! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_E", "validacion( !Reclas_Groups_E! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_SW", "validacion( !Reclas_Groups_SW! )", "PYTHON_9.3", "def validacion(valor):\\n vFinal = \"\" \\n if str(valor) == \"\" or str(valor) == \"None\":\\n  vFinal = \"0\"\\n else:\\n  vFinal = str(valor)\\n\\n return vFinal")
		arcpy.AddField_management(featureInsumo, "Reclas_Groups_2", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
		#arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_2", "revisionFinal( !Reclas_Groups_NW! , !Reclas_Groups_N! , !Reclas_Groups_NE! , !Reclas_Groups_W! , !Reclas_Groups_E! , !Reclas_Groups_SW! , !Reclas_Groups_S! , !Reclas_Groups_SE!, !Reclas_Groups! )", "PYTHON_9.3", "def revisionFinal(valor1, valor2, valor3, valor4, valor5, valor6, valor7,valor8, zona):\\n import arcpy\\n valorFinal = \"\"\\n aValores = []\\n aValores.append( valor1)\\n aValores.append( valor2)\\n aValores.append( valor3)\\n aValores.append( valor4)\\n aValores.append( valor5)\\n aValores.append( valor6)\\n aValores.append( valor7)\\n aValores.append( valor8)\\n \\n aUnicos = []\\n for k in aValores:\\n  if k not in aUnicos:\\n	aUnicos.append(k)\\n \\n aConteos = []\\n for k in aValores:\\n  aConteos.append(aValores.count(k))\\n\\n aDefinicion = []  \\n for i in aValores:\\n  aDefinicion.append(aValores.count(i))\\n  \\n aConteos.sort()\\n aConteos.reverse()\\n valorEvaluacion = aConteos[0]    \\n \\n indice = aDefinicion.index(valorEvaluacion)\\n valorOriginal = aValores[indice]\\n \\n if zona not in aUnicos and str(valorOriginal) != '0':\\n  valorFinal = str(valorOriginal)\\n elif zona not in aUnicos and str(valorOriginal) == '0':\\n  aValoresSinCeros = aValores\\n  for g in aValoresSinCeros:\\n   if g == '0':\\n    aValoresSinCeros.remove(g)\\n   \\n  aConteosSinCeros = []\\n  for k in aValoresSinCeros:\\n   aConteosSinCeros.append(aValoresSinCeros.count(k))\\n\\n  aDefinicionSinCeros = []  \\n  for i in aValores:\\n   aDefinicionSinCeros.append(aValoresSinCeros.count(i))\\n  \\n  aConteosSinCeros.sort()\\n  aConteosSinCeros.reverse()\\n  valorEvaluacion_2 = aConteos[0] \\n \\n  indice_2 = aDefinicionSinCeros.index(valorEvaluacion_2)\\n  valorOriginal_2 = aValoresSinCeros[indice_2]\\n  valorFinal = str(valorOriginal_2)\\n else:   \\n  valorFinal = str(zona)\\n\\n return valorFinal")
		arcpy.CalculateField_management(featureInsumo, "Reclas_Groups_2", "revisionFinal( !Reclas_Groups_NW! , !Reclas_Groups_N! , !Reclas_Groups_NE! , !Reclas_Groups_W! , !Reclas_Groups_E! , !Reclas_Groups_SW! , !Reclas_Groups_S! , !Reclas_Groups_SE!, !Reclas_Groups! )", "PYTHON_9.3", "def revisionFinal(valor1, valor2, valor3, valor4, valor5, valor6, valor7,valor8, zona):\\n import arcpy\\n valorFinal = \"\"\\n aValores = []\\n aValores.append( valor1)\\n aValores.append( valor2)\\n aValores.append( valor3)\\n aValores.append( valor4)\\n aValores.append( valor5)\\n aValores.append( valor6)\\n aValores.append( valor7)\\n aValores.append( valor8)\\n\\n aUnicos = []\\n for k in aValores:\\n  if k not in aUnicos:\\n	aUnicos.append(k)\\n\\n aConteos = []\\n for k in aValores:\\n  aConteos.append(aValores.count(k))\\n\\n aDefinicion = []\\n for i in aValores:\\n  aDefinicion.append(aValores.count(i))\\n\\n aConteos.sort()\\n aConteos.reverse()\\n valorEvaluacion = aConteos[0]\\n\\n indice = aDefinicion.index(valorEvaluacion)\\n valorOriginal = aValores[indice]\\n\\n if len(aUnicos) == 1 and aUnicos[0] == \"0\":\\n  valorFinal = str(zona)\\n elif zona not in aUnicos and str(valorOriginal) != '0':\\n  valorFinal = str(valorOriginal)\\n elif zona not in aUnicos and str(valorOriginal) == '0':\\n  aValoresSinCeros = []\\n  for g in aValores:\\n   if g != '0':\\n    aValoresSinCeros.append(g)\\n\\n  aConteosSinCeros = []\\n  for k in aValoresSinCeros:\\n   aConteosSinCeros.append(aValoresSinCeros.count(k))\\n\\n  aDefinicionSinCeros = []\\n  for i in aValoresSinCeros:\\n   aDefinicionSinCeros.append(aValoresSinCeros.count(i))\\n\\n  aConteosSinCeros.sort()\\n  aConteosSinCeros.reverse()\\n  valorEvaluacion_2 = aConteosSinCeros[0]\\n\\n  indice_2 = aDefinicionSinCeros.index(valorEvaluacion_2)\\n  valorOriginal_2 = aValoresSinCeros[indice_2]\\n  valorFinal = str(valorOriginal_2)\\n else:\\n  valorFinal = str(zona)\\n\\n return valorFinal")
		arcpy.DeleteField_management(featureInsumo, 'Reclas_Groups_NW;Reclas_Groups_N;Reclas_Groups_NE;Reclas_Groups_W;Reclas_Groups_E;Reclas_Groups_SW;Reclas_Groups_S;Reclas_Groups_SE')
		
		return featureInsumo
			
	def numeroGrupos(capaAgrupada, campoAgru_1, campoAgru_2, campoAgru_3):
		aValores_1 = []
		aValores_2 = []
		aValores_3 = []
		with arcpy.da.SearchCursor(capaAgrupada, [campoAgru_1, campoAgru_2, campoAgru_3]) as cursor:
			for row in cursor:
				aValores_1.append(row[0])
				aValores_2.append(row[1])
				aValores_3.append(row[2])
		
		uniquesVal1 = set(aValores_1)
		uniquesVal2 = set(aValores_2)
		uniquesVal3 = set(aValores_3)
		
		'''arcpy.AddMessage("Se encontraron %s grupos en la primera clasificacion" %(len(uniquesVal1)))
		arcpy.AddMessage("Se encontraron %s grupos en la segunda clasificacion" %(len(uniquesVal2)))
		arcpy.AddMessage("Se encontraron %s grupos en la tercera clasificacion" %(len(uniquesVal3)))'''
		
		rPrevia = os.path.normpath(pGDBFinal + os.sep + os.pardir)
		crearLog(rPrevia, len(uniquesVal1), len(uniquesVal2), len(uniquesVal3))
		
		nGrupos1 = list(range(len(uniquesVal1)))
		nGrupos2 = list(range(len(uniquesVal2)))
		nGrupos3 = list(range(len(uniquesVal3)))
		
		ugVal1 = list(uniquesVal1)
		ugVal2 = list(uniquesVal2)
		ugVal3 = list(uniquesVal3)
		
		with arcpy.da.UpdateCursor(capaAgrupada, [campoAgru_1, campoAgru_2, campoAgru_3]) as cursor:
			for row in cursor:
				
				ind1 = ugVal1.index(row[0])
				row[0] = "Bloque_" + str(nGrupos1[ind1])
				ind2 = ugVal2.index(row[1])
				row[1] = "Bloque_" + str(nGrupos2[ind2])
				ind3 = ugVal3.index(row[2])
				row[2] = "Bloque_" + str(nGrupos3[ind3])
				
				cursor.updateRow(row)
				
	def crearLog(ruta_Previa, numBloques1, numBloques2, numBloques3):
		archi=open(ruta_Previa+"\\Log_Agrupaciones.txt","w")
		archi.write("Se encontraron %s grupos en la primera clasificacion" %(numBloques1) + "\n")
		archi.write("Se encontraron %s grupos en la segunda clasificacion" %(numBloques2) + "\n")
		archi.write("Se encontraron %s grupos en la tercera clasificacion" %(numBloques3) + "\n")
		archi.close()
		
	def genEstad_Finales(capaInteres, campoEstad, gdbRecepcion):
		arcpy.Statistics_analysis(capaInteres, gdbRecepcion + "\\Estad_Basica_Agrupacion1", campoEstad + " SUM", 'Groups')
		arcpy.Statistics_analysis(capaInteres, gdbRecepcion + "\\Estad_Basica_Agrupacion2", campoEstad + " SUM", 'Reclas_Groups')
		arcpy.Statistics_analysis(capaInteres, gdbRecepcion + "\\Estad_Basica_Agrupacion3", campoEstad + " SUM", 'Reclas_Groups_2')
		
		
	if __name__ == '__main__':
		print "Ejecutando proceso 64 bits...."
		print pGDBBorrador, pGDBFinal, pFeatureClassInicial, pValorMaximo, pFieldSeleccionado
		principal()
		
except exceptions.Exception as e:
    print e.__class__, e.__doc__, e.message
    os.system("pause")		