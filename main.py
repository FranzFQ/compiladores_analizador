import json
from analizador_code import *
from analisis_semantico import *

texto = """
int suma (int a, int b){
  int c = a + b;
  return c;
}

"""

def imprimir_ast(nodo):
  if isinstance(nodo, NodoFunciones):
    return {"Funciones": [imprimir_ast(f) for f in nodo.funcion]}
  elif isinstance(nodo, NodoFuncion):
    return {"Funcion": nodo.nombre, 
            "Parametros": [imprimir_ast(p) for p in nodo.parametro],
            "Cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]}
  elif isinstance(nodo, NodoParametro):
    return {"Parametro": nodo.nombre, "Tipo": nodo.tipo} 
  elif isinstance(nodo, NodoAsignacion):
    return {"Asignacion": nodo.nombre, "Expresion": imprimir_ast(nodo.expresion)}
  elif isinstance(nodo, NodoOperacion):
    return {"Operacion": nodo.operador, 
            "Izquierda": imprimir_ast(nodo.izquierda),
            "Derecha": imprimir_ast(nodo.derecha)}
  elif isinstance(nodo, NodoRetorno):
    return {"Return": nodo.expresion}
  elif isinstance(nodo, NodoIdentificador):
    return {"Identificador": nodo.nombre}
  elif isinstance(nodo, NodoNumero):
    return {"Numero": nodo.valor}
  elif isinstance(nodo, NodoIf):
    return {"If": imprimir_ast(nodo.condicion)}
  elif isinstance(nodo, NodoWhile):
    return {"While": imprimir_ast(nodo.condicion)}
  elif isinstance(nodo, NodoFor):
    return {"For": [imprimir_ast(nodo.expresion1), imprimir_ast(nodo.expresion2), imprimir_ast(nodo.expresion3)]}
  elif isinstance(nodo, NodoPrint):
    return {"Print": imprimir_ast(nodo.contenido)}
  return {}

# Aquí se probará el analizador sintáctico
try:
  tokens = tokenize(texto)
  print('Se inicia el análisis sintáctico')
  parser = Parser(tokens)
  arbol_ast = parser.parsear()
  print(json.dumps(imprimir_ast(arbol_ast), indent=1))
  codigo_python = arbol_ast.traducir()
  print(codigo_python)
  codigo_asm = arbol_ast.generar_codigo()
  print(codigo_asm)
  Analizador_semantico = AnalizadorSemantico()
  analisis = Analizador_semantico.analizar(arbol_ast)
  
  print("Variables")
  for llave in (Analizador_semantico.tabla_simbolos.variables.keys()):
    valor = Analizador_semantico.tabla_simbolos.variables.get(llave)
    print(f"{llave}: {valor}")

  print("Funciones")
  for llave in (Analizador_semantico.tabla_simbolos.funciones.keys()):
    valor = Analizador_semantico.tabla_simbolos.funciones.get(llave)
    print(f"{llave}: {valor}")

  print('Análisis sintáctico exitoso')
  
except SyntaxError as e:
  print(e)