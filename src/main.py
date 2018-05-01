import sys
import os
import subprocess
import argparse
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

def main():
	filePath = args.file
	debug = args.debug

	with open(os.path.join(os.path.dirname(__file__), filePath), "r") as file:
		code = util.Code(file.read().split("\n"))
		fileName = os.path.basename(file.name)
		hxFileName = util.getHxFileNameFromPy(fileName)

	tabSize = 4
	newValLines = []
	# Prepass -- good for renaming functions, classes, vars, and converting spaces to tabs ;)
	for lineObj in code.getLines():
		line = lineObj.text
		lineNumber = lineObj.number

		originalLine = line
		line = line.replace(" " * tabSize, "\t")

		if not line.strip():
			line = None
		else:

			info = match.expInfo(line.strip())

			if info:
				if info["exp"] == "=":
					parse = True

					name = info["name"]
					val = info["val"]

					if "__turbo_var__" in name or "__turbo_var__" in dict(newValLines).get(lineNumber, ""):
						parse = False

					initializeVar = [False]

					# /r/ShowerThoughts sorta thing -- vars inside the scope of an if, elif, else need to be
					# exposed to code outside of that specific scope, in Python they are always exposed outside of an if
					# Bonus -- Horrible function name was created below! :)
					if code.getParentOfNest(lineNumber).text.strip().startswith(("if", "else", "elif", "for", "while")):
						parentNestFirstLineNumber = code.getParentNestFirstLineLineNumber(lineNumber)
						nest = code.getNestOfLine(parentNestFirstLineNumber, sameIndentationToo=True, lineNumDict=True)
						initializeVar = [True, parentNestFirstLineNumber]
					else:
						nest = code.getNestOfLine(lineNumber, sameIndentationToo=True, lineNumDict=True)
					if not nest:
						parse = False
					nestList = [[k, v] for k, v in nest.items()]
					nestValString = "\n".join([val for key, val in nest.items()])

					if parse and name in nestValString:
						newName = code.getVarName(name)
						newNest = dict([[lineNum, lineStr.replace(name, newName)] for lineNum, lineStr in nestList])
						line = line.replace(name, newName)
						for newLineNumber, newLine in newNest.items():
							if dict(newValLines).get(newLineNumber, False):
								newValLines = dict(newValLines)
								oldLine = dict(newValLines).get(newLineNumber)
								newValLines[newLineNumber] = typeconvert.replaceVar(oldLine, name, newName)
								newValLines = [[k, v] for k, v in newValLines.items()]
							else:
								oldLine = code.getLine(newLineNumber).text
								newValLines.append(
									[newLineNumber, typeconvert.replaceVar(oldLine, name, newName)])
						if initializeVar[0]:
							initializeLocation = initializeVar[1]
							tabsForInitialization = "\t" * util.tabsOf(code.getLine(initializeLocation).text)
							varInitializationStr = tabsForInitialization + f"var {newName}:Dynamic = null"
							if dict(newValLines).get(initializeLocation, False):
								newValLines = dict(newValLines)
								oldLine = dict(newValLines).get(initializeLocation)
								newValLines[initializeLocation] = varInitializationStr + "\n" + oldLine
								newValLines = [[k, v] for k, v in newValLines.items()]
							else:
								oldLine = code.getLine(initializeLocation).text
								newValLines.append(
									[initializeLocation, varInitializationStr + "\n" + oldLine])



		if originalLine != line:
			newValLines.append([lineNumber, line])

	code.setLines(newValLines)

	a = 1
	print("First pass")
	for line in code.getLines():
		print(f"{a}: {line.text}")
		a += 1

	lineNumber = 1
	newValLines = []
	for lineObj in code.getLines():
		line = lineObj.text

		addSemicolon = True

		originalLine = line

		if line.strip().startswith("#"):
			line = None
		elif line.strip().startswith("for"):
			info = typeconvert.convertFor(line.strip())

			if info:
				if info["range"]:
					haxeVar = f"for ({info['var']} in 0...{info['range']}) " + "{"
					line = line.replace(line.strip(), haxeVar)
					# nestedCode = code.getNestOfLine(lineNumber)
					# haxeVar += nestedCode + "\n}"
					addSemicolon = False
		elif line.strip().startswith(("if", "elif", "else")):
			info = typeconvert.convertIf(line.strip())

			if util.quoteInsensitiveSearch(line.strip(), "if __name__ == \"__main__\":"):
				info = False

			if info:
				if info["keyword"] == "else":
					haxeVar = f"{info['keyword']} " + "{"
				else:
					haxeVar = f"{info['keyword']} ({info['expression']}) " + "{"
				line = line.replace(line.strip(), haxeVar)
				# nestedCode = code.getNestOfLine(lineNumber)
				# haxeVar += nestedCode + "\n}"
				addSemicolon = False
		elif line.strip():

			info = match.expInfo(line.strip())

			if info:
				if info["exp"] == "=":
					checkLine = lineNumber - 1
					found = False
					declareStr = f"var {info['name']}:Dynamic;"
					for i in range(code.amountOfLines() - checkLine):
						checkLine -= 1
						if checkLine == 0:
							break
						elif code.getParentOfNest(checkLine) and info['name'] in\
						code.getNestOfLine(code.getParentOfNest(checkLine).number, sameIndentationToo=True, cutoff=lineNumber):
							found = True
							break
						elif not code.getParentOfNest(checkLine):
							break

					# print(f"Val: {info['name']} found: {found}")

					if not found:
						haxeVar = f"var {info['name']}:Dynamic = {info['val']}"
						line = line.replace(line.strip(), haxeVar)
		if line != None and line.strip() and addSemicolon:
			line = util.addSemicolon(line)

		if originalLine != line:
			newValLines.append([lineNumber, line])

		lineNumber += 1

	a = 1
	print("Second pass")
	for line in code.getLines():
		print(f"{a}: {line.text}")
		a += 1

	code.setLines(newValLines)

	newValLines = []
	lineNumber = 1
	closeCurlyBraces = {"for", "if", "else if", "else"}
	for line in code.getLines():
		line = line.text

		originalLine = line
		strippedLine = line.strip()

		if util.quoteInsensitiveSearch(line.strip(), "if __name__ == \"__main__\":"):
			lineNumber += 1
			continue

		for closeKw in closeCurlyBraces:
			if strippedLine.startswith(closeKw):
				if closeKw == "else" and strippedLine[4:].strip().startswith("if"):
					continue
				closeLineNumber = code.getLastLineOfNest(lineNumber)
				if dict(newValLines).get(closeLineNumber, False):
					newValLines = dict(newValLines)
					closeLine = dict(newValLines).get(closeLineNumber)
					newValLines[closeLineNumber] = closeLine + "\n" + "\t" * (util.tabsOf(closeLine) - 1) + "}"
					newValLines = [[k,v] for k, v in newValLines.items()]
				else:
					closeLine = code.getLine(closeLineNumber).text
					newValLines.append([closeLineNumber, closeLine + "\n" + "\t" * (util.tabsOf(closeLine) - 1) + "}"])

		lineNumber += 1

	a = 1
	print("Third pass™")
	for line in code.getLines():
		print(f"{a}: {line.text}")
		a += 1

	code.setLines(newValLines)

	lineNumber = 1

	insertCode = ""

	for line in code.getLines():
		line = line.text
		if util.quoteInsensitiveSearch(line.strip(), "if __name__ == \"__main__\":"):
			nestedCode = code.getNestOfLine(lineNumber)
			nestedCode = nestedCode.split("\n")
			for index, line in enumerate(nestedCode):
				nestedCode[index] = "\t" + nestedCode[index]
			nestedCode = "\n".join(nestedCode)
			insertCode += typeconvert.getImports(code, newLineEnd=True)
			insertCode += """class """ + util.getHxFileNameFromPy(fileName, appendHx=False) + """ {
	static function main() {
""" + nestedCode + """
	}
}"""
		elif line.strip().startswith("def"):
			# print("Found def line: " + line.strip())
			pass
		lineNumber += 1

	a = 1
	print("Lastpass™")
	for line in code.getLines():
		print(f"{a}: {line.text}")
		a += 1

	# Process code to convert builtins from Python to Haxe
	processedCode = util.replaceBuiltins(insertCode)

	# Create the .hx file
	createHx(processedCode, hxFileName)

	print("Finished converting Python into Haxe")

	util.runHaxeCompiler(debug, fileName, args)

	# Give the user the path to the executable
	if not args.nocomp:
		print("Python converted to C++")
		callString = r"""cd ../intermediate/cpp
cp ./""" + util.getHxFileNameFromPy(fileName, appendHx=False)\
	             + ("-debug" if debug else "") +  " ../../"\
	             + util.getHxFileNameFromPy(fileName, appendHx=False)
		print("Copy commands: \n" + callString)
		subprocess.check_call(callString, shell=True)
		print("Moved file to location of original location of .py file.")
		if not args.norun:
			print("Now the program shall execute\n-----------------------------")
			callString = r"""cd ../intermediate/cpp
					./""" + util.getHxFileNameFromPy(fileName, appendHx=False) + ("-debug" if debug else "")
			print("starting with commands:\n" + callString)
			subprocess.check_call(callString, shell=True)

def createHx(contents, fileName):
	path = os.path.join(os.path.dirname(__file__), "../intermediate/")

	print("Name: " + fileName)
	print("Creating file in: " + path + ", with contents of: " + contents)

	if not os.path.exists(path):
		os.makedirs(path)

	with open(path + fileName, "w+") as createFile:
		createFile.write(contents)

if __name__ == "__main__":
	main()