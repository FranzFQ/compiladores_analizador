import json
import analizador_code

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
  if isinstance(nodo, analizador_code.NodoFunciones):
    return {"Funciones": [imprimir_ast(nodo.funcion)] + [imprimir_ast(nodo.funcion_siguiente)]}
  elif isinstance(nodo, analizador_code.NodoFuncion):
    return {"Funcion": nodo.nombre, 
            "Parametros": [imprimir_ast(p) for p in nodo.parametro],
            "Cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]}
  elif isinstance(nodo, analizador_code.NodoParametro):
    return {"Parametro": nodo.nombre, "Tipo": nodo.tipo} 
  elif isinstance(nodo, analizador_code.NodoAsignacion):
    return {"Asignacion": nodo.nombre, "Expresion": imprimir_ast(nodo.expresion)}
  elif isinstance(nodo, analizador_code.NodoOperacion):
    return {"Operacion": nodo.operador, 
            "Izquierda": imprimir_ast(nodo.izquierda),
            "Derecha": imprimir_ast(nodo.derecha)}
  elif isinstance(nodo, analizador_code.NodoRetorno):
    return {"Return": nodo.expresion}
  elif isinstance(nodo, analizador_code.NodoIdentificador):
    return {"Identificador": nodo.nombre}
  elif isinstance(nodo, analizador_code.NodoNumero):
    return {"Numero": nodo.valor}
  elif isinstance(nodo, analizador_code.NodoIf):
    return {"If": imprimir_ast(nodo.condicion)}
  elif isinstance(nodo, analizador_code.NodoWhile):
    return {"While": imprimir_ast(nodo.condicion)}
  elif isinstance(nodo, analizador_code.NodoFor):
    return {"For": [imprimir_ast(nodo.expresion1), imprimir_ast(nodo.expresion2), imprimir_ast(nodo.expresion3)]}
  elif isinstance(nodo, analizador_code.NodoPrint):
    return {"Print": imprimir_ast(nodo.contenido)}
  return {}

# Aquí se probará el analizador sintáctico
try:
  tokens = analizador_code.tokenize(texto)
  print('Se inicia el análisis sintáctico')
  parser = analizador_code.Parser(tokens)
  arbol_ast = parser.parsear()
  print('Análisis sintáctico exitoso')
  imprimir_ast(arbol_ast)
  print(json.dumps(imprimir_ast(arbol_ast), indent=1))
  
except SyntaxError as e:
  print(e)