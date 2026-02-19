# Algoritmos-de-aproximabilidad-y-gen-ticos

En este repositorio vamos a ver algoritmos de aproximación y algoritmos genéticos para tres problemas principales: el Problema de la mochila, el TSP y el Set cover.

El repositorio incluirá los algoritmos, varias instancias de algún problema

Para el problema de la mochila, el formato de la instancia para el algoritmo genético es una lista llamada items de la forma [(valor, peso)], es decir una lista de duplas donde el primer elemento del par es el valor del objeto en cuestión y el segundo elemento es su peso; y para el algoritmo FPTAS se proporcionan la lista de valores y la lista de pesos por separado. Por otro lado, la capacidad de la mochila viene dado, bien como parámetro (en el caso del algoritmo genético), o bien en la misma llamada a la función mochila_FPTAS (en el caso del algoritmo de aproximación FPTAS).

Para los algoritmos correspondientes al TSP las instancias de entrada deberán de ser expresadas de manera explícita, en forma de una matriz simétrica de distancias.

Para los algoritmos que corresponden al SCP las instancias deberán venir dadas como, por un lado el universo U, dado como un conjunto de índices, por otro lado, una lista de subconjuntos de U y, por último, la lista de costes de cada uno de los subconjuntos, indexada de la misma forma que la lista de subconjuntos.
