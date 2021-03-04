import sys

class Token:
	def __init__(self, tipo:str, value:int):
		self.tipo: str = tipo
		self.value: int = value

class Tokenizer:
	def __init__(self, origin:str):
		self.origin: str = origin + " "
		self.position: int = 0
		self.actual: Token = None

	def selectNext(self):
		while self.origin[self.position] == " ":
			if self.position == len(self.origin)-1:
				self.actual = Token(tipo="EOF", value=0)
				return
			self.position += 1

		if self.origin[self.position].isdigit():
			temp = ""
			while self.position < len(self.origin):
				if self.origin[self.position].isdigit():
					temp += self.origin[self.position]
				elif self.origin[self.position] in ["+", "-", " "]:
					break
				elif not self.origin[self.position].isnumeric():
					raise ValueError("found a value not in [-+ 0-9]")
				self.position += 1
			self.actual = Token(tipo="integer", value=int(temp))

		elif self.origin[self.position] == "+":
			self.actual = Token(tipo="symbol", value=1)
			self.position += 1

		elif self.origin[self.position] == "-":
			self.actual = Token(tipo="symbol", value=-1)
			self.position += 1

		elif self.position == len(self.origin)-1:
			self.actual = Token(tipo="EOF", value=0)
			self.position += 1
			
		else:
			raise ValueError("found a value not in [-+ 0-9]")

class Parser:
	def __init__(self):
		self.tokens: Tokenizer = None

	def parseExpression(self):
		self.tokens.selectNext()
		if self.tokens.actual.tipo == "integer":
			total = self.tokens.actual.value
			last = self.tokens.actual
		else:
			raise ValueError("1 token != integer")

		while self.tokens.actual.tipo != "EOF":
			self.tokens.selectNext()
			if self.tokens.actual.tipo == "integer" and last.tipo == "symbol":
				total += last.value * self.tokens.actual.value
			elif self.tokens.actual.tipo == last.tipo:
				raise ValueError("2 tokens do mesmo tipo seguidos")
			if self.tokens.actual.tipo != "EOF":
				last = self.tokens.actual

		if last.tipo == "symbol":
			raise ValueError("termina em simbolo")

		return total

	def run(self, code:str):
		self.tokens = Tokenizer(code)
		return self.parseExpression()

parser = Parser()

if len(sys.argv) == 1:
	raise ValueError("sem input")

print(parser.run(sys.argv[1]))