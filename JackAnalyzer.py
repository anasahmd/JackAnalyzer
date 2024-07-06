from data import *
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
import os
import argparse

parser = argparse.ArgumentParser(
                    prog='VMTranslator.py',
                    description='Converts VM code to assembly code.',
                    epilog='More information on https://github.com/anasahmd/VMTranslator/')

parser.add_argument('input_path', help='Input VM File or Folder')

args = parser.parse_args()

class JackAnalyzer():
  def __init__(self) -> None:
    pass
  
  def handleFile(self, input_path):
    xml_file_name = input_path.replace('.jack', '.xml')
    xml_file = open(xml_file_name, 'w')
    input_file = open(input_path, 'r')
    
    compilation_engine = CompilationEngine(input_file, xml_file)
    compilation_engine.compileClass()
    
    xml_file.close()

  def analyze(self) -> None:
    # If the input is a file
    if os.path.isfile(args.input_path):
      # Error if the input file is not a jack file 
      # else proceed with file
      if ".jack" not in args.input_path:
        print( "Provided file is not a Jack file")
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