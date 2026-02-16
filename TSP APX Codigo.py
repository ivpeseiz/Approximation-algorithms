from math import sqrt
from igraph import Graph




def tsp2apx(dist):
    
    def mat_a_grafo(distancias):
        n = len(distancias)
        aristas = []
        for i in range(n): # De 0 a 57
            for j in range(n-i):   # De 0 a 57,56,...,0
                if i != j:
                    aristas.append((i,j))
        
        g = Graph(edges = aristas, directed = False)
        
        pesos = []
        for i in range(n): # De 0 a 57
            for j in range(n-i):   # De 0 a 57,56,...,0
                if i != j:
                    pesos.append(distancias[i][j])
                    
        # Grafo valorado no dirigido
    
        g.es["weight"] = pesos
        g.vs["label"] = list(range(g.vcount()))
        return g
    
    
    g = mat_a_grafo(dist)
    
    

    
    
    # Árbol de recubrimiento mínimo
    arm = g.spanning_tree(weights = g.es["weight"], return_tree = True)
    
    
    # Duplicamos aristas y hacemos ciclo euleriano
    def ciclo_euleriano(g, inicio = 0):
        visitados = set()
        camino = []
    
        def busca(u):
            visitados.add(u)
            camino.append(u)
            for v in g.neighbors(u):
                if v not in visitados:
                    busca(v)
                    # al volver, repetimos u para "pasar dos veces"
                    camino.append(u)
    
        busca(inicio)
        return camino
    
    recorr_priori = ciclo_euleriano(arm, inicio = 0)
    print("Recorrido del ARM duplicado:", recorr_priori)
    
    visitados = set()
    recorrido = []
    for vertice in recorr_priori:
        if vertice in visitados:
            pass
        else:
            visitados.add(vertice)
            recorrido.append(vertice)
    #recorrido.append(recorrido[0])  # Si se quiere que el ultimo elemento de la solucion vuelva a ser el inicio se descomenta esta linea
    print("TSP con factor 2:", recorrido)
    
    
    v = 0
    m = len(recorrido) - 1
    for i in range(m):
        v += dist[int(recorrido[i])][int(recorrido[i+1])]
    v += dist[int(recorrido[-1])][int(recorrido[0])]