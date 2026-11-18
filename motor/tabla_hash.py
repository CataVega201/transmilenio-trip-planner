class TablaHash:
    def __init__(self):
        self._cubetas = [[] for _ in range(8)]
        self._cantidad = 0
        
    def guardar(self, clave, valor):
        posicion = hash(clave) % len(self._cubetas)
        cubeta = self._cubetas[posicion]
        for i in range(len(cubeta)):
            clave_guardada, _ = cubeta[i]
            if clave_guardada == clave:
                cubeta[i] = (clave, valor)
                return
        if (self._cantidad + 1) / len(self._cubetas) > 0.79:
            self._redimensionar(len(self._cubetas) * 2)
            posicion = hash(clave) % len(self._cubetas)                
            cubeta = self._cubetas[posicion]
        cubeta.append((clave, valor))
        self._cantidad += 1
       
    def obtener(self, clave, defecto=None): 
        posicion = hash(clave) % len(self._cubetas)
        cubeta = self._cubetas[posicion]
        for clave_guardada, valor in cubeta:
            if clave_guardada == clave:
                return valor
        return defecto
    
    def eliminar(self, clave):
        posicion = hash(clave) % len(self._cubetas)
        cubeta = self._cubetas[posicion]
        for i in range(len(cubeta)):
            clave_guardada, _ = cubeta[i]
            if clave_guardada == clave:
                del cubeta[i]
                self._cantidad -= 1
                return True
        return False
    
    def pares(self):
        for cubeta in self._cubetas:
            for clave, valor in cubeta:
                yield (clave, valor)
                
    def _redimensionar(self, nueva_capacidad):
        nueva_cubetas = [[] for _ in range(nueva_capacidad)]
        for clave, valor in self.pares():
            posicion = hash(clave) % nueva_capacidad
            nueva_cubetas[posicion].append((clave, valor))
        self._cubetas = nueva_cubetas

