
  ## Guía de Usuario para la formación de grupos polígonos adyacentes de acuerdo a una magnitud acumulativa.

<p>
Instrucciones para insertar datos en el script:</br>
Antes de iniciar los siguientes pasos, recuerde que antes debería haber leído e implementado los pasos en el manual de instrucciones de instalación.
</p>

1. Abra ArcMap y verifique que en Geoprocessing options, la opción "Overwrite the outputs of geoprocessing operations" esté marcada.

<p align="center">
 <img src="Imagenes\geoprocesing_options.png">
</p>

2. Busque el Script Python “Script_UPRA_grouping_polygons_ cumulative magnitude" en el ArcMap Catalog y de doble click en el Script, y aparecerá una venta de usuario que le permitira ingresar los datos necesarios para que el script funcione.

<p align="center">
 <img src="Imagenes\abrir_script.png">
</p>
<p align="center">
 <img src="Imagenes\interfazinicial.png">
</p>

3. En la ventana que aparecerá, el primer parámetro que solicita el Script es la ruta de ubicación del GDB (Geodatabase) donde se almacenan los resultados preliminares o parciales del proceso. (Si esta GDB no está disponible, créela).

<p align="center">
 <img src="Imagenes\ruta_gdb.png">
</p>

4. El segundo parámetro que se solicita es la ubicación de la GDB donde se guardaran los resultados finales del proceso. En esta GDB se guardaran los Feature Class de los grupos resultantes del algoritmo, con los Feature Class que contienen el merge de cada uno de los grupos. Esta GDB no debe ser la misma que la del paso 3. (Si esta GDB no está disponible, créela).

<p align="center">
 <img src="Imagenes\gdb_resultados.png">
</p>

5. El tercer parámetro solicitado por el Script es la ubicación del Feature Class que contiene los polígonos que se desean agrupar(Propiedades, lotes, bloques, zonas, vecinos, etc). Importante: El Feature Class ingresado debe estar como Single Part.

<p align="center">
 <img src="Imagenes\path_FeatureClass.png">
</p>

6. En el cuarto parámetro se selecciona al usuario el campo numérico que contiene los valores con los cuales se limitará la configuración de cada uno de los grupos mientras completa la suma total. (El campo contiene valores de área, precios, presupuestos, etc. )

<p align="center">
 <img src="Imagenes\campo_valor.png">
</p>

7. El último parámetro que será ingresado por el usuario es el valor máximo que cada  puede tener  cada grupo resultante. Este valor debe relacionarse logicamente con el campo seleccionado en el paso 6. Importante: El valor máximo asignado por el usuario, no puede ser menor que el máximo valor que se encuentre en el campo seleccionado en el paso 6, Esto podría crear un error. Logicamente, el valor máximo asignado por el usuario  tampoco debe ser menor que el valor mínimo del campo seleccionado en el paso 6.

<p align="center">
 <img src="Imagenes\valor_maximo.png">
</p>

8. Una vez todos los datos hayan sido ingresados en el script, el usuario puede proceder a dar click en el botón "OK"  y esperar a que se ejecute el proceso.
