import sys


class Token:
	def __init__(self, tipo: str, value: int):
		self.tipo: str = tipo
		self.value: int = value


accepted_chars = "[-+*/ 0-9]"


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
			while self.origin[self.position : self.position + 2] != "*/":
				self.position += 1
				if self.position == len(self.origin) - 1:
					sys.exit("n fechou o comentario")
			self.position += 2

		elif self.origin[self.position] == "+":
			self.actual = Token(tipo="symbol", value=1)
			self.position += 1

		elif self.origin[self.position] == "-":
			self.actual = Token(tipo="symbol", value=-1)
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
			return self.tokens.actual.value

		if self.tokens.actual.tipo == "symbol":
			return self.tokens.actual.value * self.parseFactor()

		if self.tokens.actual.tipo == "open":
			total = self.parseExpression()
			self.getNextNotComentary()
			return total

	def parseTerm(self):
		total = self.parseFactor()
		self.getNextNotComentary()
		while self.tokens.actual.tipo == "mult" or self.tokens.actual.tipo == "div":
			if self.tokens.actual.tipo == "mult":
				total *= self.parseFactor()

			elif self.tokens.actual.tipo == "div":
				total //= self.parseFactor()

			self.getNextNotComentary()

		return total
	
			
	def parseExpression(self):
		total = self.parseTerm()

		while self.tokens.actual.tipo == "symbol":
			if self.tokens.actual.tipo == "symbol":
				signal = self.tokens.actual.value
				total += signal * self.parseFactor()
				self.getNextNotComentary()

		return int(total)

	def run(self, code: str):
		self.tokens = Tokenizer(code)
		return self.parseExpression()


parser = Parser()

if len(sys.argv) == 1:
	sys.exit("sem input")

print(parser.run(sys.argv[1]))