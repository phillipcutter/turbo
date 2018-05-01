import sys
import os
import subprocess
import argparse
import plyplus, plyplus.grammars
import util
import match
import typeconvert

# Args
parser = argparse.ArgumentParser(description='Convert Python to Machine Code with concentrated magic.')
parser.add_argument('file', metavar='file', type=str,
                    help='.py file to convert to an executable')
parser.add_argument("-d", "--debug", action="store_true",
                    help='turn on more descriptive debug output')
parser.add_argument("-n", "--nocomp", action="store_true",
                    help='do not compile into c++, just create Haxe file')
parser.add_argument("-r", "--norun", action="store_true",
                    help='do not run the file, just compile')
parser.add_argument("-t", "--trace", action="store_true",
                    help='add location traces to all print statements')

args = parser.parse_args()

file = args.file

def parseTok(tok):
	tType = tok.type
	tVal = tok.value
	tLineno = tok.lineno
	tLexpos = tok.Lexpos

	if not tLineno:
		pass

	if tType == "DEF":
		pass
	if tType == "IF":
		pass


def proccessBranch(branch):
	tail = branch.tail
	namedTail = branch.named_tail
	if branch.head == "funcdef":
		name = namedTail["name"][0].tail[0]
		if not namedTail["parameters"][0].tail:
			params = []
		else:
			pass
			params = []

		syntax = typeconvert.haxeFunc(name, params)
		print("Syntax: " + str(syntax))
		pass
	else:
		return
		raise Exception("Unexpected property: " + branch.head)


def main():
	fileContents = open(file).read()

	if not fileContents.endswith("\n"):
		fileContents += "\n"
	# Load lexical parser
	gram = util.getGrammar()
	lex = gram.lex(fileContents)
	ast = gram.parse(fileContents)
	code = util.Code(fileContents.split("\n"))

	tokArr = []
	lineTokDict = {} # Line number: [Token objects]

	for tok in lex:
		tLineno = tok.lineno
		tokArr.append(tok)

		if lineTokDict.get(tLineno, False):
			lineTokDict[tLineno].append(tok)
		else:
			lineTokDict[tLineno] = [tok]

	print(123)
	# util.tailsOfTree(parse)

	setInfo = {}  # Key: Line number, Val: {"Action": "Value"}
	# Set info allows you to queue changes in future lines before they have gotten to them
	out = ""  # Output code

	if ast.head == "start":
		for branch in ast.tail:
			proccessBranch(branch)
	else:
		raise Exception("The AST does not start with 'start'. AST: \n" + str(ast))

	# for tok in tokArr:
	# 	parseTok(tok)


if __name__ == "__main__":
	main()
