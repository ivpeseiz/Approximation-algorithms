import random
from time import time


# =====================================================
# Parametros
# =====================================================
POBLACION_INICIAL = 120
GENERACIONES = 100
PROB_CRUCE = 0.8
PROB_MUTACION = 0.01
NUM_TOR = 3
ELITISMO = 5
PENALTY = 10_000

# =====================================================
# Fitness
# =====================================================
def fitness(individuo, U, subconjuntos, costes):
    cubiertos = set()
    coste = 0

    for i, gen in enumerate(individuo):
        if gen:
            cubiertos |= subconjuntos[i]
            coste += costes[i]

    return coste + PENALTY * len(U - cubiertos)


# =====================================================
# Funcion arreglar (heuristico)
# =====================================================
def arreglar(individuo, U, subconjuntos, costes):  # nos aseguramos de que el individuo cubre el universo, usando subcjtos no seleccionados para cubrir elementos no cubiertos y lo hace priorizando subcjtos baratos que cubran muchos elementos restantes
    cubiertos = set()   # Para almacenar los elementos que ya estan cubiertos por el individuo
    for i, gen in enumerate(individuo):
        if gen:
            cubiertos |= subconjuntos[i]  # Unimos ambos conjuntos (añadimos el conjunto que si escogemos al conjunto de elementos cubiertos)

    no_cubiertos = U - cubiertos   # Cogemos el complementario en U de cubiertos para ver que elementos quedan por cubrir

    while no_cubiertos:   # Mientras haya elementos no cubiertos
        mejor_i = None
        mejor_ratio = float("inf")

        for i, subconjunto in enumerate(subconjuntos):
            if individuo[i] == 0:
                nuevo = len(subconjunto & no_cubiertos)
                if nuevo > 0:
                    ratio = costes[i] / nuevo
                    if ratio < mejor_ratio:
                        mejor_ratio = ratio
                        mejor_i = i

        if mejor_i is None:
            break

        individuo[mejor_i] = 1
        cubiertos |= subconjuntos[mejor_i]
        no_cubiertos = U - cubiertos
                    
    return individuo


# =====================================================
# Redundancy Elimination
# =====================================================
def quita_redundancia(individuo, U, subconjuntos):
    activos = [i for i, b in enumerate(individuo) if b]
    random.shuffle(activos)    # Cambiamos aleatoriamente el orden de los subconjuntos activos para evitar sesgos a la hora de descartar subconjuntos redundantes

    for i in activos:    # Para cada subconjunto que hemos seleccionado vemos si al no seleccinarlo el conjunto U sigue cubierto con el resto de subconjuntos
        individuo[i] = 0
        cubiertos = set()
        for j, b in enumerate(individuo):
            if b:
                cubiertos |= subconjuntos[j]

        if cubiertos != U:   # Si resulta que no cubrimos U al quitar el subconjunto i, le volvemos a seleccionar
            individuo[i] = 1

    return individuo


# =====================================================
# Funcion de mejora local
# =====================================================
def mejora_local(individuo, U, subconjuntos):   # Asumimos que los costes son no negativos
    mejora = True

    while mejora:    # Buscamos minimo local tatando de quitar los subconjuntos redundantes pero de manera distinta a quita-redundancia, ya que hacemos varias pasadas por los subconjuntos (tambien con un coste computacional mayor, de ahi la existencia de la otra funcion)
        mejora = False
        for i in range(len(individuo)):
            if individuo[i]:
                individuo[i] = 0
                cubiertos = set()
                for j, b in enumerate(individuo):
                    if b:
                        cubiertos |= subconjuntos[j]

                if cubiertos == U:
                    mejora = True
                else:
                    individuo[i] = 1
    return individuo


# =====================================================
# Funcion de crear individuo
# =====================================================

def crear_individuo(n):
    return [random.randint(0, 1) for _ in range(n)]


# =====================================================
# Funcion de seleccion (por torneo)
# =====================================================

def seleccion(poblacion, funcion):
    return min(random.sample(poblacion, NUM_TOR), key=funcion)


# =====================================================
# Funcion de cruce
# =====================================================

def cruce(padre1, padre2):   # Un cruce en el que nos quedamos aleatoriamente con genes del padre1 o el padre 2
    if random.random() < PROB_CRUCE:
        padre = padre1[:]    # Hacemos copias estrictas de padre1 y padre2 para evitar poblemas de punteros
        madre = padre2[:]
        return [padre[i] if random.random() < 0.5 else madre[i] for i in range(len(padre))]
    return padre1[:]


# =====================================================
# Funcion de mutacion
# =====================================================

def mutacion(individuo):
    for i in range(len(individuo)):
        if random.random() < PROB_MUTACION:
            individuo[i] ^= 1  # Uso operador xor para cambiar 1 por 0 y 0 por 1
    return individuo


# =====================================================
# Algoritmo genetico
# =====================================================
def algoritmo_genetico(U, subconjuntos, costes):
    n = len(subconjuntos)

    poblacion = [arreglar(crear_individuo(n), U, subconjuntos, costes)
                  for _ in range(POBLACION_INICIAL)]

    mejor = min(poblacion, key=lambda x: fitness(x, U, subconjuntos, costes))

    for gen in range(GENERACIONES):
        poblacion.sort(key=lambda x: fitness(x, U, subconjuntos, costes))
        elites = poblacion[:ELITISMO]

        nueva_poblacion = elites[:]

        while len(nueva_poblacion) < POBLACION_INICIAL:
            padre1 = seleccion(poblacion, lambda x: fitness(x, U, subconjuntos, costes))
            padre2 = seleccion(poblacion, lambda x: fitness(x, U, subconjuntos, costes))

            hijo = cruce(padre1, padre2)
            mutacion(hijo)

            hijo = arreglar(hijo, U, subconjuntos, costes)
            hijo = quita_redundancia(hijo, U, subconjuntos)
            #hijo = mejora_local(hijo, U, subconjuntos) # Si queremos asumir más coste computacional descomentamos esta linea

            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

        mejor_actual = poblacion[0]
        if fitness(mejor_actual, U, subconjuntos, costes) < fitness(mejor, U, subconjuntos, costes):
            mejor = mejor_actual

        print(f"Gen {gen+1} | Best cost: {fitness(mejor, U, subconjuntos, costes)}")

    return mejor