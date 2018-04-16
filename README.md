<p align=center >
** SCRIPT DE PYTHON PARA LA GENERACIÓN DE GRUPOS DE POLÍGONOS**
</p>

a. [Instalación](Installation.md)

b. [Guía de usuario](User_Guide.md)

## Breve descripción del Script
<p>
La herramienta fue desarrollada para la creación de grupos adyacentes de polígonos de acuerdo a magnitudes acumulativas o un atributo especifico.
</p>
1. Parámetros ingresados por el usuario.

<p align="center">
 <img src="Imagenes\interfazinicial.png">
</p>

2. Zona de estudio con los valores de cada polígono según el campo seleccionado (Ejemplo Área).

<p align="center">
 <img src="Imagenes\zona_estudio.png">
</p>

3. Determinación de los polígonos más extremos de la zona de estudio.

<p align="center">
 <img src="Imagenes\determinar_poligonos.png">
</p>

4. Selección de los polígonos vecinos a cada uno de los polígonos extremos previamente calculados.

<p align="center">
 <img src="Imagenes\seleccion_poligonos.png">
</p>

5. El algoritmo establece el primer grupo evaluando que la sumatoria de valores seleccionados no exceda el valor máximo ingresado por el usuario (No Mayor a 7) Si hay exceso elimina el vecino de mayor área, si hay defecto agrega más vecinos.

<p align="center">
 <img src="Imagenes\establece_grupo.png">
</p>

6. El algoritmo itera cada uno de los polígonos extremos generando grupos con la misma lógica.

<p align="center">
 <img src="Imagenes\iterar_poligono.png">
</p>

7. El algoritmo empieza un nuevo ciclo para aquellos polígonos que no tienen un grupo asociado (aplicando la misma lógica desde el paso 3) hasta que la zona de estudió este cubierta por grupos de polígonos generados.


<p align="center">
 <img src="Imagenes\grupos.png">
</p>
