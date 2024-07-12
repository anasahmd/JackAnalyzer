class SymbolTable():
  def __init__(self): 
    self.class_table = {}
    self.subroutine_table = {}
    self.static_index = 0
    self.field_index = 0
    self.arg_index = 0
    self.var_index = 0
    
  def resetClassTable(self) -> None:
    self.class_table = {}
    self.subroutine_table = {}
    self.static_index = 0
    self.field_index = 0
    self.arg_index = 0
    self.var_index = 0
    
  def resetSubroutineTable(self) -> None:
    self.subroutine_table = {}
    self.arg_index = 0
    self.var_index = 0
  
  def define(self, name: str, type: str, kind):
    if kind == 'STATIC':
      self.class_table[name] = (type, kind, self.static_index)
      self.static_index += 1
    elif kind == 'FIELD':
      self.class_table[name] = (type, kind, self.field_index)
      self.field_index += 1
    elif kind == 'ARG':
      self.subroutine_table[name] = (type, kind, self.arg_index)
      self.arg_index += 1
    elif kind == 'VAR':
      self.subroutine_table[name] = (type, kind, self.var_index)
      self.var_index += 1
    
  
  def varCount(self, kind) -> int:
    if kind == 'STATIC':
      return self.static_index
    elif kind == 'FIELD':
      return self.field_index
    elif kind == 'ARG':
      return self.arg_index
    elif kind == 'VAR':
      return self.var_index
    else:
      print('Invalid kind given!')
      exit(1)
  
  def kindOf(self, name):
    if name in self.subroutine_table:
      return self.subroutine_table[name][0]
    elif name in self.class_table:
      return self.class_table[name][0]
    else:
      return 'NONE'
  
  def typeOf(self, name) -> str:
    if name in self.subroutine_table:
      return self.subroutine_table[name][0]
    elif name in self.class_table:
      return self.class_table[name][0]
    else:
      print(name + 'not defined')
      exit(1)
  
  def indexOf(self, name):
    if name in self.subroutine_table:
      return self.subroutine_table[name][2]
    elif name in self.class_table:
      return self.class_table[name][2]
    else:
      print(name + 'not defined')
      exit(1)