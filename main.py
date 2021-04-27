import sys
from abc import ABC, abstractmethod

class Node(ABC):
	def __init__(self, value = 0, children = []):
		self.value = value
		self.children = children

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
				elif self.origin[self.position] in ["+", "-", " ", "*", "/", "(", ")", ""]:
					break
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

		elif self.origin[self.position] == "(":
			self.actual = Token(tipo="open", value=-1)
			self.brackets += 1
			self.position += 1

		elif self.origin[self.position] == ")":
			self.actual = Token(tipo="close", value=-1)
			self.brackets -= 1
			if self.brackets < 0:
				sys.exit("unbalanced bracket")
			self.position += 1

		elif self.origin[self.position] == "=":
			self.actual = Token(tipo="=", value=0)
			self.position += 1

		elif self.origin[self.position:self.position+len("println")] == "println":
			self.actual = Token(tipo="print", value=0)
			self.position += len("println")

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

var_table = {}
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
			elif self.tokens.actual.tipo == "open":
				sys.exit(f"int imediatamente antes de abrir parenteses na linha  {self.tokens.line}")
			return IntVal(value, [])

		if self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub":
			return UnOp(self.tokens.actual.tipo, self.parseFactor())

		if self.tokens.actual.tipo == "open":
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

		if self.tokens.actual.tipo == ";":
			sys.exit(f"operacao no final da linha  {self.tokens.line}")
			
		if self.tokens.actual.tipo == "close":
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
			var_table[var] = exp.Evaluate()

		else:
			sys.exit(f"sem = depois de variavel na linha  {self.tokens.line}")

	def println(self):
		self.getNextNotComentary()
		if self.tokens.actual.tipo == "open":
			exp = self.parseExpression()
			print(exp.Evaluate())
			self.getNextNotComentary()

	def command(self):
		if self.tokens.actual.tipo == "var":
			self.variable()
		elif self.tokens.actual.tipo == "print":
			self.println()

	def run(self, code: str):
		self.tokens = Tokenizer(code)
		# self.print_all_tokens()
		# return
		self.getNextNotComentary()
		while self.tokens.actual.tipo != "EOF":
			self.command()			
			if self.tokens.actual.tipo != ";":
				sys.exit(f"command n terminou em \";\" na linha {self.tokens.line}")
			self.getNextNotComentary()

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