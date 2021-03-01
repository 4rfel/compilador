import sys

def split_by_list(l, s):
	s = s.split(l[0])
	for i in l[1:]:
		temp = []
		for j in s:
			temp += j.split(i)
		s = temp
	return s

if len(sys.argv) == 1:
	print("invalid input")
	exit(1)

numbers = split_by_list(["+", "-"], sys.argv[1])
numbers = [x.strip() for x in numbers]
for i in numbers:
	for j in i:
		if j == " ":
			print("invalid input")
			exit(1)
	if i == "":
		print("invalid input")
		exit(1)

if numbers[0] == "":
	numbers[0] = 0

numbers = [float(x) for x in numbers]

l = [str(x) for x in range(10)]
operators = sys.argv[1].replace(" ", "")
operators = split_by_list(l, operators)
operators = list(filter(lambda a: a != "", operators))

result = numbers[0]
for i, operator in enumerate(operators):
	if operator == "+":
	   result += numbers[i+1]
	else:
		result -= numbers[i+1]

print(result)