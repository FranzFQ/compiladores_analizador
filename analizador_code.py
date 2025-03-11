import re
import pandas as pd
# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|while|for|return|class|def|print|range)\b',
    "KEY": r'\b(void|int|float|any)\b', 
    "BOOLEANS": r'\b(True|False)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+\b',
    "OPERATOR": r'[\+\-\*/=<>&]',  # Operadores básicos
    "DELIMITER": r'[(),;{}:]',  # Paréntesis, llaves, punto y coma
    "WHITESPACE": r'\s+'  # Espacios en blanco
}

def tokenize(text):
  patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
  patron_regex = re.compile(patron_general)

  tokens_encontrados = []

  for match in patron_regex.finditer(text):
      for token, valor in match.groupdict().items():
          if valor is not None and token != "WHITESPACE":
              tokens_encontrados.append((token, valor))

  return tokens_encontrados

class NodoAST:
  #Clase base para todos los nodos del AST
  pass

class NodoFunciones(NodoAST):
  #Nodo que representa una lista de funciones
  def __init__(self, funcion ,funcion_siguiente):
    self.funcion = funcion
    self.funcion_siguiente = funcion_siguiente

class NodoFuncion(NodoAST):
  #Nodo que representa una funcion
  def __init__(self, nombre, parametros, cuerpo):
    self.nombre = nombre
    self.parametro = parametros
    self.cuerpo = cuerpo

class NodoParametro(NodoAST):
  #Nodo que representa un parametro de funcion
  def __init__(self, tipo, nombre):
    self.tipo = tipo 
    self.nombre = nombre

class NodoAsignacion(NodoAST):
  #Nodo que representa una asignacion de variable
  def __init__(self, nombre, expresion):
    self.nombre = nombre
    self.expresion = expresion

class NodoOperacion(NodoAST):
  #Nodo que representa una operacion aritmetica
  def __init__(self, izquierda, operador, derecha):
    self.izquierda = izquierda
    self.derecha = derecha
    self.operador = operador

class NodoIf(NodoAST):
  #Nodo que representa una sentencia if
  def __init__(self, condicion):
    self.condicion = condicion

class NodoWhile(NodoAST):
  #Nodo que representa una sentencia while
  def __init__(self, condicion):
    self.condicion = condicion
  
class NodoFor(NodoAST):
  #Nodo que representa una sentencia for
  def __init__(self, expresion1, expresion2, expresion3):
    self.expresion1 = expresion1
    self.expresion2 = expresion2
    self.expresion3 = expresion3

class NodoPrint(NodoAST):
  #Nodo que representa una sentencia print
  def __init__(self, contenido):
    self.contenido = contenido

class NodoRetorno(NodoAST):
  #Nodo que representa la sentencia o instruccion de retorno
  def __init__(self, expresion):
    self.expresion = expresion

class NodoIdentificador(NodoAST):
  #Nodo que representa a un identificador
  def __init__(self, nombre):
    self.nombre = nombre

class NodoNumero(NodoAST):
  #Nodo que representa a un numero
  def __init__(self, valor):
    self.valor = valor

# Analizador sintáctico
class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0

  def obtener_token_actual(self):
    return self.tokens[self.pos] if self.pos < len(self.tokens) else None

  def coincidir(self, tipo_esperado):
    token_actual = self.obtener_token_actual()
    if token_actual and token_actual[0] == tipo_esperado:
      self.pos += 1
      return token_actual
    else:
      raise SyntaxError(f'Error sintáctico: se esperaba {tipo_esperado}, pero se encontró: {token_actual}')

  def parsear(self):
    # Punto de entrada del analizador: se espera una función
    return self.funcion()

  def funcion(self):
    # Gramática para una función: int IDENTIFICADOR (int IDENTIFICADOR*) {cuerpo}
    tipo_retorno = self.coincidir('KEY') # Tipo de retorno (ej. int)
    nombre_funcion = self.coincidir('IDENTIFIER') # Nombre de la función
    self.coincidir('DELIMITER') # Se espera un "("
    parametros = self.parametros()
    self.coincidir('DELIMITER') # Se espera un ")"
    self.coincidir('DELIMITER') # Se espera un "{"
    cuerpo = self.cuerpo()
    self.coincidir('DELIMITER') # Se espera un "}"
    if self.obtener_token_actual() and  self.obtener_token_actual()[0] == "KEY":
      return NodoFunciones(NodoFuncion(nombre_funcion, parametros, cuerpo), self.funcion())
    else:
      return NodoFuncion(nombre_funcion, parametros, cuerpo)

  def parametros(self):
    parametros = []
    # Reglas para parámetros: int IDENTIFICADOR(, int IDENTIFICADOR)*
    # Reglas para parámetros: int IDENTIFIER(, int IDENTIFIER)*
    tipo = self.coincidir('KEY') # Tipo del parámetro
    nombre = self.coincidir('IDENTIFIER') # Nombre del parámetro
    parametros.append(NodoParametro(tipo, nombre))
    while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
      self.coincidir('DELIMITER') # Espera una ","
      tipo = self.coincidir('KEY') # Tipo del parámetro
      nombre = self.coincidir('IDENTIFIER') # Nombre del parámetro
      parametros.append(NodoParametro(tipo, nombre))
    return parametros
  
  def cuerpo(self):
    instrucciones = []
    while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
      if self.obtener_token_actual()[1] == "return":
        instrucciones.append(self.retorno())
      elif self.obtener_token_actual()[0] == "KEY":
        instrucciones.append(self.asignacion())
      elif self.obtener_token_actual()[1] == "if":
        instrucciones.append(self.operation_IF())
      elif self.obtener_token_actual()[1] == "while":
        instrucciones.append(self.operation_while())
      elif self.obtener_token_actual()[1] == "for":
        instrucciones.append(self.operation_for())
      elif self.obtener_token_actual()[1] == "print": 
        instrucciones.append(self.operation_print())
    return instrucciones

  def asignacion(self):
    self.coincidir("KEY")
    nombre = self.coincidir("IDENTIFIER")
    self.coincidir("OPERATOR")
    expresion = self.expresion()
    self.coincidir("DELIMITER")
    return NodoAsignacion(nombre, expresion)
  
  def expresion(self):
    izquierda = self.termino()
    while self.obtener_token_actual() and self.obtener_token_actual()[0] == "OPERATOR":
      operador = self.coincidir("OPERATOR")
      if self.obtener_token_actual()[0] == "OPERATOR":
        operador += self.coincidir("OPERATOR")
      derecha = self.termino()
      izquierda = NodoOperacion(izquierda, operador, derecha)
    return izquierda

  def operation_IF(self):
    self.coincidir("KEYWORD")
    condicion = self.expresion()
    self.coincidir("DELIMITER")
    return NodoIf(condicion)
    
  def operation_print(self):
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    contenido = self.termino()
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    return NodoPrint(contenido)

  def operation_while(self):
    self.coincidir("KEYWORD")
    if self.obtener_token_actual()[0] == "IDENTIFIER":
      condicion = self.expresion()
    elif self.obtener_token_actual()[0] == "BOOLEAN":
      condicion = self.coincidir("BOOLEAN")
    self.coincidir("DELIMITER")
    return NodoWhile(condicion)
  
  def operation_for(self):
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    expresion1 = self.asignacion()
    expresion2 = self.expresion()
    self.coincidir("DELIMITER")
    expresion3 = self.expresion()
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    return NodoFor(expresion1, expresion2, expresion3)
  
  def retorno(self):
    self.coincidir("KEYWORD")
    expresion = self.coincidir("IDENTIFIER")
    if self.obtener_token_actual()[0] == "DELIMITER":
      self.coincidir("DELIMITER")
      return NodoRetorno(expresion)
    else:
      return NodoRetorno(self.expresion())

  def termino(self):
    token = self.obtener_token_actual()
    if token[0] == "IDENTIFIER":
      return NodoIdentificador(self.coincidir("IDENTIFIER"))
    elif token[0] == "NUMBER":
      return NodoNumero(int(self.coincidir("NUMBER")))
    else:
      raise SyntaxError(f"Error de sintaxis: se esperaba un identificador o un número, pero se encontró {token}")
    