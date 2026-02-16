import random
import multiprocessing as mp

def tsp_evo(dist):
    
    def delta_2opt(ruta, i, j, dist):   # Calculamos el coste de manera incremental
        
        n = len(ruta)
        a = ruta[(i - 1) % n]
        b = ruta[i % n]
        c = ruta[j % n]
        d = ruta[(j + 1) % n]  # Evita i=0, como la funcion 2opt en los indices de los bucles.
    
        quitados = dist[a][b] + dist[c][d]
        sumados = dist[a][c] + dist[b][d]
        return sumados - quitados
    
    
    
    
    ###_______________________________________ FUNCION FITNESS ______________________________________________###
    
    
    def fitness(ruta, dist):    # En esta ocasion solo lo usamos al construir o medir rutas completas, ya que el calculo de las mejoras es incremental
        total = 0
        n = len(ruta)
        for i in range(n):
            total += dist[ruta[i]][ruta[(i + 1) % n]]
        return total
    
    
    ###_______________________________________ FUNCION DE SELECCION (POR TORNEO) ______________________________________________###
    
    
    def seleccion(poblacion, k=2):   # Poblacion es lista de (ruta, coste)
        candidatos = random.sample(poblacion, k)
        return min(candidatos, key=lambda x: x[1])
    
    
    ###_______________________________________ FUNCION DE CRUCE (PMX) ______________________________________________###
    
    def cruce(padre1, padre2):
        n = len(padre1)
        hijo = [-1] * n
        a, b = sorted(random.sample(range(n), 2))
        hijo[a:b+1] = padre1[a:b+1]
    
        for i in range(a, b+1):
            if padre2[i] not in hijo:
                posicion = i
                ciudad = padre2[i]
                
                # resolver colisiones (cuando se va a repetir o a saltar una ciudad)
                while hijo[posicion] != -1:
                    posicion = padre2.index(padre1[posicion])
                hijo[posicion] = ciudad
    
        for i in range(n):
            if hijo[i] == -1:
                hijo[i] = padre2[i]
        return hijo
    
    
    
    ###_______________________________________ FUNCIONES DE MUTACION (INVERSION Y SWAP) ______________________________________________###
    
    def mutacion_inv(ruta):
        i, j = sorted(random.sample(range(len(ruta)), 2))
        r = ruta[:]   # Copiamos para no mutar la original
        r[i:j+1] = reversed(r[i:j+1])
        return r
    
    def mutacion_swap(ruta):
        i, j = random.sample(range(len(ruta)), 2)
        r = ruta[:]   # Copiamos para no mutar la original
        r[i], r[j] = r[j], r[i]
        return r
    
    ###_______________________________________ 2-OPT (EVALUACIÓN INCREMENTAL) ______________________________________________###
    
    def dos_opt(ruta, dist):   # Consiste en cambiar aristas AB y CD por AC y BD, lo hacemos con calculo incremental del coste
        n = len(ruta)
        mejor = ruta[:]
        mejor_ruta = fitness(mejor, dist)
    
        mejora = True
        while mejora:
            mejora = False
            # empezar en 1 para mantener a (0) como posible ancla (se puede variar)
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # evitar 2-opt trivial (adyacente con j = i+1 se puede saltar)
                    if i == j:
                        continue
                    delta = delta_2opt(mejor, i, j, dist)
                    if delta < 0:
                        # aplicar inversión y actualizar coste incrementalmente
                        mejor[i:j+1] = reversed(mejor[i:j+1])
                        mejor_ruta += delta
                        mejora = True
                        break
                if mejora:
                    break
        return mejor, mejor_ruta
    
    
    
    ###_______________________________________ WORKER PARA POOL ______________________________________________###
    
    def worker_dos_opt(args): # La funcion que mapeamos en el pool
        ruta, distanc = args
        return dos_opt(ruta, distanc)  # devuelve (ruta, coste)
    
    ###_______________________________________ ALGORITMO MEMETICO PARALELIZADO ______________________________________________###
    
    def algoritmo_genetico(dist, poblacion_inicial=80, generaciones=300,
                       p_mut=0.2, elitismo=1, p_local=0.3, n_jobs=None,
                       numtor=2):
    
        if n_jobs is None:
            n_jobs = mp.cpu_count()
    
        n = len(dist)
    
        # inicializamos la población (ruta, coste)
        poblacion = []
        for _ in range(poblacion_inicial):
            r = random.sample(range(n), n)
            poblacion.append((r, fitness(r, dist)))
    
        # mejoramos el mejor inicial con 2-opt (secuencial)
        poblacion.sort(key=lambda x: x[1])
        mejor0, mejor_coste0 = dos_opt(poblacion[0][0], dist)
        poblacion[0] = (mejor0, mejor_coste0)
    
        # creamos Pool una vez (se crea en contexto en main guard)
        pool = mp.Pool(processes=n_jobs)
    
        try:
            for gen in range(generaciones):
                # ordenamos para elitismo
                poblacion.sort(key=lambda x: x[1])
                nueva_poblacion = poblacion[:elitismo]  # copiar élites (lista de tuplas)
    
                # mejoramos la élite con 2-opt (opcional redundante, pero preserva calidad)
                ruta_elite, coste_elite = dos_opt(nueva_poblacion[0][0][:], dist)
                nueva_poblacion[0] = (ruta_elite, coste_elite)
    
                hijos = []
                # generar hijos sin local search todavía
                while len(hijos) + len(nueva_poblacion) < poblacion_inicial:
                    p1, _ = seleccion(poblacion, k=numtor)
                    p2, _ = seleccion(poblacion, k=numtor)
                    hijo = cruce(p1, p2)
    
                    # mutamos o bien por inversion o bien por swap
                    if random.random() < p_mut:
                        if random.random() < 0.5:
                            hijo = mutacion_inv(hijo)
                        else:
                            hijo = mutacion_swap(hijo)
    
                    # calcular coste completo del hijo (O(n))
                    coste_hijo = fitness(hijo, dist)
    
                    # decidir si aplicaremos 2-opt local (p_local)
                    if random.random() < p_local:
                        # añadimos a la lista para procesar en paralelo
                        hijos.append((hijo, None))  # None placeholder para coste
                    else:
                        # sin 2-opt, lo añadimos directamente
                        hijos.append((hijo, coste_hijo))
    
                # Separar los que necesitan 2-opt
                to_opt = [(c[0], dist) for c in hijos if c[1] is None]
                # indices para reconstruir hijos
                idx_map = [i for i, c in enumerate(hijos) if c[1] is None]
    
                # ejecutar 2-opt en paralelo
                if to_opt:
                    results = pool.map(worker_dos_opt, to_opt)
                    # results: lista de (ruta_mejorada, coste_mejorado)
                    r_iter = iter(results)
                    # reconstruir hijos con resultados mejorados
                    for idx in idx_map:
                        ruta_mejorada, coste_mejorado = next(r_iter)
                        hijos[idx] = (ruta_mejorada, coste_mejorado)
    
                # ahora todos los hijos tienen coste -> los añadimos a nueva_poblacion 
                nueva_poblacion.extend(hijos)
    
                # asegurar tamaño correcto (en caso de pequeños desajustes)
                poblacion = nueva_poblacion[:poblacion_inicial]
                print(f"Mejor coste generacion {gen+1}: {poblacion[0][1]}")
    
            # fin generaciones: retornar mejor individuo
            poblacion.sort(key=lambda x: x[1])
            mejor_ruta, mejor_coste = poblacion[0]
            return mejor_ruta, mejor_coste
    
        finally:
            pool.close()
            pool.join()
            
            
    # Si no queremos que se use el 2-opt, podemos hacer que la probabilidad de usarlo p_local sea nula o -1 
 
    return algoritmo_genetico(dist,
                              poblacion_inicial=80,
                              generaciones=100,
                              p_mut=0.2,
                              elitismo=2,
                              p_local=0.1,
                              n_jobs=4,  # ajustar según CPUs
                              numtor=3)
