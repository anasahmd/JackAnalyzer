from data import *

class JackTokenizer:
  
  def __init__(self, input_file) -> None:
    self.input_file = input_file
    self.current_token = ''
    self.token_type = None
    self.multi_comment = False
    self.current_line = ''
    self.add_new_line()
    self.advance()
        
  # Assume that input_line is empty
  def add_new_line(self):
    while not self.hasMoreTokens():
      new_line = self.input_file.readline()
      if new_line == '':
        break
      self.current_line = self.remove_comments(new_line)
    
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
    if self.current_line:
      return True
    else:
      return False
  
  # called if hasMoreTokens is true
  def advance(self):
    if not self.hasMoreTokens():
      self.add_new_line()
      
    self.current_token = ''
    self.token_type = None 
    for index, char in enumerate(self.current_line):
      if self.token_type == None:
        if char == '"':
          self.token_type = 'STRING_CONST'
        elif char.isnumeric():
          self.current_token = char
          self.token_type = 'INT_CONST'
        elif char in symbol:
          self.current_token = char
          self.token_type = 'SYMBOL'
          self.current_line = self.current_line[index + 1:]
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
          self.current_line = self.current_line[index:]
          return
        else:
          self.current_token += char
        
      elif self.token_type == 'INT_CONST':
        if char.isalpha():
          print('Invalid Code')
          exit(1)
        if not char.isnumeric():
          self.current_line = self.current_line[index:]
          return
        else:
          self.current_token += char
      
      elif self.token_type == 'STRING_CONST':
        if char == '"':
          self.current_line = self.current_line[index + 1:]
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
    return self.current_token + self.symbol_table[self.current_token]

  def intVal(self):
    return self.current_token 

  def stringVal(self):
    return self.current_token
