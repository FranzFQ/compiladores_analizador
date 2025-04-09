from analizador_code import *

#________________________________________Analisis semantico_________________________________________________________
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()

    def analizar(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar
            self.tabla_simbolos.declarar_variables(nodo.nombre[1], tipo_expr)

        elif isinstance(nodo, NodoParametro):
            self.tabla_simbolos.declarar_variables(nodo.nombre[1], nodo.tipo[1])
        
        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])

        elif isinstance(nodo, NodoNumero):
            return "int"

        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error semantico: Operacion entre tipos incompatibles")
            return tipo_izq
        
        elif isinstance(nodo, NodoFuncion):
            self.tabla_simbolos.declarar_funcion(nodo.nombre[1], nodo.parametro[0].tipo[1], nodo.parametro)
            for param in nodo.parametro:
                self.analizar(param)

        elif isinstance(nodo, NodoFuncionAnidada):
            tipo_retorno, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre[1])
            if len(parametros) != len(nodo.parametros):
                raise Exception(f"Error semantico: La funcion {nodo.nombre[1]} espera {len(parametros)} argumentos, pero se le han dado {len(nodo.parametros)}")
            return tipo_retorno

        elif isinstance(nodo, NodoFunciones):
            for funcion in nodo.funcion:
                self.analizar(funcion)

        else:
            raise Exception(f"No se ha importado el analisis semantico para {type(nodo).__name__}")
        
    # def visitar_NodoFunciones(self, nodo):
    #     for funcion in nodo.funcion:
    #         self.analizar(funcion)
  
    # def visitar_NodoFuncion(self, nodo):
    #     if nodo.nombre[1] in self.tabla_simbolos:
    #         raise Exception(f"Error semantico: la funcion {nodo.nombre[1]} ya esta definida")
    
    #     self.tabla_simbolos[nodo.nombre[1]] = {"tipo": nodo.parametro[0].tipo[1], "parametros": nodo.parametro}
    #     for param in nodo.parametro:
    #         self.tabla_simbolos[param.nombre[1]] = {"tipo": param.tipo[1]}

    #     for instruccion in nodo.cuerpo:
    #         self.analizar(instruccion)
    
    # def visitar_NodoParametro(self, nodo):
    #     if nodo.nombre[1] in self.tabla_simbolos:
    #         raise Exception(f"Error semantico: el parametro {nodo.nombre[1]} ya esta definido")
    #     self.tabla_simbolos[nodo.nombre[1]] = {"tipo": nodo.tipo[1]}

    # def visitar_NodoAsignacion(self, nodo):
    #     tipo_expresion = self.analizar(nodo.expresion)
    #     self.tabla_simbolos[nodo.nombre[1]] = {"tipo": tipo_expresion}

    # def visitar_NodoOperacion(self, nodo):
    #     tipo_izquierda = self.analizar(nodo.izquierda)
    #     tipo_derecha = self.analizar(nodo.derecha)

    #     if tipo_izquierda != tipo_derecha:
    #         raise Exception(f"Error semantico: Operacion entre tipos incompatibles")
        
    #     return tipo_izquierda

    # def visitar_NodoNumero(self, nodo):
    #     return "int" if "." not in nodo.valor[1] else "float"
    
    # def visitar_NodoIdentificador(self, nodo):
    #     if nodo.nombre[1] not in self.tabla_simbolos:
    #         raise Exception (f"Error semantico: La variable {nodo.nombre[1]} no ")
    #     return self.tabla_simbolos[nodo.nombre[1]]["tipo"]

    # def visitar_NodoRetorno(self, nodo):
    #     return self.analizar(nodo.expresion)

class TablaSimbolos:
    def __init__(self):
        self.variables = {} #almacena variables {nombre: tipo}
        self.funciones = {} #almacena funciones {nombre: (tipo_retorno, [parametros])}
    
    def declarar_variables(self, nombre, tipo):
        if nombre in self.variables:
            raise Exception(f"Error: La variable {nombre} ya ha sido declarada.")
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error: La variable {nombre} no ha sido declarada.")
        return self.variables[nombre]
    
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: La funcion {nombre} ya ha sido declarada.")
        self.funciones[nombre] = (tipo_retorno, parametros)
    
    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: La funcion {nombre} no ha sido declarada.")
        return self.funciones[nombre]