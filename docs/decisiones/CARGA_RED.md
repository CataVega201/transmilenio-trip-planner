# Carga y fachada Red

Catalina Vega completa la integración inicialmente asignada a Alejandro.
Red(carpeta) lee únicamente los tres CSV recibidos. csv.reader, tablas hash
propias y merge sort iterativo permiten cargar filas mezcladas sin diccionarios
ni ordenamientos de biblioteca en motor/.

La carga conserva los nombres originales y usa claves normalizadas solo para
buscar. Rechaza encabezados, columnas, órdenes o referencias inválidos,
estaciones ambiguas y paradas repetidas; indica archivo y fila cuando corresponde.
Admite BOM UTF-8, rutas de carpeta con espacios, horas mayores de 23 y eventos
duplicados. Los eventos duplicados cuentan como buses distintos.

Con n estaciones, p paradas de rutas y h horarios, la construcción usa
O(n log n + p log p + h log h) esperado en tiempo y O(n + p + h) espacio,
incluidos los arreglos auxiliares de ordenación. Las colisiones pueden empeorar
las operaciones hash. El orden de rutas se compara numéricamente; cada ruta
mantiene su sentido. Una carga fallida no publica una red parcialmente cargada.

El lector valida antes de construir los índices finales. La alternativa de
insertar cada parada buscando linealmente su posición haría la carga cuadrática.
No se modifica el directorio global y no se incluyen rutas del computador autor.

Comprobación local de carga con el generador de Daniel, una ejecución por tamaño:
10.000 estaciones, 0,352 s; 20.000, 0,831 s; 40.000, 2,168 s; 80.000, 4,950 s.
Son observaciones preliminares y no medianas oficiales ni una garantía entre
máquinas. Ambos conjuntos CSV reales cargaron en aproximadamente 0,6 s.

Exportación pública: from motor import Red, simular_fila.
El contrato incluye los índices alfabéticos R2/R3 y el ranking incremental R6.
