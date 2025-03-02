import re
import pandas as pd

texto = """
int resta(int a, int b) {
  def prueba():
    if a <= b // b == a;
      while True;
        print("Hello");
  int c = a * a / b;
  return c;
}
"""

# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|while|for|return|int|float|void|class|def|print|range)\b',
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

tokens = tokenize(texto)
tabla = pd.DataFrame(tokens, columns=['Tipo', 'Valor'])

resumen = pd.DataFrame(tabla['Tipo'].value_counts())
resumen['Encontrado'] = ''

for x, fila in resumen.iterrows():
  listado = tabla[tabla['Tipo'] == x]['Valor'].tolist()
  resumen.at[x, 'Encontrado'] = listado
  resumen.at[x, 'Encontrado'] = ', '.join(listado)


def parse(tokens):
  def consume(tipo_esperado):
    global token_actual
    if token_actual[0] == tipo_esperado:
      global indice_token
      token_actual = tokens[indice_token]
      indice_token += 1
    else:
      raise Exception(f'Se esperaba {tipo_esperado} pero se obtuvo {token_actual[1]}')

    # Reglas de produccion como funciones

    def E():
      # Implementar la regla de produccion de expresiones
      T()
      while token_actual[0] in ['+', '-']:
        operador = token_actual[1]
        consume('Operador')
        T()
      pass
    def T():
      # Implementar la regla de produccion de terminos
      pass
    def F():
      # Implementar la regla de produccion de factores
      pass
    # Inicialización de variables
    # global token_actual, indice_token
    token_actual = tokens[0]
    indice_token[1]
    # Iniciar el análisis
    E()

    # Si se consumieron todos los tokens, el análisis fue exitoso
    if indice_token == len(tokens):
      return True
    else:
      raise Exception('Error de sintaxis')


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
    self.funcion()

  def funcion(self):
    # Gramática para una función: int IDENTIFICADOR (int IDENTIFICADOR*) {cuerpo}
    tipo_retorno = self.coincidir('KEYWORD') # Tipo de retorno (ej. int)
    nombre_funcion = self.coincidir('IDENTIFIER') # Nombre de la función
    self.coincidir('DELIMITER') # Se espera un "("
    parametros = self.parametros()
    self.coincidir('DELIMITER') # Se espera un ")"
    self.coincidir('DELIMITER') # Se espera un "{"
    cuerpo = self.cuerpo()
    self.coincidir('DELIMITER') # Se espera un "}"
    return NodoFuncion(nombre_funcion, parametros, cuerpo)

  def parametros(self):
    parametros = []
    # Reglas para parámetros: int IDENTIFICADOR(, int IDENTIFICADOR)*
    # Reglas para parámetros: int IDENTIFIER(, int IDENTIFIER)*
    tipo = self.coincidir('KEYWORD') # Tipo del parámetro
    nombre = self.coincidir('IDENTIFIER') # Nombre del parámetro
    parametros.append(NodoParametro(tipo, nombre))
    while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
      self.coincidir('DELIMITER') # Espera una ","
      tipo = self.coincidir('KEYWORD') # Tipo del parámetro
      nombre = self.coincidir('IDENTIFIER') # Nombre del parámetro
      parametros.append(NodoParametro(tipo, nombre))
    return parametros

  def cuerpo(self):
    instrucciones = []
    # Gramática para el cuerpo de la función: return IDENTIFIER OPERATOR IDENTIFIER
    if self.obtener_token_actual()[1] == "if":
      self.coincidir("KEYWORD")
      self.operation_IF()

    elif self.obtener_token_actual()[1] == "return":
      self.coincidir("KEYWORD")
      self.operation_return()

    elif self.obtener_token_actual()[1] == "print":
      self.coincidir("KEYWORD")
      self.operation_print()

    elif self.obtener_token_actual()[1] == "int" or self.obtener_token_actual()[1] == "float":
      self.coincidir("KEYWORD")
      self.operation_X()

    elif self.obtener_token_actual()[1] == "while":
      self.coincidir("KEYWORD")
      self.operation_while()

    elif self.obtener_token_actual()[1] == "for":
      self.coincidir("KEYWORD")
      self.operation_for()

    elif self.obtener_token_actual()[1] == "def":
      self.coincidir("KEYWORD")
      self.operration_def()

    elif self.obtener_token_actual()[1] == "}":
      return instrucciones
    
    return self.cuerpo()

  def operation_return(self):
    self.coincidir("IDENTIFIER")
    if self.obtener_token_actual()[0] == "DELIMITER":
      self.coincidir("DELIMITER")
      return 0
    else:
      self.coincidir("OPERATOR")
      return self.operation_return()
  
  def operation_X(self):
    self.coincidir("IDENTIFIER")
    if self.obtener_token_actual()[0] == "DELIMITER":
      self.coincidir("DELIMITER")
      return 0
    else:
      self.coincidir("OPERATOR")
      return self.operation_X()

  def operation_IF(self):
      self.coincidir("IDENTIFIER")
      self.coincidir('OPERATOR')
      if self.obtener_token_actual()[0] == "OPERATOR":
        self.coincidir("OPERATOR")
      else:
        pass
      self.coincidir("IDENTIFIER")
      if self.obtener_token_actual()[0] == "DELIMITER":
        self.coincidir("DELIMITER")
        return 0
      else:
        self.coincidir("OPERATOR")
        self.coincidir("OPERATOR")
        self.operation_IF()
        return 0
    
  def operation_print(self):
    self.coincidir("DELIMITER")
    self.coincidir("IDENTIFIER")
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    return 0

  def operation_while(self):
    if self.obtener_token_actual()[0] == "BOOLEANS":
      self.coincidir("BOOLEANS")
      self.coincidir("DELIMITER")
    else:
      self.operation_IF()
  
    return 0
  def operation_for(self):
    self.coincidir("IDENTIFIER")
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    self.coincidir("IDENTIFIER")
    self.coincidir("DELIMITER")
    self.coincidir("IDENTIFIER")
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    return 0
  
  def operration_def(self):
    self.coincidir("IDENTIFIER")
    self.coincidir("DELIMITER")
    if self.obtener_token_actual()[0] == "DELIMITER":
      self.coincidir("DELIMITER")
      self.coincidir("DELIMITER")
      return 0
    else:
      self.coincidir("IDENTIFIER")
      self.coincidir("DELIMITER")
      self.coincidir("DELIMITER")
      return 0

class NodoAST:
  #Clase base para todos los nodos del AST
  pass

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
    self.izquerda = izquierda
    self.derecha = derecha
    self.operador = operador

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

  

# Aquí se probará el analizador sintáctico
try:
  print('Se inicia el análisis sintáctico')
  parser = Parser(tokens)
  parser.parsear()
  print('Análisis sintáctico exitoso')
except SyntaxError as e:
  print(e)