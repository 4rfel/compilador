import sys
import re

numbers = re.split("[+-]", sys.argv[1])
numbers = [x.strip() for x in numbers]
for i in numbers:
    for j in i:
        if j == " ":
            print("found a number with a space in the middle")
            exit(1)

if numbers[0] == "":
    numbers[0] = 0
numbers = [float(x) for x in numbers]

operators = re.split("[0-9]", sys.argv[1].replace(" ", ""))
operators = list(filter(lambda a: a != "", operators))

result = numbers[0]
for i, operator in enumerate(operators):
    if operator == "+":
       result += numbers[i+1]
    else:
        result -= numbers[i+1]

print(result)