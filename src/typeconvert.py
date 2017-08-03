# Converts Python syntax to Haxe syntax
import re

forRegex = re.compile(r"for\s+(?P<var>[A-Za-z0-9_])\s+in\s(?:range\((?P<range>[0-9]+)\)|(?P<ref>[A-Za-z0-9_]+)):")

def convertFor(string):
	# Before --
	# for i in range(1000):
	#   print(i)
	# After --
	# for (i in 0..1000) {
	#   print(i)
	# }
	results = forRegex.search(string)
	if not results:
		return False
	return results.groupdict()

ifRegex = re.compile(r"(?P<kw>if|elif)\s+(?P<expr>.+[^:]):")
def convertIf(string):
	if string.startswith("else"):
		return {"keyword": "else", "expression": None}

	results = ifRegex.search(string)

	if not results:
		return False

	expression = results.group("expr")
	if expression.startswith("not"):
		expression = "!" + expression[3:]

	expression = expression.replace("and", "&&").replace("or", "||")

	keyword = results.group("kw").replace("elif", "else if")

	return {"expression": expression, "keyword": keyword}