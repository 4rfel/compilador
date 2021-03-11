import sys

class Token:
	def __init__(self, tipo:str, value:int):
		self.tipo: str = tipo
		self.value: int = value

accepted_chars = "[-+*/ 0-9]"

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
				elif self.origin[self.position] in ["+", "-", " ", "*", "/"]:
					break
				elif not self.origin[self.position].isnumeric():
					sys.exit(f"found a value not in {accepted_chars}")
				self.position += 1
			self.actual = Token(tipo="integer", value=int(temp))

		elif self.origin[self.position:self.position+2] == "/*":
			self.actual = Token(tipo="comentary", value=0)
			while self.origin[self.position:self.position+2] != "*/":
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
			self.actual = Token(tipo="multdiv", value=1)
			self.position += 1
		
		elif self.origin[self.position] == "/":
			self.actual = Token(tipo="multdiv", value=-1)
			self.position += 1

		elif self.position == len(self.origin)-1:
			self.actual = Token(tipo="EOF", value=0)
			self.position += 1
			
		else:
			sys.exit(f"found a value not in {accepted_chars}")

class Parser:
	def __init__(self):
		self.tokens: Tokenizer = None

	def parseExpression(self):
		self.tokens.selectNext()
		while self.tokens.actual.tipo == "comentary":
			self.tokens.selectNext()

		if self.tokens.actual.tipo == "integer":
			total = self.tokens.actual.value
			last = self.tokens.actual
			last_int = total
			last_tipo = "integer"
		else:
			sys.exit("1 token != integer")

		last_op = 0 # 0 == +-, 1 == */
		signal = 1

		while self.tokens.actual.tipo != "EOF":
			self.tokens.selectNext()

			if self.tokens.actual.tipo == "symbol":
				signal = self.tokens.actual.value
				self.tokens.selectNext()
				last = self.tokens.actual

				total += signal * last.value
				last_op = 0

			elif self.tokens.actual.tipo == "multdiv":
				if last_op == 0:
					total -= signal * last_int
				elif last_op == 1:
					total -= last_int

				signal = self.tokens.actual.value
				self.tokens.selectNext()
				last = self.tokens.actual


				if signal == 1:
					last_int *= self.tokens.actual.value
					total += last_int
				else:
					last_int /= self.tokens.actual.value
					total += last_int
				last_op = 1
			
			if ((last.tipo == "symbol" or last.tipo == "multdiv") and
			(self.tokens.actual.tipo == "symbol" or self.tokens.actual.tipo == "multdiv")):
				sys.exit("2 simbolos seguidos fora de comentario")

			elif last.tipo == "EOF" or last.tipo == "comentary":
				sys.exit("termina em operacao")

		return int(total)
 
	def run(self, code:str):
		self.tokens = Tokenizer(code)
		return self.parseExpression()

parser = Parser()

if len(sys.argv) == 1:
	sys.exit("sem input")

print(parser.run(sys.argv[1]))