<p align=center >
** SCRIPT DE PYTHON PARA LA GENERACIÓN DE GRUPOS DE POLÍGONOS**
</p>

<p>
La herramienta fue desarrolada para la creación de grupos adyacentes de poligonos de acuerdo a magnitudes acumulativas o un atributo especifico.
</p>
1. Parámetros ingresados por el usuario.
2. Zona de estudio con los valores de cada polígono según el campo seleccionado (Ejemplo Área).
3. Determinación de los polígonos mas extremos de la zona de estudio.
4. Selección de los polígonos vecinos a cada uno de los polígonos extremos previamente calculados
5. El algoritmo establece el primer grupo evaluando que la sumatoria de valores seleccionados no exceda el valor máximo ingresado por el usuario (No Mayor a 7) Si hay exceso elimina el vecino de mayor área, si hay defecto agrega mas vecinos.
6. El algoritmo itera cada uno de los polígonos extremos generando grupos con la misma lógica
7. El algoritmo empieza un nuevo ciclo para aquellos polígonos que no tienen un grupo asociado (aplicando la misma lógica desde el paso 3) hasta que la zona de estudió este cubierta por grupos de polígonos generados.



  a. [Instalación](Installation.md)
  b. [Guía de usuario](User_Guide.md)
