import sys
from abc import ABC, abstractmethod

class Token:
	def __init__(self, tipo: str, value: int):
		self.tipo: str = tipo
		self.value: int = value


class Node(ABC):
	def __init__(self, value = 0, children = []):
		self.value = value
		self.children = children

	@abstractmethod
	def Evaluate(self):
		return

class BinOP(Node):
	def Evaluate(self):
		if len(self.children) != 2:
			sys.exit("BinOP diferente de 2 filhos")

		if self.value == "add":
			return self.children[0].Evaluate() + self.children[1].Evaluate()
		if self.value == "sub":
			return self.children[0].Evaluate() - self.children[1].Evaluate()
		if self.value == "mult":
			return self.children[0].Evaluate() * self.children[1].Evaluate()
		if self.value == "div":
			return self.children[0].Evaluate() // self.children[1].Evaluate()

		sys.exit("DEU RUIM")

class UnOp(Node):
	def Evaluate(self):
		if len(self.children) != 1:
			sys.exit("UnOp diferente de 1 filho")
		if self.value == "add":
			return self.children[0].Evaluate()
		if self.value == "sub":
			return -self.children[0].Evaluate()
		
		sys.exit("DEU RUIM 2")

class IntVal(Node):
	def Evaluate(self):
		if len(self.children) != 0:
			sys.exit("IntVal tem Filho")

		return self.value

class NoOp(Node):
	pass	

accepted_chars = "[-+*/ 0-9()]"


class Tokenizer:
	def __init__(self, origin: str):
		self.origin: str = origin + " "
		self.position: int = 0
		self.actual: Token = None
		self.brackets = 0

	def selectNext(self):
		while self.origin[self.position] == " ":
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
				elif self.origin[self.position] in ["+", "-", " ", "*", "/", "(", ")"]:
					break
				elif not self.origin[self.position].isnumeric():
					sys.exit(f"found a value not in {accepted_chars}")
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

		else:
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
				sys.exit("2 integers seguidas")
			return IntVal(value)

		if self.tokens.actual.tipo == "symbol":
			return UnOp(self.tokens.actual, self.parseFactor())

		if self.tokens.actual.tipo == "open":
			total = self.parseExpression()
			self.getNextNotComentary()
			return total

		if self.tokens.actual.tipo == "EOF":
			sys.exit("operacao no final")
			
		sys.exit("2 mult/div seguidos")

	def parseTerm(self):
		branch = self.parseFactor()
		
		while self.tokens.actual.tipo == "mult" or self.tokens.actual.tipo == "div":
			if self.tokens.actual.tipo == "mult" or self.tokens.actual.tipo == "div":
				branch = BinOP(self.tokens.actual.tipo, [branch, self.parseFactor()])

		return branch
	
			
	def parseExpression(self):
		branch = self.parseTerm()
		while self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub":			
			if self.tokens.actual.tipo == "add" or self.tokens.actual.tipo == "sub":
				branch = branch = BinOP(self.tokens.actual.tipo, [branch, self.parseTerm()])

		return branch

	def run(self, code: str):
		self.tokens = Tokenizer(code)
		tree = self.parseExpression()
		return tree.Evaluate()


parser = Parser()

if len(sys.argv) == 1:
	sys.exit("sem input")

with open(sys.argv[1], "r") as f:
	code = f.read()
# print(code)
print(parser.run("1+1"))