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
  def traducir(self):
    raise NotImplementedError("Métpdp traducir() no implementado en este nodo.")
  
  def generar_codigo(self):
    raise NotImplementedError("Método generar_codigo() no implementado en este nodo.")

class NodoFunciones(NodoAST):
  #Nodo que representa una lista de funciones
  def _init_(self, funcion ,funcion_siguiente):
    self.funcion = funcion
    self.funcion_siguiente = funcion_siguiente

class NodoFuncion(NodoAST):
  #Nodo que representa una funcion
  def _init_(self, nombre, parametros, cuerpo):
    self.nombre = nombre
    self.parametro = parametros
    self.cuerpo = cuerpo

  def traducir(self):
    params = ",".join(p.traducir()[1] for p in self.parametros)
    cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
    return f"def {self.nombre}({params}):\n    {cuerpo}"

class NodoParametro(NodoAST):
  #Nodo que representa un parametro de funcion
  def _init_(self, tipo, nombre):
    self.tipo = tipo 
    self.nombre = nombre

  def traducir(self):
    return self.nombre

class NodoAsignacion(NodoAST):
  #Nodo que representa una asignacion de variable
  def _init_(self, nombre, expresion):
    self.nombre = nombre
    self.expresion = expresion
    
  def traducir(self):
    return f"{self.nombre} = {self.expresion.traducir()}"
  
  def generar_codigo(self):
    codigo = self.expresion.generar_codigo()
    codigo += f"\n    mov [{self.nombre[1]}], eax; guardar resultado en {self.nombre[1]}"

class NodoOperacion(NodoAST):
  #Nodo que representa una operacion aritmetica
  def _init_(self, izquierda, operador, derecha):
    self.izquierda = izquierda
    self.derecha = derecha
    self.operador = operador

  def traducir(self):
    return f"{self.izquierda.traducir()} {self.operador[1]} {self.derecha.traducir()}"
  
  def generar_codigo(self):
    codigo = []
    codigo.append(self.izquierda.generar_codigo())
    codigo.append("       push eax ; guardar en la pila")
    
    codigo.append(self.derecha.generar_codigo())
    codigo.append("       pop ebx ; cargar en ebx el valor de la pila")
    
    if self.operador[1] == "+":
      codigo.append("       add eax, ebx ; eax = eax + ebx")
    elif self.operador[1] == "-":
      codigo.append("       sub eax, ebx ; eax = eax - ebx")
      codigo.append("       neg eax ; negar eax")
      return 
    


  
  def optimizar(self):
    if isinstance(self.izquierda, NodoOperacion):
      izquierda = self.izquierda.optimizar()
    else:
      izquierda =  self.izquierda
      
    if isinstance(self.derecha, NodoOperacion):
      derecha = self.derecha.optimizar()
    else:
      derecha =  self.derecha
    
    #Si ambos operandos son numeros, evaluamos la operacion
    if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
      if self.operador == '+':
        return NodoNumero(izquierda.valor + derecha.valor)
      elif self.operador == '-':
        return NodoNumero(izquierda.valor - derecha.valor)
      elif self.operador == '*':
        return NodoNumero(izquierda.valor * derecha.valor)
      elif self.operador == '/' and derecha.valor != 0:
        return NodoNumero(izquierda.valor / derecha.valor)
      
      # simplificacion algebraica
      if self.operador == '*' and isinstance(derecha, NodoNumero) and derecha.valor == 1:
        return izquierda
      if self.operador == '*' and isinstance(izquierda, NodoNumero) and derecha.valor == 1:
        return derecha
      if self.operador == '+' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
        return izquierda
      if self.operador == '+' and isinstance(izquierda, NodoNumero) and derecha.valor == 0:
        return derecha

      #Si no se puede optimizar mas, devolvemos la misma operacion
      return NodoOperacion(izquierda, self.operador, derecha)

class NodoIf(NodoAST):
  #Nodo que representa una sentencia if
  def _init_(self, condicion):
    self.condicion = condicion

class NodoWhile(NodoAST):
  #Nodo que representa una sentencia while
  def _init_(self, condicion):
    self.condicion = condicion
  
class NodoFor(NodoAST):
  #Nodo que representa una sentencia for
  def _init_(self, expresion1, expresion2, expresion3):
    self.expresion1 = expresion1
    self.expresion2 = expresion2
    self.expresion3 = expresion3

class NodoPrint(NodoAST):
  #Nodo que representa una sentencia print
  def _init_(self, contenido):
    self.contenido = contenido

class NodoRetorno(NodoAST):
  #Nodo que representa la sentencia o instruccion de retorno
  def _init_(self, expresion):
    self.expresion = expresion

  def traducir(self):
    return f"return {self.expresion.traducir()}"
  
  def generar_codigo(self):
    return self.expresion.generar_codigo() + "\n    ret ; retorno desde la subrutina"

class NodoIdentificador(NodoAST):
  #Nodo que representa a un identificador
  def _init_(self, nombre):
    self.nombre = nombre

  def traducir(self):
    return self.nombre

class NodoNumero(NodoAST):
  #Nodo que representa a un numero
  def _init_(self, valor):
    self.valor = valor

  def traducir(self):
    return str(self.valor)
  
  def generar_codigo(self):
    return f'       mov eax, {self.valor[1]} ; cargar numero {self.valor[1]} en eax'

# Analizador sintáctico
class Parser:
  def _init_(self, tokens):
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
    