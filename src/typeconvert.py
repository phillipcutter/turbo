# Converts Python syntax to Haxe syntax
import re

forRegex = re.compile(r"for\s+(?P<var>[A-Za-z0-9_]+)\s+in\s(?:range\((?P<range>[0-9]+)\)|(?P<ref>[A-Za-z0-9_]+)):")

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


varRegexStr = r"(?<!\.)(?=(?:[^\S]|^|\[|\(|\-|\\|\+|\=|\%|\*)*){}(?=[^\S]|$|\]|\)|\-|\\|\+|\=|\%|\*|\.)"
def replaceVar(string, replaceOld, replaceNew):
	import util
	"""Takes a string, old var, and new var. This function returns the new line with only references to the old
	replace var with the new replace var"""

	varRegex = re.compile(varRegexStr.format(replaceOld))
	occurences = [m.start() for m in varRegex.finditer(string)]
	newStrLst = list(string)
	for occurence in occurences:
		for i in range(len(replaceNew)):
			forceInsert = True
			if i < len(replaceOld):
				forceInsert = False
			newStrLst = util.updateOrAddToList(newStrLst, i + occurence, replaceNew[i], forceInsert=forceInsert)

	return "".join(list(newStrLst))

importsRegexStr = r"{}\s*\((?:.*)\)"
importsFromFunc = {
	"print": "import Sys.print;"
}
def getImports(code, newLineEnd=False):
	imports = []
	for key, val in importsFromFunc.items():
		if re.search(importsRegexStr.format(key), "\n".join([line.text for line in code.getLines()])):
			imports.append(val)

	return "\n".join(imports) + "\n" if newLineEnd else ""

haxeFuncStr = """static function {}({}) """
haxeParamStr = """{}:Dynamic"""
def haxeFunc(name, params):
	if isinstance(params, str):
		params = params.replace(" ", "").split(",")

	formattedParams = []
	for param in params:
		formattedParams.append(haxeParamStr.format(param))

	return haxeFuncStr.format(name, ", ".join(formattedParams)) + "{"