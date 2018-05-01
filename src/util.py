import base64
import json
import math
import time
import os
import subprocess
import warnings

import pickle

import dill
from plyplus import plyplus, grammars
from plyplus.strees import STree


def quoteInsensitiveSearch(string, filter):
	filter = filter.replace("'", "\"")
	if filter in string:
		return True
	else:
		filter = filter.replace("\"", "'")
		if filter in string:
			return True
		else:
			return False

def consecutiveSubstrInStr(string, substr):
	"""Returns how many of substr are in string at the beginning"""
	checkLen = len(substr)
	count = 0
	for i in range(math.ceil(len(string)/checkLen)):
		pos = i * checkLen
		if string[pos:].startswith(substr):
			count += 1
	return count



class Code():
	def __init__(self, lines):
		lineObjs = []
		for i in range(len(lines)):
			lineObjs.append(Line(lines[i], i + 1))
		self.lines = [None] + lineObjs  # This is so line 0 is None and line 1 is the same line as in the file
		self.varIncrementer = 0

	def setLine(self, lineNumber, new):
		newObj = Line(new, lineNumber)
		if new == None:
			self.lines.pop(lineNumber)
		elif lineNumber > self.amountOfLines():
			self.lines.append(newObj)
		else:
			self.lines[lineNumber] = newObj

	def setLines(self, newLines):
		"""Sets all values and then overrides self's, that way indexes aren't misaligned."""

		lines = self.lines

		# processedLines = []

		# # First pass -- If a new line has two lines ("hi\nhello") in one, this will split them back up
		# for arr in newLines:
		# 	lineNumber = arr[0]
		# 	new = arr[1]
		# 	while lineNumber in [lineNum for lineNum, lineStr in processedLines]:
		# 		lineNumber += 1
		#
		# 	if new and len(new.split("\n")) > 1:
		# 		splitNew = new.split("\n")
		# 		newLineNumber = lineNumber
		# 		for newLine in splitNew:
		# 			processedLines.append([newLineNumber, newLine, "spliced"])
		# 			newLineNumber += 1
		# 	else:
		# 		processedLines.append([lineNumber, new, "normal"])


		# First pass -- actually loads the changes into the lists object
		for arr in newLines:
			lineNumber = arr[0]
			new = arr[1]

			newObj = Line(new, lineNumber)

			if new == None:
				lines[lineNumber] = None
			elif lineNumber >= len(lines):
				lines.append(newObj)
			else:
				lines[lineNumber] = newObj

		lines = [line for line in lines if line != None]

		# Second pass -- splits up elements in the lists object that have more than one line("\n") in one element
		for line in lines:
			lineNumber = line.number
			lineText = line.text
			index = lines.index(line)

			if lineText and len(lineText.split("\n")) > 1:
				splitNew = lineText.split("\n")
				newLineNumber = lineNumber
				lines.pop(index) # Remove combined string, as it will be re-added
				iteration = 0
				for newLine in splitNew:
					newObj = Line(newLine, newLineNumber)
					lines.insert(index + iteration, newObj)
					newLineNumber += 1
					iteration += 1

		self.lines = lines

	def getLine(self, lineNumber):
		return self.lines[lineNumber]

	def getLines(self):
		return self.lines[1:] # Don't return the 0th element, because it's None. Look in __init__

	def amountOfLines(self):
		return len(self.getLines())

	def getParentOfNest(self, lineNumber):
		"""Gets the direct parent of a line of a code"""
		if lineNumber == 1:
			return ""

		beginningLine = self.getLine(lineNumber).text
		tabsAtStart = consecutiveSubstrInStr(beginningLine, "\t")

		returnContents = None

		checkLine = lineNumber - 1

		for i in range(lineNumber):
			if i == 0:
				continue
			checkLine = lineNumber - i
			if consecutiveSubstrInStr(self.getLine(checkLine).text, "\t") < tabsAtStart:
				returnContents = self.getLine(checkLine)
				break
			if checkLine == 1:
				break

		return returnContents

	def getNestOfLine(self, lineNumber, lastLineNumberReturn=False,
	                  sameIndentationToo=False, lineNumDict=False, cutoff=None):

		if lineNumber == self.amountOfLines():
			return "" # The given line is the last line

		beginningLine = self.getLine(lineNumber).text
		tabsAtStart = consecutiveSubstrInStr(beginningLine, "\t")

		if lineNumDict:
			returnContents = {}
		else:
			returnContents = ""

		checkLine = lineNumber + 1
		if cutoff and checkLine >= cutoff:
			return returnContents
		if sameIndentationToo:
			for i in range(self.amountOfLines() - lineNumber):
				if not self.getLine(checkLine).text.strip() and not lastLineNumberReturn:
					checkLine += 1
					continue
				if not consecutiveSubstrInStr(self.getLine(checkLine).text, "\t") >= tabsAtStart:
					break

				if cutoff and checkLine >= cutoff:
					break

				if lineNumDict:
					returnContents[checkLine] = self.getLine(checkLine).text
				else:
					returnContents += self.getLine(checkLine).text + "\n"
				if checkLine == self.amountOfLines():
					checkLine += 1
					break
				checkLine += 1
		else:
			for i in range(self.amountOfLines() - lineNumber):
				if not self.getLine(checkLine).text.strip():
					checkLine += 1
					continue
				if not consecutiveSubstrInStr(self.getLine(checkLine).text, "\t") > tabsAtStart:
					break

				if cutoff and checkLine >= cutoff:
					break

				if lineNumDict:
					returnContents[checkLine] = self.getLine(checkLine).text
				else:
					returnContents += self.getLine(checkLine).text + "\n"
				if checkLine == self.amountOfLines():
					checkLine += 1
					break
				checkLine += 1

		if not lineNumDict and returnContents.endswith("\n"):
			returnContents = returnContents[:-1]

		if lastLineNumberReturn:
			return checkLine - 1
		else:
			return returnContents

	def isFirstLineOfNest(self, lineNumber):
		beginningLine = self.getLine(lineNumber).text
		tabsAtStart = consecutiveSubstrInStr(beginningLine, "\t")

		checkLine = lineNumber - 1
		if checkLine <= 0:
			return True
		else:
			return consecutiveSubstrInStr(self.getLine(checkLine).text, "\t") > tabsAtStart


	def isLastLineOfNest(self, lineNumber):
		beginningLine = self.getLine(lineNumber).text
		tabsAtStart = consecutiveSubstrInStr(beginningLine, "\t")

		checkLine = lineNumber + 1
		if checkLine >= self.amountOfLines():
			return True
		else:
			return consecutiveSubstrInStr(self.getLine(checkLine).text, "\t") < tabsAtStart

	def getLastLineOfNest(self, lineNumber):
		return self.getNestOfLine(lineNumber, lastLineNumberReturn=True)

	def getVarName(self, string):
		string += "__" + str(self.varIncrementer) + "__turbo_var__"
		self.varIncrementer += 1
		return string

	def getParentNestFirstLineLineNumber(self, lineNumber):
		checkLine = lineNumber - 1
		if checkLine == 0:
			warnings.warn("Why the heck do you think the parent of the first line is an if statement!? returning None")
			return None
		elif not self.getParentOfNest(checkLine):
			return 1
		while self.getParentOfNest(checkLine).text.strip().startswith(("if", "else", "elif", "for", "while")):
			if checkLine == self.amountOfLines() or \
					self.getParentOfNest(checkLine).text.strip().replace(" ", "")\
					.startswith("if__name__==\"__main__\""):
				break
			elif not self.getParentOfNest(checkLine - 1):
				return 1
			checkLine -= 1

		return checkLine

	def __str__(self):
		lines = [line.text for line in self.getLines()]
		returnStr = ""
		ln = 1
		for line in lines:
			returnStr += str(ln) + ": " + line + "\n"
			ln += 1
		if returnStr.endswith("\n"):
			returnStr = returnStr[:-2]
		return returnStr

# Python: Haxe
builtinConversions = {
	"print": "println",
	"append": "push"
}

def replaceBuiltins(code):
	for pyBuiltin, hxBuiltin in builtinConversions.items():
		code = code.replace(pyBuiltin, hxBuiltin)
	return code

def addSemicolon(line, dontAddIfAlreadHas=True):
	if dontAddIfAlreadHas and line.endswith(";"):
		return line
	else:
		return line + ";"

def addSemicolons(code, dontAddIfAlreadHas=True):
	"""Adds semicolons to at the end of each line"""
	code = code.split("\n")

	code = [line + ";" if (dontAddIfAlreadHas and not line.endswith(";")) else "" for line in code]

	code = "\n".join(code)

	return code

def getHxFileNameFromPy(fileName, appendHx=True):
	if appendHx:
		return fileName.replace(".py", "").title() + ".hx"
	else:
		return fileName.replace(".py", "").title()

def runHaxeCompiler(debug, fileName, args):
	# Get Haxe to convert .hx to C++
	if not args.nocomp:
		flags = []
		if debug:
			flags.append("-debug")
		# if not args.trace:
		# 	flags.append("--no-traces")
		print("Converting to C++")
		callString = r"""cd ../intermediate
		haxe -cpp cpp -main """ + getHxFileNameFromPy(fileName, appendHx=False) + " " + " ".join(flags)

		if debug:
			subprocess.check_call(callString, shell=True)
		else:
			FNULL = open(os.devnull, 'w')
			try:
				subprocess.check_call(callString, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
			except subprocess.CalledProcessError as err:
				print("Looks like an error occured, to learn more try running with the -d flag for debug output.")
				time.sleep(0.25) # This is so the print statement isn't jumbled with the error
				raise err

def tabsOf(string):
	return consecutiveSubstrInStr(string, "\t")

class Line():
	def __init__(self, text, number, flags=None):
		if flags is None:
			flags = {}
		self._text = text
		self._number = number
		self._flags = flags # Flags should allow comments or hidden attributes on lines during compile time

	@property
	def flags(self):
		return self._flags

	@flags.setter
	def flags(self, flags):
		self._flags = flags

	@property
	def text(self):
		return self._text

	@text.setter
	def text(self, text):
		self._text = text

	@property
	def number(self):
		return self._number

	@number.setter
	def number(self, number):
		self._number = number

	def __str__(self):
		return f"Line Obj: {self.text}"

def updateOrAddToList(lst, index, newVal, forceInsert=False):
	if forceInsert or index >= len(lst):
		lst.insert(index, newVal)
	else:
		lst[index] = newVal
	return lst

def getGrammar():
	with open("grammar.tmp", "ab+") as file:
		file.seek(0)
		contents = file.read()
		file.seek(0)
		if not contents:
			# Regenerate grammar file:
			grammar = plyplus.Grammar(grammars.open('python.g'))
			dill.dump(grammar, file)
		else:
			# Access grammar file
			grammar = dill.load(file)
	return grammar

def tailsOfTree(tree):
	tokInfo = {}
	for subTree in tree.tail:
		if isinstance(subTree, STree) and len(subTree.tail) > 1:
			tokInfo.update(tailsOfTree(subTree))
		else:
			tokInfo[subTree.head] = subTree.tail

	print(tokInfo)
	return tokInfo