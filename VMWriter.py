class VMWriter:
    def __init__(self, output_file) -> None:
        self.output_file = output_file

    def writePush(self, segment: str, index: int) -> None:
        self.output_file.write(f"push {segment} {str(index)}\n")

    def writePop(self, segment, index) -> None:
        self.output_file.write(f"pop {segment} {str(index)}\n")

    def writeArithmetic(self, command: str) -> None:
        self.output_file.write(f"{command.lower()}\n")

    def writeLabel(self, label: str) -> None:
        self.output_file.write(f"label {label}\n")

    def writeGoto(self, label: str) -> None:
        self.output_file.write(f"goto {label}\n")

    def writeIf(self, label: str) -> None:
        self.output_file.write(f"if-goto {label}\n")

    def writeCall(self, name: str, nArgs: int) -> None:
        self.output_file.write(f"call {name} {str(nArgs)}\n")

    def writeFunction(self, name: str, nVars: int) -> None:
        self.output_file.write(f"function {name} {str(nVars)}\n")

    def writeReturn(self) -> None:
        self.output_file.write("return\n")

    def close(self) -> None:
        self.output_file.close()
