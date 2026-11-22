def _combinar(izquierda, derecha):
    combinado = []
    i, j = 0, 0
    while i < len(izquierda) and j < len(derecha):
        if izquierda[i] < derecha[j]:
            combinado.append(izquierda[i])
            i += 1
        else:
            combinado.append(derecha[j])
            j += 1
    combinado.extend(izquierda[i:])
    combinado.extend(derecha[j:])
    return combinado

def _ordenar(lista):
    if len(lista) <= 1:
        return lista
    medio = len(lista) // 2
    izquierda = _ordenar(lista[:medio])
    derecha = _ordenar(lista[medio:])
    return _combinar(izquierda, derecha)

def _primer_indice(lista, elemento):
    bajo = 0
    alto = len(lista)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if lista[medio] < elemento:
            bajo = medio + 1
        else:
            alto = medio
    return bajo
