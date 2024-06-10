from data import *
import os
import argparse

parser = argparse.ArgumentParser(
                    prog='VMTranslator.py',
                    description='Converts VM code to assembly code.',
                    epilog='More information on https://github.com/anasahmd/VMTranslator/')

parser.add_argument('input_path', help='Input VM File or Folder')

args = parser.parse_args()

class JackTokenizer:
  
  def __init__(self, input_line = '') -> None:
    self.current_token = ''
    self.token_type = None
    self.multi_comment = False
    self.input_line = self.remove_comments(input_line)
    
  # Assume that input_line is empty
  def add_new_line(self, line):
    self.input_line = self.remove_comments(line)
    
  def remove_comments(self, line):
    removed_multi_line = self.remove_multi_line_comment(line)
    removed_inline = self.remove_inline_comment(removed_multi_line)
    return removed_inline.strip()
  
  def remove_inline_comment(self, line) -> str:
    comment_index = line.find('//')
    removed_comment = line
    # if comment, then remove it
    if not comment_index == -1:
      removed_comment = line[:comment_index]
    # Return the line after removing white space and line break
    return removed_comment
  
  def remove_multi_line_comment(self, line) -> str:
    if self.multi_comment:
      end_multi_index = line.find('*/')
      if end_multi_index != -1:
        self.multi_comment = False
        return line[end_multi_index + 2:]
      else:
        return ''
    else:
      start_multi_index = line.find('/*')
      end_multi_index = line.find('*/')
      if start_multi_index != -1 and end_multi_index != -1:
        return line[:start_multi_index] + line[end_multi_index + 2:]
      elif start_multi_index != -1 and end_multi_index == -1:
        self.multi_comment = True
        return line[:start_multi_index]
      else:
        return line

  # Checks if there are more tokens, might not need it
  def hasMoreTokens(self) -> bool:
    if self.input_line:
      return True
    else:
      return False
  
  # called if hasMoreTokens is true
  def advance(self):
    self.current_token = ''
    self.token_type = None 
    for index, char in enumerate(self.input_line):
      if self.token_type == None:
        if char == '"':
          self.token_type = 'STRING_CONST'
        elif char.isnumeric():
          self.current_token = char
          self.token_type = 'INT_CONST'
        elif char in symbol:
          self.current_token = char
          self.token_type = 'SYMBOL'
          self.input_line = self.input_line[index + 1:]
          return
        elif char.isalpha() or char == '_':
          self.current_token = char
          self.token_type = 'idorkey'
      
      # If token type is not None
      elif self.token_type == 'idorkey':
        if char == ' ' or char in symbol:
          if self.current_token in keyword:
            self.token_type = 'KEYWORD'
          else:
            self.token_type = 'IDENTIFIER'
          self.input_line = self.input_line[index:]
          return
        else:
          self.current_token += char
        
      elif self.token_type == 'INT_CONST':
        if char.isalpha():
          print('Invalid Code')
          exit(1)
        if not char.isnumeric():
          self.input_line = self.input_line[index:]
          return
        else:
          self.current_token += char
      
      elif self.token_type == 'STRING_CONST':
        if char == '"':
          self.input_line = self.input_line[index + 1:]
          return
        else:
          self.current_token += char
  
  # returns the type of current token
  def tokenType(self):
    return self.token_type

  # Returns the keyword as a constant
  def keyWord(self):
    return self.current_token

  def symbol(self):
    return self.current_token

  def identifier(self):
    return self.current_token

  def intVal(self):
    return self.current_token

  def stringVal(self):
    return self.current_token

class CompilationEngine:
  
  def __init__(self, tokenizer: JackTokenizer, output_file) -> None:
    self.tokenizer = tokenizer
    self.output_file = output_file
  
  def process(self, string: str):
    # Consider changing current token accessor
    if (self.tokenizer.current_token == string):
      self.printXMLToken()
    else:
      print('Syntax Error')
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
    self.output_file.write('<class>')
    self.process('class')
    self.printXMLToken()
    self.process('{')
    while self.tokenizer.current_token in ('static', 'field'):
      self.compileClassVarDec()
    while self.tokenizer.current_token in ('function', 'function', 'method'):
      self.compileSubroutine()
    self.process('}')
    self.output_file.write('</class>')
    
  def compileClassVarDec(self):
    self.output_file.write('<classVarDec>')
    if self.tokenizer.current_token in ('static', 'field'):
      self.printXMLToken()
      self.printXMLToken()
      self.printXMLToken()
      while self.tokenizer.current_token == ',':
        self.process(',')
        self.printXMLToken()
      self.process(';')
    self.output_file.write('</classVarDec>')

  def compileSubroutine(self):
    self.output_file.write('<subroutineDec>')
    if self.tokenizer.current_token in ('constructor', 'function', 'method'):
      self.printXMLToken()
      self.printXMLToken()
      self.printXMLToken()
      self.process('(')
      self.compileParameterList()
      self.process(')')
      self.compileSubroutineBody()
    self.output_file.write('</subroutineDec>')  
  
  def compileParameterList(self):
    self.output_file.write('<parameterList>')
    # Checks if parameterList is not empty
    if self.tokenizer.current_token != ')':
      self.printXMLToken()
      self.printXMLToken()
      while self.tokenizer.current_token == ',':
        self.printXMLToken()
        self.printXMLToken()
        self.printXMLToken()
    self.output_file.write('</parameterList>')

  def compileSubroutineBody(self):
    self.output_file.write('<subroutineBody>')
    self.process('{')
    while self.tokenizer.current_token == 'var':
      self.compileVarDec()
    self.compileStatements()
    self.process('}')
    self.output_file.write('</subroutineBody>')

  def compileVarDec(self):
    self.output_file.write('<varDec>')
    self.printXMLToken()
    self.printXMLToken()
    while self.tokenizer.current_token == ',':
      self.printXMLToken()
      self.printXMLToken()
    self.process(';')
    self.output_file.write('</varDec>')
  
  def compileStatements(self):
    self.output_file.write('<statements>')
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
    self.output_file.write('</statements>')
  
  def compileLet(self):
    self.output_file.write('<let>')
    self.process('let')
    self.printXMLToken()
    if self.tokenizer.current_token == '[':
      self.process('[')
      self.compileExpression()
      self.process(']')
    self.process('=')
    self.compileExpression()
    self.process(';')
    self.output_file.write('</let>')

  def compileIf(self):
    self.output_file.write('<ifStatement>')
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
    self.output_file.write('<ifStatement>')
      
  def compileWhile(self):
    self.output_file.write('<whileStatement>')
    self.process('while')
    self.process('(')
    self.compileExpression()
    self.process(')')
    self.process('{')
    self.compileStatements()
    self.process('}')
    self.output_file.write('</whileStatement>')
    
  def compileDo(self):
    self.output_file.write('<doStatement>')
    self.process('do')
    self.compileExpression()
    self.process(';')
    self.output_file.write('</doStatement>')
  
  def compileReturn(self):
    self.output_file.write('<returnStatement>')
    self.process('return')
    if (self.tokenizer.current_token != ';'):
      self.compileExpression()
    self.process(';')
    self.output_file.write('</returnStatement>')
  
  def compileExpression(self):
    self.output_file.write('<expression>')
    self.compileTerm()
    while self.tokenizer.current_token in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
      self.printXMLToken()
      self.compileTerm()
    self.output_file.write('</expression>')

  def compileTerm(self):
    self.output_file.write('<term>')
    self.printXMLToken()
    self.output_file.write('</term>')
  
  def compileExpressionList(self):
    no_of_expressions = 0
    self.output_file.write('<expressionList>')
    if (self.tokenizer.current_token != ')'):
      self.compileExpression()
      no_of_expressions += 1
      while self.tokenizer.current_token == ',':
        self.printXMLToken()
        self.compileExpression()
        no_of_expressions += 1
    self.output_file.write('</expressionList>')
    return no_of_expressions
    

  

class JackAnalyzer():
  def __init__(self) -> None:
    pass
  
  def handleFile(self, input_path):
    xml_file_name = input_path.replace('.jack', 'T.xml')
    xml_file = open(xml_file_name, 'w')
    
    # Initialize JackTokenizer
    tokenizer = JackTokenizer()
    with open(input_path, 'r') as file:
      xml_file.write('<tokens>\n')
      for line in file:
        tokenizer.add_new_line(line)
        while tokenizer.hasMoreTokens():
          tokenizer.advance()
          # if tokenizer.tokenType() == 'KEYWORD':
          #   xml_file.writelines(['<keyword> ', tokenizer.keyWord(), ' </keyword>', '\n'])
          # elif tokenizer.tokenType() == 'SYMBOL':
          #   alternate_symbol = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
          #   symbol = tokenizer.symbol()
          #   if alternate_symbol.get(symbol):
          #     xml_file.writelines(['<symbol> ', alternate_symbol[symbol], ' </symbol>', '\n'])
          #   else:
          #     xml_file.writelines(['<symbol> ', symbol, ' </symbol>', '\n'])
          
          # elif tokenizer.tokenType() == 'IDENTIFIER':
          #   xml_file.writelines(['<identifier> ', tokenizer.identifier(), ' </identifier>', '\n'])
          # elif tokenizer.tokenType() == 'INT_CONST':
          #   xml_file.writelines(['<integerConstant> ', tokenizer.intVal(), ' </integerConstant>', '\n'])
          # elif tokenizer.tokenType() == 'STRING_CONST':
          #   xml_file.writelines(['<stringConstant> ', tokenizer.stringVal(), ' </stringConstant>', '\n'])
      xml_file.write('</tokens>\n')
    xml_file.close()

  def analyze(self) -> None:
    # If the input is a file
    if os.path.isfile(args.input_path):
      # Error if the input file is not a jack file 
      # else proceed with file
      if ".jack" not in args.input_path:
        print( "Provided file is not a VM file")
        exit(1)
      else:
        self.handleFile(args.input_path)
        

    # If the input is a folder
    elif os.path.isdir(args.input_path):
      if args.input_path[-1] != '/':
        args.input_path = args.input_path + '/'

      for file in os.listdir(args.input_path):
        if ".jack" in file:
          self.handleFile(args.input_path + file)
    else:
      print('Wrong input path provided')
      exit(1)
  
def main():
  pass
      
if __name__ == '__main__':
  analyzer = JackAnalyzer()
  analyzer.analyze()