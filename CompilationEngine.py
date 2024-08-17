from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:

    def __init__(self, input_file, output_file) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.tokenizer = JackTokenizer(input_file)
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_file)
        self.class_name = None
        self.subroutine_name = None
        self.subroutine_type = None
        self.label_counter = 0

    def process(self, string: str):
        # Consider changing current token accessor
        if self.tokenizer.current_token == string:
            self.tokenizer.advance()
        else:
            print("Syntax Error")
            print(string)
            print(self.tokenizer.current_token)
            exit(1)

    def getLabelCounter(self):
        counter = self.label_counter
        self.label_counter += 1
        return str(counter)

    def compileClass(self):
        self.process("class")
        self.class_name = self.tokenizer.current_token
        self.tokenizer.advance()
        self.process("{")
        while self.tokenizer.current_token in ("static", "field"):
            self.compileClassVarDec()
        while self.tokenizer.current_token in ("constructor", "function", "method"):
            self.compileSubroutine()
        self.process("}")
        self.symbol_table.resetClassTable()

    def compileClassVarDec(self):
        if self.tokenizer.current_token in ("static", "field"):
            kind = self.tokenizer.current_token.upper()
            self.tokenizer.advance()
            type = self.tokenizer.current_token
            self.tokenizer.advance()
            name = self.tokenizer.current_token
            self.symbol_table.define(name, type, kind)
            index = self.symbol_table.indexOf(name)
            self.tokenizer.advance()
            while self.tokenizer.current_token == ",":
                self.process(",")
                name = self.tokenizer.current_token
                self.symbol_table.define(name, type, kind)
                index = self.symbol_table.indexOf(name)
                self.tokenizer.advance()
            self.process(";")

    # ('constructor'| 'function'| 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutine(self):
        if self.tokenizer.current_token in ("constructor", "function", "method"):
            self.subroutine_type = self.tokenizer.current_token
            if self.subroutine_type == "method":
                self.symbol_table.define("this", self.class_name, "ARG")

            self.tokenizer.advance()
            self.tokenizer.advance()
            self.subroutine_name = self.tokenizer.current_token
            self.tokenizer.advance()
            self.process("(")
            self.compileParameterList()
            self.process(")")
            self.compileSubroutineBody()
        self.symbol_table.resetSubroutineTable()
        self.subroutine_name = None

    def compileParameterList(self):
        # Checks if parameterList is not empty
        if self.tokenizer.current_token != ")":
            type = self.tokenizer.current_token
            self.tokenizer.advance()
            name = self.tokenizer.current_token
            self.symbol_table.define(name, type, "ARG")
            index = self.symbol_table.indexOf(name)
            self.tokenizer.advance()
            while self.tokenizer.current_token == ",":
                self.process(",")
                type = self.tokenizer.current_token
                self.tokenizer.advance()
                name = self.tokenizer.current_token
                self.symbol_table.define(name, type, "ARG")
                index = self.symbol_table.indexOf(name)
                self.tokenizer.advance()

    # '{' varDec* statements'}'
    def compileSubroutineBody(self):
        self.tokenizer.advance()
        while self.tokenizer.current_token == "var":
            self.compileVarDec()
        self.vm_writer.writeFunction(
            f"{self.class_name}.{self.subroutine_name}", self.symbol_table.var_index
        )
        if self.subroutine_type == "constructor":
            field_count = self.symbol_table.varCount("FIELD")
            self.vm_writer.writePush("constant", field_count)
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePop("pointer", 0)
        elif self.subroutine_type == "method":
            self.vm_writer.writePush("argument", 0)
            self.vm_writer.writePop("pointer", 0)
        self.compileStatements()
        self.process("}")

    def compileVarDec(self):
        self.tokenizer.advance()
        type = self.tokenizer.current_token
        self.tokenizer.advance()
        name = self.tokenizer.current_token
        self.symbol_table.define(name, type, "VAR")
        index = self.symbol_table.indexOf(name)
        self.tokenizer.advance()
        while self.tokenizer.current_token == ",":
            self.tokenizer.advance()
            name = self.tokenizer.current_token
            self.symbol_table.define(name, type, "VAR")
            index = self.symbol_table.indexOf(name)
            self.tokenizer.advance()
        self.process(";")

    # statement*
    def compileStatements(self):
        while self.tokenizer.current_token in ("let", "if", "while", "do", "return"):
            if self.tokenizer.current_token == "let":
                self.compileLet()
            elif self.tokenizer.current_token == "if":
                self.compileIf()
            elif self.tokenizer.current_token == "while":
                self.compileWhile()
            elif self.tokenizer.current_token == "do":
                self.compileDo()
            elif self.tokenizer.current_token == "return":
                self.compileReturn()

    def compileLet(self):
        self.process("let")
        segment = self.symbol_table.kindOfSegment(self.tokenizer.current_token)
        index = self.symbol_table.indexOf(self.tokenizer.current_token)

        self.tokenizer.advance()
        if self.tokenizer.current_token == "[":
            self.vm_writer.writePush(segment, index)
            self.process("[")
            self.compileExpression()
            self.process("]")
            self.vm_writer.writeArithmetic("add")
            self.process("=")
            self.compileExpression()
            self.vm_writer.writePop("temp", 0)
            self.vm_writer.writePop("pointer", 1)
            self.vm_writer.writePush("temp", 0)
            self.vm_writer.writePop("that", 0)
        else:
            self.process("=")
            self.compileExpression()
            self.vm_writer.writePop(segment, index)

        self.process(";")

    def compileIf(self):
        self.process("if")
        self.process("(")
        self.compileExpression()
        self.vm_writer.writeArithmetic("not")
        l1 = "L" + self.getLabelCounter()
        self.vm_writer.writeIf(l1)
        self.process(")")
        self.process("{")
        self.compileStatements()
        l2 = "L" + self.getLabelCounter()
        self.vm_writer.writeGoto(l2)
        self.process("}")
        self.vm_writer.writeLabel(l1)
        # Process else conditionally
        if self.tokenizer.current_token == "else":
            self.tokenizer.advance()
            self.process("{")
            self.compileStatements()
            self.process("}")
        self.vm_writer.writeLabel(l2)

    def compileWhile(self):
        l1 = "L" + self.getLabelCounter()
        self.vm_writer.writeLabel(l1)
        self.process("while")
        self.process("(")
        self.compileExpression()
        self.process(")")
        self.vm_writer.writeArithmetic("not")
        l2 = "L" + self.getLabelCounter()
        self.vm_writer.writeIf(l2)
        self.process("{")
        self.compileStatements()
        self.process("}")
        self.vm_writer.writeGoto(l1)
        self.vm_writer.writeLabel(l2)

    # 'do' subroutineCall';'
    def compileDo(self):
        self.tokenizer.advance()
        self.compileTerm()
        self.vm_writer.writePop("temp", 0)
        self.process(";")

    def compileReturn(self):
        self.process("return")
        if self.tokenizer.current_token != ";":
            self.compileExpression()
        else:
            self.vm_writer.writePush("constant", 0)
        self.process(";")
        self.vm_writer.writeReturn()

    def compileExpression(self):
        self.compileTerm()
        op = ""
        while self.tokenizer.current_token in (
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
        ):
            op = self.tokenizer.current_token
            self.tokenizer.advance()

            self.compileTerm()

        if op == "+":
            self.vm_writer.writeArithmetic("add")
        elif op == "-":
            self.vm_writer.writeArithmetic("sub")
        elif op == "*":
            self.vm_writer.writeCall("Math.multiply", 2)
        elif op == "/":
            self.vm_writer.writeCall("Math.divide", 2)
        elif op == "&":
            self.vm_writer.writeArithmetic("and")
        elif op == "|":
            self.vm_writer.writeArithmetic("or")
        elif op == "<":
            self.vm_writer.writeArithmetic("lt")
        elif op == ">":
            self.vm_writer.writeArithmetic("gt")
        elif op == "=":
            self.vm_writer.writeArithmetic("eq")

    def compileTerm(self):
        if self.tokenizer.tokenType() == "IDENTIFIER":
            self.tokenizer.peek()  # updates next_token

            if self.tokenizer.next_token == ".":
                left = self.tokenizer.current_token
                segment = self.symbol_table.kindOfSegment(left)

                self.tokenizer.advance()
                self.tokenizer.advance()  # skip .
                right = self.tokenizer.current_token
                self.tokenizer.advance()

                if segment != "NONE":
                    index = self.symbol_table.indexOf(left)
                    self.vm_writer.writePush(segment, index)
                    self.process("(")
                    no_of_expression = self.compileExpressionList()
                    self.process(")")
                    class_name = self.symbol_table.typeOf(left)
                    self.vm_writer.writeCall(
                        f"{class_name}.{right}", no_of_expression + 1
                    )
                else:
                    self.process("(")
                    no_of_expression = self.compileExpressionList()
                    self.process(")")
                    self.vm_writer.writeCall(f"{left}.{right}", no_of_expression)

            elif self.tokenizer.next_token == "(":
                subroutine = self.tokenizer.current_token
                self.vm_writer.writePush("pointer", 0)
                self.tokenizer.advance()
                self.process("(")
                no_of_expression = self.compileExpressionList()
                self.process(")")
                self.vm_writer.writeCall(
                    f"{self.class_name}.{subroutine}", no_of_expression + 1
                )

            elif self.tokenizer.next_token == "[":
                array = self.tokenizer.current_token
                segment = self.symbol_table.kindOfSegment(array)
                index = self.symbol_table.indexOf(array)
                self.vm_writer.writePush(segment, index)
                self.tokenizer.advance()
                self.process("[")
                self.compileExpression()
                self.process("]")
                self.vm_writer.writeArithmetic("add")
                self.vm_writer.writePop("pointer", 1)
                self.vm_writer.writePush("that", 0)

            else:
                segment = self.symbol_table.kindOfSegment(self.tokenizer.current_token)
                index = self.symbol_table.indexOf(self.tokenizer.current_token)
                self.vm_writer.writePush(segment, index)
                self.tokenizer.advance()

        elif self.tokenizer.current_token == "(":
            self.process("(")
            self.compileExpression()
            self.process(")")

        elif self.tokenizer.current_token == "-":
            self.tokenizer.advance()
            self.compileTerm()
            self.vm_writer.writeArithmetic("neg")

        elif self.tokenizer.current_token == "~":
            self.tokenizer.advance()
            self.compileTerm()
            self.vm_writer.writeArithmetic("not")

        elif self.tokenizer.tokenType() == "INT_CONST":
            self.vm_writer.writePush("constant", self.tokenizer.current_token)
            self.tokenizer.advance()

        elif self.tokenizer.tokenType() == "STRING_CONST":
            string_length = len(self.tokenizer.current_token)
            self.vm_writer.writePush("constant", string_length)
            self.vm_writer.writeCall("String.new", 1)
            for c in self.tokenizer.current_token:
                self.vm_writer.writePush("constant", ord(c))
                self.vm_writer.writeCall("String.appendChar", 2)
            self.tokenizer.advance()

        elif self.tokenizer.tokenType() == "KEYWORD":
            if self.tokenizer.current_token == "true":
                self.vm_writer.writePush("constant", 1)
                self.vm_writer.writeArithmetic("neg")
            elif self.tokenizer.current_token in ("false", "null"):
                self.vm_writer.writePush("constant", 0)
            elif self.tokenizer.current_token == "this":
                self.vm_writer.writePush("pointer", 0)
            self.tokenizer.advance()

        else:
            print("Syntax Error" + self.tokenizer.current_token)
            exit(1)

    def compileExpressionList(self):
        no_of_expressions = 0
        if self.tokenizer.current_token != ")":
            self.compileExpression()
            no_of_expressions += 1
            while self.tokenizer.current_token == ",":
                self.tokenizer.advance()
                self.compileExpression()
                no_of_expressions += 1
        return no_of_expressions
