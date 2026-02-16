from typing import List, Set, Tuple


def voraz_set_cover(universo: Set[int], subconjuntos: List[Set[int]], costes: List[float]) -> Tuple[List[int], List[Set[int]], float, Set[int]]:
   
    falta = set(universo)
    indices_elegidos: List[int] = []
    subcjtos_elegidos: List[Set[int]] = []
    total = 0.0

    usados = [False] * len(subconjuntos)

    while falta:
        mejor_indice = None
        mejor_ratio = float("inf")
        nuevo_mejor: Set[int] = set()

        # Evaluar todos los subconjuntos que no se han usado aún
        for i, s in enumerate(subconjuntos):
            if usados[i]:
                continue
            cubre = s & falta
            if not cubre:
                continue
            ratio = costes[i] / len(cubre)
            if ratio < mejor_ratio:
                mejor_ratio = ratio
                mejor_indice = i
                nuevo_mejor = cubre

        if mejor_indice is None:
            # No se puede cubrir todo el universo
            break

        # Registrar la elección
        usados[mejor_indice] = True
        indices_elegidos.append(mejor_indice)
        subcjtos_elegidos.append(subconjuntos[mejor_indice])
        total += costes[mejor_indice]
        falta -= nuevo_mejor

    return indices_elegidos, subcjtos_elegidos, total, falta


