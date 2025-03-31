import json
from analizador_code import *

texto = """
int suma (int a, int b) {
  if (a > b){
    return a;
  }
  return b;
}

int main (){
  int c = a + b;
  int a = suma(a, b);
  for (int i = 0, i < b, i += 1){
  }
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
  imprimir_ast(arbol_ast)
  print('Análisis sintáctico exitoso')
  
except SyntaxError as e:
  print(e)