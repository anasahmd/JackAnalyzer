from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable

class CompilationEngine:
  
  def __init__(self, input_file, output_file) -> None:
    self.input_file = input_file
    self.output_file = output_file
    self.tokenizer = JackTokenizer(input_file)
    self.symbol_table = SymbolTable()
  
  def process(self, string: str):
    # Consider changing current token accessor
    if (self.tokenizer.current_token == string):
      self.printXMLToken()
    else:
      print('Syntax Error')
      print(string)
      print(self.tokenizer.current_token)
      exit(1)
    
      
  def printXMLToken(self):
    if self.tokenizer.tokenType() == 'KEYWORD':
      self.output_file.writelines(['<keyword> ', self.tokenizer.keyWord(), ' </keyword>', '\n'])
      
    elif self.tokenizer.tokenType() == 'SYMBOL':
      alternate_symbol = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
      symbol = self.tokenizer.symbol()
      if alternate_symbol.get(symbol):
        self.output_file.writelines(['<symbol> ', alternate_symbol[symbol], ' </symbol>', '\n'])
      else:
        self.output_file.writelines(['<symbol> ', symbol, ' </symbol>', '\n'])
    
    elif self.tokenizer.tokenType() == 'IDENTIFIER':
      self.output_file.writelines(['<identifier> ', self.tokenizer.identifier(), ' </identifier>', '\n'])
      
    elif self.tokenizer.tokenType() == 'INT_CONST':
      self.output_file.writelines(['<integerConstant> ', self.tokenizer.intVal(), ' </integerConstant>', '\n'])
      
    elif self.tokenizer.tokenType() == 'STRING_CONST':
      self.output_file.writelines(['<stringConstant> ', self.tokenizer.stringVal(), ' </stringConstant>', '\n'])
      
    self.tokenizer.advance()
      
  
  def compileClass(self):
    self.output_file.write('<class>\n')
    self.process('class')
    self.printXMLToken()
    self.process('{')
    while self.tokenizer.current_token in ('static', 'field'):
      self.compileClassVarDec()
    while self.tokenizer.current_token in ('constructor', 'function', 'method'):
      self.compileSubroutine()
    self.process('}')
    self.output_file.write('</class>\n')
    self.symbol_table.resetClassTable()
    
  def compileClassVarDec(self):
    self.output_file.write('<classVarDec>\n')
    if self.tokenizer.current_token in ('static', 'field'):
      kind =  self.tokenizer.current_token.upper()
      self.printXMLToken()
      type = self.tokenizer.current_token
      self.printXMLToken()
      name = self.tokenizer.current_token
      self.symbol_table.define(name, type, kind)
      self.printXMLToken()
      while self.tokenizer.current_token == ',':
        self.process(',')
        name = self.tokenizer.current_token
        self.symbol_table.define(name, type, kind)
        self.printXMLToken()
      self.process(';')
    self.output_file.write('</classVarDec>\n')

  def compileSubroutine(self):
    self.output_file.write('<subroutineDec>\n')
    if self.tokenizer.current_token in ('constructor', 'function', 'method'):
      self.printXMLToken()
      self.printXMLToken()
      self.printXMLToken()
      self.process('(')
      self.compileParameterList()
      self.process(')')
      self.compileSubroutineBody()
    self.output_file.write('</subroutineDec>\n')  
    self.symbol_table.resetSubroutineTable()
  
  def compileParameterList(self):
    self.output_file.write('<parameterList>\n')
    # Checks if parameterList is not empty
    if self.tokenizer.current_token != ')':
      type = self.tokenizer.current_token
      self.printXMLToken()
      name = self.tokenizer.current_token
      self.printXMLToken()
      self.symbol_table.define(name, type, 'ARG')
      while self.tokenizer.current_token == ',':
        self.printXMLToken()
        type = self.tokenizer.current_token
        self.printXMLToken()
        name = self.tokenizer.current_token
        self.symbol_table.define(name, type, 'ARG')
        self.printXMLToken()
    self.output_file.write('</parameterList>\n')

  def compileSubroutineBody(self):
    self.output_file.write('<subroutineBody>\n')
    self.process('{')
    while self.tokenizer.current_token == 'var':
      self.compileVarDec()
    self.compileStatements()
    self.process('}')
    self.output_file.write('</subroutineBody>\n')

  def compileVarDec(self):
    self.output_file.write('<varDec>\n')
    self.printXMLToken()
    type =  self.tokenizer.current_token
    self.printXMLToken()
    name = self.tokenizer.current_token
    self.symbol_table.define(name, type, 'VAR')
    self.printXMLToken()
    while self.tokenizer.current_token == ',':
      self.printXMLToken()
      name = self.tokenizer.current_token
      self.symbol_table.define(name, type, 'VAR')
      self.printXMLToken()
    self.process(';')
    self.output_file.write('</varDec>\n')
  
  def compileStatements(self):
    self.output_file.write('<statements>\n')
    while self.tokenizer.current_token in ('let', 'if', 'while', 'do', 'return'):
      if self.tokenizer.current_token == 'let':
        self.compileLet()
      elif self.tokenizer.current_token == 'if':
        self.compileIf()
      elif self.tokenizer.current_token == 'while':
        self.compileWhile()
      elif self.tokenizer.current_token == 'do':
        self.compileDo()
      elif self.tokenizer.current_token == 'return':
        self.compileReturn()     
    self.output_file.write('</statements>\n')
  
  def compileLet(self):
    self.output_file.write('<letStatement>\n')
    self.process('let')
    self.printXMLToken()
    if self.tokenizer.current_token == '[':
      self.process('[')
      self.compileExpression()
      self.process(']')
    self.process('=')
    self.compileExpression()
    self.process(';')
    self.output_file.write('</letStatement>\n')

  def compileIf(self):
    self.output_file.write('<ifStatement>\n')
    self.process('if')
    self.process('(')
    self.compileExpression()
    self.process(')')
    self.process('{')
    self.compileStatements()
    self.process('}')
    # Process else conditionally
    if self.tokenizer.current_token == 'else':
      self.printXMLToken()
      self.process('{')
      self.compileStatements()
      self.process('}')
    self.output_file.write('</ifStatement>\n')
      
  def compileWhile(self):
    self.output_file.write('<whileStatement>\n')
    self.process('while')
    self.process('(')
    self.compileExpression()
    self.process(')')
    self.process('{')
    self.compileStatements()
    self.process('}')
    self.output_file.write('</whileStatement>\n')
    
  def compileDo(self):
    self.output_file.write('<doStatement>\n')
    self.process('do')
    self.printXMLToken()
    if self.tokenizer.current_token == '.':
      self.printXMLToken()
      self.printXMLToken()
    self.process('(')
    self.compileExpressionList()
    self.process(')')
    self.process(';')
    self.output_file.write('</doStatement>\n')
  
  def compileReturn(self):
    self.output_file.write('<returnStatement>\n')
    self.process('return')
    if (self.tokenizer.current_token != ';'):
      self.compileExpression()
    self.process(';')
    self.output_file.write('</returnStatement>\n')
  
  def compileExpression(self):
    self.output_file.write('<expression>\n')
    self.compileTerm()
    while self.tokenizer.current_token in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
      self.printXMLToken()
      self.compileTerm()
    self.output_file.write('</expression>\n')

  def compileTerm(self):
    self.output_file.write('<term>\n')
    if self.tokenizer.tokenType() == 'IDENTIFIER':
      self.printXMLToken()
      if self.tokenizer.current_token == '.':
        self.printXMLToken()
        self.printXMLToken()
        self.process('(')
        self.compileExpressionList()
        self.process(')')
      elif self.tokenizer.current_token == '(':
        self.printXMLToken('(')
        self.compileExpressionList()
        self.process(')')
      elif self.tokenizer.current_token == '[':
        self.printXMLToken()
        self.compileExpression()
        self.process(']')
        
    elif self.tokenizer.current_token == '(':
      self.printXMLToken()
      self.compileExpression()
      self.process(')')
    
    elif self.tokenizer.current_token in ('-', '~'):
      self.printXMLToken()
      self.compileTerm()
      
    elif self.tokenizer.tokenType() in ('INT_CONST', 'STRING_CONST', 'KEYWORD'):
      self.printXMLToken()
    
    else:
      print('Syntax Error')
      exit(1)
      
    self.output_file.write('</term>\n')
  
  def compileExpressionList(self):
    no_of_expressions = 0
    self.output_file.write('<expressionList>\n')
    if (self.tokenizer.current_token != ')'):
      self.compileExpression()
      no_of_expressions += 1
      while self.tokenizer.current_token == ',':
        self.printXMLToken()
        self.compileExpression()
        no_of_expressions += 1
    self.output_file.write('</expressionList>\n')
    return no_of_expressions
    