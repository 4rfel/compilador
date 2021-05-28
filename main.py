import sys
from abc import ABC, abstractmethod

class STDOUTWriter():
	instruction = ""
	with open("header.txt", "r") as header:
		instruction += header.read()

	def AddInstruction(instructions:str):
		STDOUTWriter.instruction += "  " + instructions + "\n"

	def Write():
		sys.stdout.write(STDOUTWriter.instruction)
		

class SymbolTable():
	def __init__(self) -> None:
		self.table = {} # {varname:[vartipo, varvalue, bytesToEBP]}
		self.bytesToEBP = 0
		self.intBytesQuant = 4
		self.boolBytesQuant = 4

	def SetVar(self, var_type, var_name, var_value):
		if var_name not in self.table:
			if var_type == "int":
				self.bytesToEBP += self.intBytesQuant
			elif var_type == "bool":
				self.bytesToEBP += self.boolBytesQuant
			else:
				sys.exit(f"invalid var type: {var_type}")
			
			bytesToEBP = self.bytesToEBP
		else:
			bytesToEBP = self.table[var_name][2]
		
		self.table[var_name] = [var_type, var_value, bytesToEBP]

	def GetVar(self, var_name):
		return self.table[var_name]

	def GetVarType(self, var_name):
		if var_name not in self.table:
			sys.exit(f"var {var_name} is wasnt declared") 
		
		return self.table[var_name][0]

	def GetVarValue(self, var_name):
		if var_name not in self.table:
			sys.exit(f"var {var_name} is wasnt declared") 
		
		return self.table[var_name][1]
	
	def GetBytesToEBP(self, var_name):
		if var_name not in self.table:
			sys.exit(f"var {var_name} is wasnt declared") 
		
		return self.table[var_name][2]

class Node(ABC):
	id = 0

	def __init__(self, value = 0, children = []):
		self.value = value
		self.children:Node = children
		self.id = self.newId()

	def newId(self):
		Node.id += 1
		return Node.id

	@abstractmethod
	def Evaluate(self):
		return

class BinOP(Node):
	def __init__(self, value, children):
		super().__init__(value=value, children=children)

	def Evaluate(self):
		c0 = self.children[0].Evaluate()
		STDOUTWriter.AddInstruction("PUSH EBX")
		c1 = self.children[1].Evaluate()
		STDOUTWriter.AddInstruction("POP EAX")
		
		if c0[0] != "int" or c1[0] != "int":
			sys.exit("conta com variavel diferente de int")

		if self.value == "add":
			STDOUTWriter.AddInstruction("ADD EAX, EBX")
			STDOUTWriter.AddInstruction("MOV EBX, EAX")
			STDOUTWriter.AddInstruction("")
			return ["int", c0[1] + c1[1]]

		if self.value == "sub":
			STDOUTWriter.AddInstruction("SUB EAX, EBX")
			STDOUTWriter.AddInstruction("MOV EBX, EAX")
			STDOUTWriter.AddInstruction("")

			return ["int", c0[1] - c1[1]]
		
		if self.value == "mult":
			STDOUTWriter.AddInstruction("IMUL EBX")
			STDOUTWriter.AddInstruction("MOV EBX, EAX")
			STDOUTWriter.AddInstruction("")

			return ["int", c0[1] * c1[1]]
		
		if self.value == "div":
			STDOUTWriter.AddInstruction("IDIV EBX")
			STDOUTWriter.AddInstruction("MOV EBX, EAX")
			STDOUTWriter.AddInstruction("")
			return ["int", int(c0[1] / c1[1])]

		sys.exit("DEU RUIM")

class UnOp(Node):
	def __init__(self, value, children):
		super().__init__(value=value, children=children)

	def Evaluate(self):
		self.children.Evaluate()

		if self.value == "sub":
			STDOUTWriter.AddInstruction("MOV EAX, 0")
			STDOUTWriter.AddInstruction("SUB EAX, EBX")
			STDOUTWriter.AddInstruction("MOV EBX, EAX")
			STDOUTWriter.AddInstruction("")
			return
			
		if self.value == "!":
			STDOUTWriter.AddInstruction("NOT EBX")
			STDOUTWriter.AddInstruction("")
			return

		sys.exit("DEU RUIM 2")

class IntVal(Node):
	def __init__(self, value):
		super().__init__(value=value, children=[])

	def Evaluate(self):
		STDOUTWriter.AddInstruction(f"MOV EBX, {self.value} ; int val")
		STDOUTWriter.AddInstruction("")
		return ["int", self.value]

class NoOp(Node):
	def __init__(self):
		super().__init__(value=None, children=[])

	def Evaluate(self):
		return super().Evaluate()

class PrintOp(Node):
	def __init__(self, children):
		super().__init__(value=None, children=children)

	def Evaluate(self):
		self.children[0].Evaluate()
		
		STDOUTWriter.AddInstruction("PUSH EBX ; printing")
		STDOUTWriter.AddInstruction("CALL print")
		STDOUTWriter.AddInstruction("POP EBX")
		STDOUTWriter.AddInstruction("")

		# print(var[1])

class SetVar(Node):
	def __init__(self, children, symbolTable:SymbolTable):
		super().__init__(value=None, children=children)
		self.symbolTable:SymbolTable = symbolTable

	def Evaluate(self):
		var_name = self.children[0]
		if var_name not in self.symbolTable.table:
			STDOUTWriter.AddInstruction(f"PUSH DWORD 0 ; setting var")
			
			var_type = self.children[1]
			if len(self.children) == 3:
				var_value = self.children[2].Evaluate()
			else:
				var_value = None
				# if(var_type == "string"):
				# 	var_value = ""
		else:
			var_type = self.symbolTable.GetVarType(var_name)
			var_value = self.children[1].Evaluate()
		
		if type(var_value) == list:
			var_value = var_value[1]
		
		if var_value != None:
			if(var_type == "bool"):
				var_value = bool(var_value)
			# if(var_type == "string"):
			# 	self.symbolTable.table[var_name] = [var_type, str(var_value)]
			elif(var_type == "int"):
				var_value = int(var_value)
		
		self.symbolTable.SetVar(var_type, var_name, var_value)
		if var_value != None:
			STDOUTWriter.AddInstruction(f"MOV [EBP-{self.symbolTable.GetBytesToEBP(var_name)}], EBX")
		STDOUTWriter.AddInstruction("")


class VarVal(Node):
	def __init__(self, children, symbolTable:SymbolTable):
		super().__init__(value=None, children=children)
		self.symbolTable = symbolTable

	def Evaluate(self):
		STDOUTWriter.AddInstruction(f"MOV EBX, [EBP-{self.symbolTable.GetBytesToEBP(self.children[0])}] ; getting var")
		STDOUTWriter.AddInstruction("")

		return self.symbolTable.GetVar(self.children[0])

# class Readln(Node):
# 	def __init__(self):
# 		super().__init__(value=None, children=[])
		
# 	def Evaluate(self):
# 		i = input()
# 		if i.isnumeric():
# 			return ["int", int(i)]
# 		else:
# 			return ["string", i]

class CompOp(Node):
	def __init__(self, value, children):
		super().__init__(value=value, children=children)

	def Evaluate(self):

		c0 = self.children[0].Evaluate()
		STDOUTWriter.AddInstruction("PUSH EBX")

		c1 = self.children[1].Evaluate()

		STDOUTWriter.AddInstruction("POP EAX")
		STDOUTWriter.AddInstruction("CMP EAX, EBX")

		if self.value == "==":
			STDOUTWriter.AddInstruction("CALL binop_je")
			return ["bool", c0[1] == c1[1]]

		if self.value == "<":
			STDOUTWriter.AddInstruction("CALL binop_jl")
			return ["bool", c0[1] < c1[1]]

		if self.value == ">":
			STDOUTWriter.AddInstruction("CALL binop_jg")
			return ["bool", c0[1] > c1[1]]

		if self.value == "&&":
			STDOUTWriter.AddInstruction(f"AND EBX, EAX")
			return ["bool", bool(c0[1]) and bool(c1[1])]

		if self.value == "||":
			STDOUTWriter.AddInstruction(f"OR EBX, EAX")
			return ["bool", bool(c0[1]) or bool(c1[1])]

		
		sys.exit("DEU RUIM 3")

class IfOp(Node):
	def __init__(self, children):
		super().__init__(value=None, children=children)

	def Evaluate(self):
		self.children[0].Evaluate()[1]
		STDOUTWriter.AddInstruction("CMP EBX, False")
		if len(self.children) == 3:
			STDOUTWriter.AddInstruction(f"JE else_{self.id}")
		else:
			STDOUTWriter.AddInstruction(f"JE end_if_{self.id}")
			

		self.children[1].Evaluate()

		if len(self.children) == 3:
			STDOUTWriter.AddInstruction(f"JMP end_if_{self.id}")
			STDOUTWriter.AddInstruction(f"else_{self.id}:")
			self.children[2].Evaluate()

		STDOUTWriter.AddInstruction(f"end_if_{self.id}:")
		


class WhileOp(Node):
	def __init__(self, children):
			super().__init__(value=None, children=children)

	def Evaluate(self):
		STDOUTWriter.AddInstruction(f"while_{self.id}:")
		self.children[0].Evaluate()
		STDOUTWriter.AddInstruction("CMP EBX, False")
		STDOUTWriter.AddInstruction(f"JE while_exit_{self.id}")

		self.children[1].Evaluate()
		STDOUTWriter.AddInstruction(f"JMP while_{self.id}")
		STDOUTWriter.AddInstruction(f"while_exit_{self.id}:")


class BoolVal(Node):
	def __init__(self, children):
			super().__init__(value=None, children=children)

	def Evaluate(self):
		value = bool(self.children[0])
		if value:
			STDOUTWriter.AddInstruction("CALL binop_true ; bool val")
		else:
			STDOUTWriter.AddInstruction("CALL binop_false ; bool val")

		return ["bool", value]

# class StrVal(Node):
# 	def __init__(self, children):
# 			super().__init__(value=None, children=children)

# 	def Evaluate(self):
# 		return ["string", str(self.children[0])]


class Block(Node):
	def __init__(self):
		super().__init__(value=None, children=[])

	def Evaluate(self):
		for node in self.children:
			node.Evaluate()

	def AddNode(self, node):
		self.children.append(node)


accepted_chars = "[-+*/ 0-9()_a-zA-Z;=]"

class Token:
	def __init__(self, tipo: str, value: int):
		self.tipo: str = tipo
		self.value = value

class Tokenizer:
	def __init__(self, origin: str):
		self.origin: str = origin + " "
		self.position: int = 0
		self.actual: Token = None
		self.brackets = 0
		self.line = 1

	def selectNext(self):

		while self.origin[self.position] == " " or self.origin[self.position] == "\n":
			if self.position == len(self.origin) - 1:
				self.actual = Token(tipo="EOF", value=0)
				if self.brackets != 0:
					sys.exit("unbalanced bracket")
				return
			self.position += 1

		if self.origin[self.position].isdigit():
			temp = ""
			while self.position < len(self.origin):
				if self.origin[self.position].isdigit():
					temp += self.origin[self.position]
				elif not self.origin[self.position].isnumeric():
					break
				self.position += 1
			self.actual = Token(tipo="integer", value=int(temp))

		elif self.origin[self.position : self.position + 2] == "/*":
			self.actual = Token(tipo="comentary", value=0)
			self.position += 2
			while self.origin[self.position : self.position + 2] != "*/":
				self.position += 1
				if self.position >= len(self.origin):
					sys.exit("n fechou o comentario")
			self.position += 2

		elif self.origin[self.position] == "+":
			self.actual = Token(tipo="add", value=1)
			self.position += 1

		elif self.origin[self.position] == "-":
			self.actual = Token(tipo="sub", value=-1)
			self.position += 1

		elif self.origin[self.position] == "*":
			self.actual = Token(tipo="mult", value=1)
			self.position += 1

		elif self.origin[self.position] == "/":
			self.actual = Token(tipo="div", value=-1)
			self.position += 1

		elif self.origin[self.position] == ">":
			self.actual = Token(tipo=">", value=-1)
			self.position += 1
		
		elif self.origin[self.position] == "<":
			self.actual = Token(tipo="<", value=-1)
			self.position += 1

		elif self.origin[self.position] == "!":
			self.actual = Token(tipo="!", value=-1)
			self.position += 1

		elif self.origin[self.position] == "=":
			if(self.origin[self.position+1] == "="):
				self.actual = Token(tipo="==", value=-1)
				self.position += 2
			else:
				self.actual = Token(tipo="=", value=0)
				self.position += 1

		elif self.origin[self.position] == "&":
			if(self.origin[self.position+1] == "&"):
				self.actual = Token(tipo="&&", value=-1)
				self.position += 2
			else:
				sys.exit(f"only one & in condition on line {self.line}")

		elif self.origin[self.position] == "|":
			if(self.origin[self.position+1] == "|"):
				self.actual = Token(tipo="||", value=-1)
				self.position += 2
			else:
				sys.exit(f"only one | in condition on line {self.line}")

		elif self.origin[self.position] == "(":
			self.actual = Token(tipo="open_parenteses", value=-1)
			self.brackets += 1
			self.position += 1

		elif self.origin[self.position] == ")":
			self.actual = Token(tipo="close_parenteses", value=-1)
			self.brackets -= 1
			if self.brackets < 0:
				sys.exit("unbalanced parenteses")
			self.position += 1

		elif self.origin[self.position] == "{":
			self.actual = Token(tipo="open_chaves", value=-1)
			self.position += 1

		elif self.origin[self.position] == "}":
			self.actual = Token(tipo="close_chaves", value="}")
			self.position += 1

		elif self.origin[self.position] == "\"":
			tmp = ""
			self.position += 1
			while self.origin[self.position] != "\"":
				tmp += self.origin[self.position]
				self.position += 1
			
			self.position += 1
			self.actual = Token(tipo="string", value=tmp)

		elif self.origin[self.position] == "\'":
			tmp = ""
			self.position += 1
			while self.origin[self.position] != "\'":
				tmp += self.origin[self.position]
				self.position += 1
			self.position += 1			
			self.actual = Token(tipo="string", value=tmp)

		elif self.origin[self.position:self.position+len("true")] == "true":
			self.actual = Token(tipo="bool", value="true")
			self.position += len("true")

		elif self.origin[self.position:self.position+len("false")] == "false":
			self.actual = Token(tipo="bool", value="false")
			self.position += len("false")

		elif self.origin[self.position:self.position+len("println")] == "println":
			self.actual = Token(tipo="print", value="println")
			self.position += len("println")

		elif self.origin[self.position:self.position+len("if")] == "if":
			self.actual = Token(tipo="if", value="if")
			self.position += len("if")

		elif self.origin[self.position:self.position+len("while")] == "while":
			self.actual = Token(tipo="while", value="while")
			self.position += len("while")

		elif self.origin[self.position:self.position+len("else")] == "else":
			self.actual = Token(tipo="else", value="else")
			self.position += len("else")

		elif self.origin[self.position:self.position+len("readln")] == "readln":
			self.actual = Token(tipo="readln", value="readln")
			self.position += len("readln")
		
		elif self.origin[self.position:self.position+len("int")] == "int":
			self.actual = Token(tipo="var_type", value="int")
			self.position += len("int")
		
		elif self.origin[self.position:self.position+len("bool")] == "bool":
			self.actual = Token(tipo="var_type", value="bool")
			self.position += len("bool")
		
		elif self.origin[self.position:self.position+len("string")] == "string":
			self.actual = Token(tipo="var_type", value="string")
			self.position += len("string")

		elif self.origin[self.position] == ";":
			self.actual = Token(tipo=";", value=0)
			self.position += 1
			self.line += 1
			if self.origin[self.position] == "\n":
				self.position += 1
			if self.brackets != 0:
				sys.exit("unbalanced bracket")

		elif self.origin[self.position].isalpha():
			tmp = self.origin[self.position]
			self.position += 1
			while self.origin[self.position].isalpha() or self.origin[self.position].isnumeric() or self.origin[self.position] == "_":
				tmp += self.origin[self.position]
				self.position += 1
			self.actual = Token(tipo="var", value=tmp)

		else:
			print(ord(self.origin[self.position]))
			sys.exit(f"found a value not in {accepted_chars}")


class Parser:
	def __init__(self):
		self.tokens:Tokenizer = None
		self.symbolTable:SymbolTable = SymbolTable()
		self.writer = STDOUTWriter()

	def print_token(self):
		print(self.tokens.actual.tipo, self.tokens.actual.value)

	def getNextNotComentary(self):
		self.tokens.selectNext()
		while self.tokens.actual.tipo == "comentary":
			self.tokens.selectNext()

	def parseFactor(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "integer":
			value = self.tokens.actual.value
			self.getNextNotComentary()
			if self.tokens.actual.tipo == "integer":
				sys.exit(f"2 integers seguidas na linha  {self.tokens.line}")
			elif self.tokens.actual.tipo == "open_parenteses":
				sys.exit(f"int imediatamente antes de abrir parenteses na linha  {self.tokens.line}")
			return IntVal(value)

		if self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub" or self.tokens.actual.tipo == "!":
			return UnOp(self.tokens.actual.tipo, self.parseFactor())

		if self.tokens.actual.tipo == "open_parenteses":
			total = self.parseOr()
			self.getNextNotComentary()
			return total

		if self.tokens.actual.tipo == "bool":
			value = self.tokens.actual.value == "true"
			self.getNextNotComentary()
			return BoolVal(children=[value])

		# if self.tokens.actual.tipo == "string":
		# 	value = self.tokens.actual.value
		# 	self.getNextNotComentary()
		# 	return StrVal(children=[value])

		if self.tokens.actual.tipo == "var":
			var = self.tokens.actual.value
			self.getNextNotComentary()
			return VarVal([var], self.symbolTable)

		# if self.tokens.actual.tipo == "readln":
		# 	self.getNextNotComentary()
		# 	if self.tokens.actual.tipo != "open_parenteses":
		# 		sys.exit("sem parenteses depois de readln")

		# 	self.getNextNotComentary()
		# 	if self.tokens.actual.tipo != "close_parenteses":
		# 		sys.exit("sem fechar parenteses depois de readln")
		# 	return Readln()
			

		if self.tokens.actual.tipo == ";":
			sys.exit(f"operacao no final da linha {self.tokens.line}")
			
		if self.tokens.actual.tipo == "close_parenteses":
			sys.exit(f"int after close da linha  {self.tokens.line}")

		
		sys.exit(f"2 mult/div seguidos na linha {self.tokens.line}")

	def parseTerm(self):
		branch = self.parseFactor()
		
		while self.tokens.actual.tipo == "mult" or self.tokens.actual.tipo == "div":
			branch = BinOP(self.tokens.actual.tipo, [branch, self.parseFactor()])

		return branch
			
	def parseExpression(self):
		branch = self.parseTerm()
		while self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub":			
			branch = BinOP(self.tokens.actual.tipo, [branch, self.parseTerm()])

		return branch

	def variable_with_type(self):
		var_type = self.tokens.actual.value
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "var":
			var_name = self.tokens.actual.value
			self.getNextNotComentary()
			if self.tokens.actual.tipo == "=":
				exp = self.parseOr()
				return SetVar([var_name, var_type, exp], self.symbolTable)
			elif self.tokens.actual.tipo == ";":
				return SetVar([var_name, var_type], self.symbolTable)
			else:
				
				sys.exit(f"sem = depois de variavel na linha  {self.tokens.line}")
		else:
			sys.exit(f"sem var_name depois de tipo na linha  {self.tokens.line}")

	def println(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "open_parenteses":
			exp = self.parseOr()
			self.getNextNotComentary()
			return PrintOp([exp])
		sys.exit(f"sem ( depois de chamr println na linha  {self.tokens.line}")


	def parseIf(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo != "open_parenteses":
			
			sys.exit(f"no ( after if on line {self.tokens.line}")

		condition = self.parseOr()
		if self.tokens.actual.tipo != "close_parenteses":
			
			sys.exit(f"no ) closing if on line {self.tokens.line}")

		self.getNextNotComentary()
		blockIf = self.command()

		self.getNextNotComentary()

		if self.tokens.actual.tipo == "else":
			self.getNextNotComentary()
			blockElse = self.command()
			return IfOp(children=[condition, blockIf, blockElse])
		else:
			self.tokens.position -= len(self.tokens.actual.value)
			return IfOp(children=[condition, blockIf])
				
	def parseWhile(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo != "open_parenteses":
			sys.exit(f"no ( after while on line {self.tokens.line}")

		condition = self.parseOr()
		if self.tokens.actual.tipo != "close_parenteses":
			sys.exit(f"no ) closing while on line {self.tokens.line}")

		self.getNextNotComentary()
		block = self.command()
		return WhileOp(children=[condition, block])

	def parseOr(self):
		andexp = self.parseAnd()
		if self.tokens.actual.tipo == "||":
			cmp = CompOp(self.tokens.actual.tipo, children=[andexp, self.parseAnd()])
			while self.tokens.actual.tipo == "||":
				cmp = CompOp(self.tokens.actual.tipo, children=[cmp, self.parseAnd()])
			return cmp
		return andexp

	def parseAnd(self):
		iqualexp = self.parseIquals()
		if self.tokens.actual.tipo == "&&":
			cmp = CompOp(self.tokens.actual.tipo, children=[iqualexp, self.parseIquals()])
			while self.tokens.actual.tipo == "&&":
				cmp = CompOp(self.tokens.actual.tipo, children=[cmp, self.parseIquals()])
			return cmp
		return iqualexp

	def parseIquals(self):
		maiormenorexp: Node = self.parseRelExpr()

		if self.tokens.actual.tipo == "==":
			cmp = CompOp(self.tokens.actual.tipo, children=[maiormenorexp, self.parseRelExpr()])
			while self.tokens.actual.tipo == "==":
				cmp = CompOp(self.tokens.actual.tipo, children=[cmp, self.parseRelExpr()])
			return cmp
		return maiormenorexp

	def parseRelExpr(self):
		exp = self.parseExpression()

		if self.tokens.actual.tipo in [">", "<"]:
			cmp = CompOp(self.tokens.actual.tipo, [exp, self.parseExpression()])
			while self.tokens.actual.tipo in [">", "<"]:
				cmp = CompOp(self.tokens.actual.tipo, [cmp, self.parseExpression()])
			return cmp
		return exp

	def variable_already_declared(self):
		var_name = self.tokens.actual.value
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "=":
			exp = self.parseOr()
			return SetVar([var_name, exp], self.symbolTable)
		else:
			sys.exit(f"sem = depois de variavel na linha  {self.tokens.line}")

	def command(self):
		node = None
		if self.tokens.actual.tipo == "var_type":
			node = self.variable_with_type()
		elif self.tokens.actual.tipo == "var":
			node = self.variable_already_declared()
		elif self.tokens.actual.tipo == "print":
			node = self.println()
		elif self.tokens.actual.tipo == "if":
			node = self.parseIf()
		elif self.tokens.actual.tipo == "while":
			node = self.parseWhile()
		elif self.tokens.actual.tipo == ";":
			node = NoOp()
		elif self.tokens.actual.tipo == "open_chaves":
			node = self.parseBlock()
		return node

	def parseBlock(self):
		block = Block()

		if self.tokens.actual.tipo != "open_chaves":
			sys.exit(f"block cant start with {self.tokens.actual.tipo}")

		self.getNextNotComentary()
		while self.tokens.actual.tipo != "close_chaves":
			block.AddNode(self.command())
			self.getNextNotComentary()

		if self.tokens.actual.tipo != "close_chaves":
			sys.exit(f"block cant end with {self.tokens.actual.tipo}")

		return block

	def run(self, code: str):
		self.tokens = Tokenizer(code)
		# self.print_all_tokens()
		# return
		self.getNextNotComentary()
		self.parseBlock().Evaluate()
		STDOUTWriter.AddInstruction("\n; interrupcao de saida")
		STDOUTWriter.AddInstruction("POP EBP")
		STDOUTWriter.AddInstruction("MOV EAX, 1")
		STDOUTWriter.AddInstruction("INT 0x80")
		STDOUTWriter.Write()

	def print_all_tokens(self):
		self.tokens.selectNext()
		while self.tokens.actual.tipo != "EOF":
			
			# print()
			self.tokens.selectNext()
		

if __name__ == "__main__":
	parser = Parser()

	if len(sys.argv) == 1:
		sys.exit("sem input")

	with open(sys.argv[1], "r") as f:
		code = f.read()
	parser.run(code)