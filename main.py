import sys
from abc import ABC, abstractmethod

var_table = {}

class Node(ABC):
	def __init__(self, value = 0, children = []):
		self.value = value
		self.children:Node = children

	@abstractmethod
	def Evaluate(self):
		return

class BinOP(Node):
	def Evaluate(self):
		if self.value == "add":
			return self.children[0].Evaluate() + self.children[1].Evaluate()
		if self.value == "sub":
			return self.children[0].Evaluate() - self.children[1].Evaluate()
		if self.value == "mult":
			return self.children[0].Evaluate() * self.children[1].Evaluate()
		if self.value == "div":
			return int(self.children[0].Evaluate() / self.children[1].Evaluate())

		sys.exit("DEU RUIM")

class UnOp(Node):
	def Evaluate(self):
		if self.value == "add":
			return self.children.Evaluate()
		if self.value == "sub":
			return -self.children.Evaluate()
		sys.exit("DEU RUIM 2")

class IntVal(Node):
	def Evaluate(self):
		return self.value

class NoOp(Node):
	pass

class PrintOp(Node):
	def Evaluate(self):
		print(self.children[0].Evaluate())

class SetVar(Node):
	def Evaluate(self):
		global var_table
		var = self.children[0].value
		var_table[var] = self.children[1].Evaluate()

class VarVal(Node):
	def Evaluate(self):
		return var_table[self.value]

class Readln(Node):
    def Evaluate(self):
        i = input()
        if i.isnumeric():
            return int(i)
        else:
            raise ValueError("input must be an int")

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
			return c0 and c1

		if self.value == "||":
			return c0 or c1
		
		sys.exit("DEU RUIM 3")

class IfOp(Node):
	def Evaluate(self):
		if self.children[0].Evaluate():
			return self.children[1].Evaluate()
		elif len(self.children) == 3:
			return self.children[2].Evaluate()

class WhileOp(Node):
	def Evaluate(self):
		while self.children[0].Evaluate():
			return self.children[1].Evaluate()

class Block(Node):
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
			self.actual = Token(tipo="maior", value=-1)
			self.position += 1
		
		elif self.origin[self.position] == "<":
			self.actual = Token(tipo="menor", value=-1)
			self.position += 1

		elif self.origin[self.position] == "!":
			self.actual = Token(tipo="not", value=-1)
			self.position += 1

		elif self.origin[self.position] == "=":
			if(self.origin[self.position+1] == "="):
				self.actual = Token(tipo="==", value=-1)
				self.position += 2
			else:
				sys.exit(f"assign in condition on line {self.line}")

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
			# self.brackets += 1
			self.position += 1

		elif self.origin[self.position] == "}":
			self.actual = Token(tipo="close_chaves", value=-1)
			# self.brackets -= 1
			# if self.brackets < 0:
			# 	sys.exit("unbalanced chaves")
			self.position += 1

		elif self.origin[self.position] == "=":
			self.actual = Token(tipo="=", value=0)
			self.position += 1

		elif self.origin[self.position:self.position+len("println")] == "println":
			self.actual = Token(tipo="print", value=len("println"))
			self.position += len("println")

		elif self.origin[self.position:self.position+len("if")] == "if":
			self.actual = Token(tipo="if", value=len("if"))
			self.position += len("if")

		elif self.origin[self.position:self.position+len("while")] == "while":
			self.actual = Token(tipo="while", value=len("while"))
			self.position += len("while")

		elif self.origin[self.position:self.position+len("else")] == "else":
			self.actual = Token(tipo="else", value=len("else"))
			self.position += len("else")

		elif self.origin[self.position:self.position+len("readln")] == "readln":
			self.actual = Token(tipo="readln", value=len("readln"))
			self.position += len("readln")

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

		if self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub":
			return UnOp(self.tokens.actual.tipo, self.parseFactor())

		if self.tokens.actual.tipo == "open_parenteses":
			total = self.parseExpression()
			self.getNextNotComentary()
			return total

		if self.tokens.actual.tipo == "var":
			if self.tokens.actual.value in var_table:
				total = var_table[self.tokens.actual.value]
			else:
				sys.exit(f"variavel acessada antes de definir na linha  {self.tokens.line}")
			self.getNextNotComentary()
			return IntVal(total, [])

		elif self.tokens.actual.tipo == "readln":

			self.tokens.selectNext()
			if self.tokens.actual.tipo != "open_parenteses":
				sys.exit("sem parenteses depois de readln")

			self.tokens.selectNext()
			if self.tokens.actual.tipo != "close_parenteses":
				sys.exit("sem fechar parenteses depois de readln")

		if self.tokens.actual.tipo == ";":
			sys.exit(f"operacao no final da linha  {self.tokens.line}")
			
		if self.tokens.actual.tipo == "close_parenteses":
			sys.exit(f"int after close da linha  {self.tokens.line}")

		sys.exit(f"2 mult/div seguidos na linha  {self.tokens.line}")

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

	def variable(self):
		global var_table
		var = self.tokens.actual.value
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "=":
			exp = self.parseExpression()
			return SetVar(0, [var, exp])

		else:
			sys.exit(f"sem = depois de variavel na linha  {self.tokens.line}")

	def println(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "open_parenteses":
			exp = self.parseExpression()
			self.getNextNotComentary()
			return PrintOp(0, [exp])
		sys.exit(f"sem ( depois de chamr println na linha  {self.tokens.line}")


	def parseIf(self):
		self.getNextNotComentaryself.getNextNotComentary()()
		if self.tokens.actual.tipo != "if":
			self.getNextNotComentary()
			if self.tokens.actual.tipo != "open_parenteses":
				sys.exit(f"no ( after if on line {self.tokens.line}")
			condition = self.parseOr()
			self.getNextNotComentary()
			if self.tokens.actual.tipo != "close_parenteses":
				sys.exit(f"no ) closing if on line {self.tokens.line}")
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
		if self.tokens.actual.tipo != "while":
			self.getNextNotComentary()
			if self.tokens.actual.tipo != "open_parenteses":
				sys.exit(f"no ( after while on line {self.tokens.line}")

			condition = self.parseOr()
			if self.tokens.actual.tipo != "close_parenteses":
				sys.exit(f"no ) closing while on line {self.tokens.line}")

			block = self.command()
			return WhileOp(children=[condition, block])

	def parseOr(self):
		andexp = self.parseAnd()
		if self.tokens.actual.tipo == "||":
			cmp = CompOp(children=[andexp, self.parseIquals()])
			while self.tokens.actual.tipo == "||":
				cmp = CompOp(children=[cmp, self.parseAnd()])
			return cmp
		return andexp

	def parseAnd(self):
		iqualexp = self.parseAnd()
		if self.tokens.actual.tipo == "&&":
			cmp = CompOp(children=[iqualexp, self.parseIquals()])
			while self.tokens.actual.tipo == "&&":
				cmp = CompOp(children=[cmp, self.parseIquals()])
			return cmp
		return iqualexp

	def parseIquals(self):
		maiormenorexp: Node = self.parseRelExpr()

		if self.tokens.actual.tipo == "==":
			cmp = CompOp(children=[maiormenorexp, self.parseRelExpr()])
			while self.tokens.actual.tipo == "==":
				cmp = CompOp(children=[cmp, self.parseRelExpr()])
			return cmp
		return maiormenorexp

	def parseRelExpr(self):
		exp = self.parseExpression()

		if self.tokens.actual.tipo in [">", "<"]:
			cmp = CompOp(self.tokens.actual, exp, self.parseExpression())
			while self.tokens.actual.tipo in [">", "<"]:
				cmp = CompOp(self.tokens.actual, cmp, self.parseExpression())
			return cmp
		return exp
				

	def command(self):
		node = None
		if self.tokens.actual.tipo == "var":
			node = self.variable()
		elif self.tokens.actual.tipo == "print":
			node = self.println()
		elif self.tokens.actual.tipo == "if":
			node = self.parseIf()
		elif self.tokens.actual.tipo == "while":
			node = self.parseWhile()
		# elif self.tokens.actual.tipo == "close_chaves":
		# 	node = self.println()

		return node

	def parseBlock(self):
		block = Block()

		if self.tokens.actual.tipo != "open_chaves":
			sys.exit(f"block cant start with {self.tokens.actual.tipo}")

		self.getNextNotComentary()
		while self.tokens.actual.tipo != self.tokens.actual.tipo != "close_chaves":
			block.addNode(self.command())
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
			print(self.tokens.actual.tipo, self.tokens.actual.value)
			self.tokens.selectNext()
		print(self.tokens.actual.tipo, self.tokens.actual.value)
		

if __name__ == "__main__":
	parser = Parser()

	if len(sys.argv) == 1:
		sys.exit("sem input")

	with open(sys.argv[1], "r") as f:
		code = f.read()
	parser.run(code)