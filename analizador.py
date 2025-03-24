import json
from analizador_code import *

texto = """
int resta(int a, int b){
  while a > b;
    int c = a - b;
   if a <= b // b == a;
   return c;
  }
int suma(int a, int b){
  int c = a + b;
  print("hola_mundo");
  return c;
}
any main(int a){
  for (int i = c; i < a; i += b);
  return main;
}
"""

def imprimir_ast(nodo):
  if isinstance(nodo, NodoFunciones):
    return {"Funciones": [imprimir_ast(nodo.funcion)] + [imprimir_ast(nodo.funcion_siguiente)]}
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
  codigo_asm = arbol_ast.generar_codigo()
  print(codigo_asm)
  print('Análisis sintáctico exitoso')
  imprimir_ast(arbol_ast)
  print(json.dumps(imprimir_ast(arbol_ast), indent=1))
  
except SyntaxError as e:
  print(e)