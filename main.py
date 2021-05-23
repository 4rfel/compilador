import sys
from abc import ABC, abstractmethod

var_table = {} # {varname:[vartipo, varvalue]}

class Node(ABC):
	def __init__(self, value = 0, children = []):
		self.value = value
		self.children:Node = children

	@abstractmethod
	def Evaluate(self):
		return

class BinOP(Node):
	def Evaluate(self):
		c0 = self.children[0].Evaluate()
		c1 = self.children[1].Evaluate()
		if c0[0] != "int" or c1[0] != "int":
			sys.exit("conta com variavel diferente de int")
		if self.value == "add":
			return ["int", c0[1] + c1[1]]
		if self.value == "sub":
			return ["int", c0[1] - c1[1]]
		if self.value == "mult":
			return ["int", c0[1] * c1[1]]
		if self.value == "div":
			return ["int", int(c0[1] / c1[1])]

		sys.exit("DEU RUIM")

class UnOp(Node):
	def Evaluate(self):
		if self.value == "add":
			return self.children.Evaluate()
		if self.value == "sub":
			return -self.children.Evaluate()
		if self.value == "!":
			return int(not self.children.Evaluate())

		sys.exit("DEU RUIM 2")

class IntVal(Node):
	def Evaluate(self):
		return self.value

class NoOp(Node):
	def Evaluate(self):
		return super().Evaluate()

class PrintOp(Node):
	def Evaluate(self):
		print(self.children[0].Evaluate()[1])

class SetVar(Node):
	def Evaluate(self):
		global var_table
		var_name = self.children[0]
		if var_name not in var_table:
			
			var_type = self.children[1]
			if len(self.children) == 3:
				var_value = self.children[2].Evaluate()
			else:
				if(var_type == "bool"):
					var_value = False
				if(var_type == "string"):
					var_value = ""
				if(var_type == "int"):
					var_value = 0
		else:
			var_type = var_table[var_name][0]
			var_value = self.children[1].Evaluate()
		
		if type(var_value) == list:
			var_value = var_value[1]
		

		if(var_type == "bool"):
			var_table[var_name] = [var_type, bool(var_value)]
		if(var_type == "string"):
			var_table[var_name] = [var_type, str(var_value)]
		if(var_type == "int"):
			var_table[var_name] = [var_type, int(var_value)]

class VarVal(Node):
	def __init__(self, children):
		super().__init__(value=None, children=children)

	def Evaluate(self):
		return var_table[self.children[0]]

class Readln(Node):
    def Evaluate(self):
        i = input()
        if i.isnumeric():
            return ["int", int(i)]
        else:
            return ["string", i]

class CompOp(Node):
	def Evaluate(self):
		c0 = self.children[0].Evaluate()
		c1 = self.children[1].Evaluate()

		if self.value == "==":
			return c0 == c1

		if self.value == "<":
			return c0 < c1

		if self.value == ">":
			return c0 > c1

		if self.value == "&&":
			return bool(c0) and bool(c1)

		if self.value == "||":
			return bool(c0) or bool(c1)
		
		sys.exit("DEU RUIM 3")

class IfOp(Node):
	def Evaluate(self):
		if self.children[0].Evaluate():
			return self.children[1].Evaluate()
		elif len(self.children) == 3:
			return self.children[2].Evaluate()

class WhileOp(Node):
	def __init__(self, children):
			super().__init__(value=None, children=children)

	def Evaluate(self):
		while self.children[0].Evaluate():
			self.children[1].Evaluate()

class BoolVal(Node):
	def __init__(self, children):
			super().__init__(value=None, children=children)

	def Evaluate(self):
		return bool(self.children[0])

class StrVal(Node):
	def __init__(self, children):
			super().__init__(value=None, children=children)

	def Evaluate(self):
		return str(self.children[0])


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
		self.tokens: Tokenizer = None

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
			return IntVal(value, [])

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

		if self.tokens.actual.tipo == "string":
			value = self.tokens.actual.value
			self.getNextNotComentary()
			return StrVal(children=[value])

		if self.tokens.actual.tipo == "var":
			var = self.tokens.actual.value
			self.getNextNotComentary()
			return VarVal(children=[var])

		if self.tokens.actual.tipo == "readln":
			self.getNextNotComentary()
			if self.tokens.actual.tipo != "open_parenteses":
				sys.exit("sem parenteses depois de readln")

			self.getNextNotComentary()
			if self.tokens.actual.tipo != "close_parenteses":
				sys.exit("sem fechar parenteses depois de readln")
			return Readln()
			

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
				return SetVar(0, [var_name, var_type, exp])
			elif self.tokens.actual.tipo == ";":
				return SetVar(0, [var_name, var_type])
			else:
				
				sys.exit(f"sem = depois de variavel na linha  {self.tokens.line}")
		else:
			sys.exit(f"sem var_name depois de tipo na linha  {self.tokens.line}")

	def println(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "open_parenteses":
			exp = self.parseOr()
			self.getNextNotComentary()
			return PrintOp(0, [exp])
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
			return SetVar(0, [var_name, exp])
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