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

declaracion_variables = []

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
  def __init__(self):
    self.funcion = []
  
  def agregar(self, funcion):
    self.funcion.append(funcion)

  def traducir(self):
    text = ""
    for f in self.funcion:
      text += f.traducir() + "\n\n"
    return text

  def generar_codigo(self):
    for f in self.funcion:
      f.generar_codigo()
    codigo = ".data\n\n"
    codigo += "".join(declaracion_variables) + "\n"
    codigo += ".code\n\n"
    codigo += ";Inicio del programa\n"
    codigo += "CALL main ; Ejecuta la funcion main\n"
    codigo += "mov ah, 4ch ; finaliza el programa \nint 21h\n\n"
    codigo += "\n\n".join(f.generar_codigo() for f in self.funcion)
    return codigo
  
class NodoFuncion(NodoAST):
  #Nodo que representa una funcion
  def __init__(self, nombre, parametros, cuerpo):
    self.nombre = nombre
    self.parametro = parametros
    self.cuerpo = cuerpo

  def traducir(self):
    params = ",".join(p.traducir() for p in self.parametro)
    cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
    return f"def {self.nombre[1]}({params}):\n    {cuerpo}"
  
  def generar_codigo(self):
    codigo = f"{self.nombre[1]} proc\n"
    codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
    codigo += f"    \n{self.nombre[1]} endp"
    return codigo

class NodoParametro(NodoAST):
  #Nodo que representa un parametro de funcion
  def __init__(self, tipo, nombre):
    self.tipo = tipo 
    self.nombre = nombre

  def traducir(self):
    return self.nombre[1]

class NodoAsignacion(NodoAST):
  #Nodo que representa una asignacion de variable
  def __init__(self, nombre, expresion):
    self.nombre = nombre
    self.expresion = expresion
    
  def traducir(self):
    return f"{self.nombre[1]} = {self.expresion.traducir()}"
  
  def generar_codigo(self):
    codigo = self.expresion.generar_codigo()
    if codigo is None:
      codigo = ""
    if isinstance(self.expresion, NodoNumero):
      declaracion_variables.append(f"{self.nombre[1]} dw ?\n")

    if isinstance(self.expresion, NodoIdentificador):
      declaracion_variables.append(f"{self.nombre[1]} dw ?\n")

    codigo += f"\n    mov {self.nombre[1]}, ax; guardar resultado en {self.nombre[1]}"
    return codigo

class NodoOperacion(NodoAST):
  #Nodo que representa una operacion aritmetica
  def __init__(self, izquierda, operador, derecha):
    self.izquierda = izquierda
    self.derecha = derecha
    self.operador = operador

  def traducir(self):
    return f"{self.izquierda.traducir()} {self.operador[1]} {self.derecha.traducir()}"
  
  def generar_codigo(self):
    codigo = []
    codigo.append(self.izquierda.generar_codigo())
    codigo.append("    push ax ; guardar en la pila")
    
    codigo.append(self.derecha.generar_codigo())
    codigo.append("    pop bx ; cargar en bx el valor de la pila" )
    
    if self.operador[1] == "+":
      codigo.append("    add ax, bx ; ax = ax + bx \n")
    elif self.operador[1] == "-":
      codigo.append("    sub ax, bx ; ax = ax - bx")
      codigo.append("    neg ax ; negar ax\n")
    elif self.operador[1] == "*":
      codigo.append("    mul bx ; ax = ax * bx\n")
    elif self.operador[1] == "/":
      codigo.append("    div dx, dx \n    div bx ; ax = ax / bx\n")
      
    return "\n".join(codigo)
    
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
  def __init__(self, condicion, cuerpo):
    self.condicion = condicion
    self.cuerpo = cuerpo

  def traducir(self):
    cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
    return f"if {self.condicion.traducir()}: \n       {cuerpo}"

  def generar_codigo(self):
    codigo = []
    codigo.append(self.condicion.izquierda.generar_codigo())
    codigo.append("    push ax ; guardar en la pila")
    
    codigo.append(self.condicion.derecha.generar_codigo())
    codigo.append("    pop bx ; cargar en bx el valor de la pila" )
    if self.condicion.operador[1] == ">":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    jg a_mayor_b ;salto si ax es mayor que bx\n    jmp fin ;Si ax no es mayor a bx   \n    a_mayor_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    elif self.condicion.operador[1] == "<":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    jl a_menor_b ;salto si ax es menor que bx\n    jmp fin ;Si ax no es menor a bx   \n    a_menor_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    elif self.condicion.operador[1] == "==":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    je a_igual_b ;salto si ax es igual a bx\n    jmp fin ;Si ax no es igual a bx   \n    a_igual_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    elif self.condicion.operador[1] == "!=":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    jne a_diferente_b ;salto si ax es diferente a bx\n    jmp fin ;Si ax no es diferente a bx   \n    a_diferente_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    elif self.condicion.operador[1] == ">=":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    jge a_mayor_igual_b ;salto si ax es mayor o igual a bx\n    jmp fin ;Si ax no es mayor o igual a bx   \n    a_mayor_igual_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    elif self.condicion.operador[1] == "<=":
      codigo.append(f"    cmp ax, bx ; compara ax a con bx\n    jle a_menor_igual_b ;salto si ax es menor o igual a bx\n    jmp fin ;Si ax no es menor o igual a bx   \n    a_menor_igual_b: ;Realiza lo demas\n")
      codigo.append("    ".join([p.generar_codigo() for p in self.cuerpo]))
      codigo.append("    fin: ;Realiza todo lo que no este dentro del if")
    return "\n".join(codigo)

class NodoWhile(NodoAST):
  #Nodo que representa una sentencia while
  def __init__(self, condicion, cuerpo):
    self.condicion = condicion
    self.cuerpo = cuerpo

  def traducir(self):
    cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
    return f"while {self.condicion.traducir()}: \n       {cuerpo}"


  def generar_codigo(self):
    codigo = []
    codigo.append(f"    While:\n")
    codigo.append("    ".join([c.generar_codigo() for c in self.cuerpo]))
    codigo.append("    cmp ax, bx\n    jle While\n")
    return codigo
  
class NodoFor(NodoAST):
  #Nodo que representa una sentencia for
  def __init__(self, expresion1, expresion2, expresion3, cuerpo):
    self.expresion1 = expresion1
    self.expresion2 = expresion2
    self.expresion3 = expresion3
    self.cuerpo = cuerpo

  def traducir(self):
    variable = self.expresion1.nombre
    limite = self.expresion2.derecha.nombre
    return f"for {variable[1]} in range ({str(limite[1])}):"
  
  def generar_codigo(self):
      codigo = []
      codigo.append(f"    For:\n")
      codigo.append("    ".join([c.generar_codigo() for c in self.cuerpo]))
      codigo.append("    cmp ax, bx\n    jle For\n")
      return codigo

class NodoPrint(NodoAST):
  #Nodo que representa una sentencia print
  def __init__(self, contenido):
    self.contenido = contenido

  def traducir(self):
    return f"print ({self.contenido.traducir()})"

  def generar_codigo(self):
    return f"    mov ah, 09h ;Crea el espacio para mostrar\n    mov dx, offset {self.contenido.nombre[1]} + '$';mueve el contenido para que los muestre\n    int 21h; intervencion 21 para que muestre\n"

class NodoRetorno(NodoAST):
  #Nodo que representa la sentencia o instruccion de retorno
  def __init__(self, expresion):
    self.expresion = expresion

  def traducir(self):
    return f"return {self.expresion[1]}"
  
  def generar_codigo(self):
    declaracion_variables.append(f"{self.expresion[1]} dw ?\n")
    return '\n    ret ; retorno desde la subrutina'

class NodoIdentificador(NodoAST):
  #Nodo que representa a un identificador
  def __init__(self, nombre):
    self.nombre = nombre

  def traducir(self):
    return self.nombre[1]
  
  def generar_codigo(self):
    return f'    mov ax, [{self.nombre[1]}] ; cargar valor de {self.nombre[1]} en ax'

class NodoNumero(NodoAST):
  #Nodo que representa a un numero
  def __init__(self, valor):
    self.valor = valor

  def traducir(self):
    return str(self.valor[1])
  
  def generar_codigo(self):
    return f'    mov ax, [{str(self.valor[1])}] ; cargar numero {str(self.valor[1])} en ax'
  
class NodoFuncionAnidada(NodoAST):
  def __init__(self, nombre, parametros):
    self.nombre = nombre
    self.parametros = parametros
  
  def traducir(self):
    return f"{self.nombre[1]}({self.parametros})"

  def generar_codigo(self):
    return f"    CALL {self.nombre[1]}"

# Analizador sintáctico
class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0
    self.funciones = []

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
    self.funciones.append(nombre_funcion[1])
    self.coincidir('DELIMITER') # Se espera un "("
    if self.obtener_token_actual()[0] == "DELIMITER":
      parametros = []
    else:
      parametros = self.parametros()
    self.coincidir('DELIMITER') # Se espera un ")"
    self.coincidir('DELIMITER') # Se espera un "{"
    cuerpo = self.cuerpo()
    self.coincidir('DELIMITER') # Se espera un "}"
    if self.obtener_token_actual() and  self.obtener_token_actual()[0] == "KEY":
      funciones = NodoFunciones()
      funcion = NodoFuncion(nombre_funcion, parametros, cuerpo)
      funciones.agregar(funcion)
      funciones.agregar(self.funcion())
      return funciones
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
      elif self.obtener_token_actual()[0] == "IDENTIFIER":
        instrucciones.append(self.funcion_interna())
      
    return instrucciones

  def asignacion(self):
    self.coincidir("KEY")
    nombre = self.coincidir("IDENTIFIER")
    self.coincidir("OPERATOR")
    verificacion = self.verificacion()
    if verificacion == None:
      expresion = self.expresion()
      self.coincidir("DELIMITER")
    else:
      expresion = verificacion
    return NodoAsignacion(nombre, expresion)
  
  def verificacion(self):
    expresion = None
    for i in self.funciones:
      if self.obtener_token_actual()[1] == i:
        expresion = self.funcion_interna()
        break
    return expresion
  
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
    cuerpo = []
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    condicion = self.expresion()
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
      if self.obtener_token_actual()[1] == "return":
        cuerpo.append(self.retorno())
      elif self.obtener_token_actual()[0] == "KEY":
        cuerpo.append(self.asignacion())
      elif self.obtener_token_actual()[1] == "if":
        cuerpo.append(self.operation_IF())
      elif self.obtener_token_actual()[1] == "while":
        cuerpo.append(self.operation_while())
      elif self.obtener_token_actual()[1] == "for":
        cuerpo.append(self.operation_for())
      elif self.obtener_token_actual()[1] == "print": 
        cuerpo.append(self.operation_print())
      elif self.obtener_token_actual()[0] == "IDENTIFIER":
        cuerpo.append(self.funcion_interna())
    self.coincidir("DELIMITER")
    return NodoIf(condicion, cuerpo)
    
  def operation_print(self):
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    contenido = self.termino()
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    return NodoPrint(contenido)

  def operation_while(self):
    cuerpo = []
    self.coincidir("KEYWORD")
    if self.obtener_token_actual()[0] == "IDENTIFIER":
      condicion = self.expresion()
    elif self.obtener_token_actual()[0] == "BOOLEAN":
      condicion = self.coincidir("BOOLEAN")
    while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
      if self.obtener_token_actual()[1] == "return":
        cuerpo.append(self.retorno())
      elif self.obtener_token_actual()[0] == "KEY":
        cuerpo.append(self.asignacion())
      elif self.obtener_token_actual()[1] == "if":
        cuerpo.append(self.operation_IF())
      elif self.obtener_token_actual()[1] == "while":
        cuerpo.append(self.operation_while())
      elif self.obtener_token_actual()[1] == "for":
        cuerpo.append(self.operation_for())
      elif self.obtener_token_actual()[1] == "print": 
        cuerpo.append(self.operation_print())
      elif self.obtener_token_actual()[0] == "IDENTIFIER":
        cuerpo.append(self.funcion_interna())
    self.coincidir("DELIMITER")
    return NodoWhile(condicion, cuerpo)
  
  def operation_for(self):
    cuerpo = []
    self.coincidir("KEYWORD")
    self.coincidir("DELIMITER")
    expresion1 = self.asignacion()
    expresion2 = self.expresion()
    self.coincidir("DELIMITER")
    expresion3 = self.expresion()
    self.coincidir("DELIMITER")
    self.coincidir("DELIMITER")
    while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
      if self.obtener_token_actual()[1] == "return":
        cuerpo.append(self.retorno())
      elif self.obtener_token_actual()[0] == "KEY":
        cuerpo.append(self.asignacion())
      elif self.obtener_token_actual()[1] == "if":
        cuerpo.append(self.operation_IF())
      elif self.obtener_token_actual()[1] == "while":
        cuerpo.append(self.operation_while())
      elif self.obtener_token_actual()[1] == "for":
        cuerpo.append(self.operation_for())
      elif self.obtener_token_actual()[1] == "print": 
        cuerpo.append(self.operation_print())
      elif self.obtener_token_actual()[0] == "IDENTIFIER":
        cuerpo.append(self.funcion_interna())
    self.coincidir("DELIMITER")
    return NodoFor(expresion1, expresion2, expresion3, cuerpo)
  
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
      return NodoNumero(self.coincidir("NUMBER"))
    else:
      raise SyntaxError(f"Error de sintaxis: se esperaba un identificador o un número, pero se encontró {token}")
    
  def funcion_interna(self):
    nombre = self.coincidir("IDENTIFIER")
    if self.obtener_token_actual()[0] == "DELIMITER ":
      self.coincidir("DELIMITER")
      parametros = ""
      self.coincidir("DELIMITER")
    else:
      self.coincidir("DELIMITER")
      parametros = ""
      while True:
        parametros += self.coincidir("IDENTIFIER")[1]
        if self.obtener_token_actual()[1] != ")":
          parametros += self.coincidir("DELIMITER")[1]
        else:
          self.coincidir("DELIMITER")
        if self.obtener_token_actual()[1] == ";":
          self.coincidir("DELIMITER")
          break
    return NodoFuncionAnidada(nombre, parametros)