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
    stripped_code = line.strip()
    removed_multi_line = self.remove_multi_line_comment(stripped_code)
    removed_inline = self.remove_inline_comment(removed_multi_line)
    return removed_inline
  
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
        if not char.isnumeric() & char.isalpha():
          self.input_line = self.input_line[index:]
          return
        elif char.isalpha():
          print('Invalid Code')
          exit(1)
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
  
  def __init__(self) -> None:
    pass
  
  # !!!
  def compileClass():
    pass
  
  # !!!
  def compileClassVarDec():
    pass
  
  # !!!
  def compileSubroutine():
    pass 
  
  # !!!
  def compileParameterList():
    pass
  
  # !!!
  def compileSubroutineBody():
    pass
  
  # !!!
  def compileVarDec():
    pass
  
  # !!!
  def compileStatements():
    pass 
  
  # !!!
  def compileLet():
    pass
  
  # !!!
  def compileIf():
    pass
  
  # !!!
  def compileWhile():
    pass 
  
  # !!!
  def compileDo():
    pass 
  
  # !!!
  def compileReturn():
    pass 
  
  # !!!
  def compileExpression():
    pass 
  
  # !!!
  def compileTerm():
    pass
  
  # !!!
  def compileExpressionList():
    pass
  

class JackAnalyzer():

  def analyze() -> None:
    # If the input is a file
    if os.path.isfile(args.input_path):
      # Error if the input file is not a jack file 
      # else proceed with file
      if ".jack" not in args.input_path:
        print( "Provided file is not a VM file")
        exit(1)
      else:
        xml_file_name = args.input_path.replace('.jack', 'T.xml')
        xml_file = open(xml_file_name, 'w')
        
        # Initialize JackTokenizer
        tokenizer = JackTokenizer()
        with open(args.input_path, 'r') as file:
          xml_file.write('<tokens>\n')
          for line in file:
            tokenizer.add_new_line(line)
            while tokenizer.hasMoreTokens():
              tokenizer.advance()
              if tokenizer.tokenType() == 'KEYWORD':
                xml_file.writelines(['<keyword>', tokenizer.keyWord(), '</keyword>', '\n'])
              elif tokenizer.tokenType() == 'SYMBOL':
                alternate_symbol = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
                symbol = tokenizer.symbol()
                if alternate_symbol.get(symbol):
                  xml_file.writelines(['<symbol>', alternate_symbol[symbol], '</symbol>', '\n'])
                else:
                  xml_file.writelines(['<symbol>', symbol, '</symbol>', '\n'])
              
              elif tokenizer.tokenType() == 'IDENTIFIER':
                xml_file.writelines(['<identifier>', tokenizer.identifier(), '</identifier>', '\n'])
              elif tokenizer.tokenType() == 'INT_CONST':
                xml_file.writelines(['<integerConstant>', tokenizer.intVal(), '</integerConstant>', '\n'])
              elif tokenizer.tokenType() == 'STRING_CONST':
                xml_file.writelines(['<stringConstant>', tokenizer.stringVal(), '</stringConstant>', '\n'])
          xml_file.write('</tokens>\n')
        xml_file.close()
        pass

    # If the input is a folder
    elif os.path.isdir(args.input_path):
      # if args.input_path[-1] != '/':
      #   args.input_path = args.input_path + '/'

      # asm_file_name = args.input_path + args.input_path.split('/')[-2] + '.asm'
      # asm_file = open(asm_file_name, 'w')
      # # Initialize CodeWriter
      # codewriter = CodeWriter(asm_file)

      # for file in os.listdir(args.input_path):
      #   if ".vm" in file:
      #     input_file = open(args.input_path + file, "r")
      #     codewriter.setFileName(input_file)
      #     parser = Parser(input_file, codewriter)
      #     parser.parse()

      # codewriter.writeInfiniteLoop()
      # asm_file.close()
      pass
    else:
      print('Wrong input path provided')
      exit(1)
  
def main():
  pass
      
if __name__ == '__main__':
  analyzer = JackAnalyzer
  analyzer.analyze()