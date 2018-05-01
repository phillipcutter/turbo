def CodeNestingTest():
	import util

	lines = """if __name__ == "__main__": 
		print("starting")
		lst = []
		for i in range(1000000):
			if i % 5 == 0 and i % 3 == 0:
				print("fizzbuzz")
			elif i % 5 == 0:
				print("fizz")
			elif i % 3 == 0:
				print("buzz")
			else:
				print(i)
		print("ending")""".split("\n") # 13

	code = util.Code(lines)

	assert code.getLastLineOfNest(4) == 12
	assert code.getLastLineOfNest(1) == 13
	assert not code.getLastLineOfNest(13) == 1

	lines = """if __name__ == "__main__": 
			print("starting")
			lst = []
			for i in range(1000000):
				if i % 5 == 0 and i % 3 == 0:
					print("fizzbuzz")
				elif i % 5 == 0:
					if True:
						print("test")
					print("fizz")
				elif i % 3 == 0:
					print("buzz")
				else:
					print(i)
			print("ending")""".split("\n")  # 15

	code = util.Code(lines)

	assert code.getParentNestFirstLineLineNumber(9) == 4
	assert code.getParentNestFirstLineLineNumber(8) == 4
	pass

def UtilVarReplaceTest():
	import typeconvert

	string, replaceOld, replaceNew = 'a = "abcdefg" + abc - a + a - a + "a"', "a", "A"
	assert typeconvert.replaceVar(string, replaceOld, replaceNew) == 'A = "abcdefg" + abc - A + A - A + "a"'
	string, replaceOld, replaceNew = "\t\tprint(abc)", "abc", "abc__1__turbo_var__"
	assert typeconvert.replaceVar(string, replaceOld, replaceNew) == '\t\tprint(abc__1__turbo_var__)'

def GetImportsTest():
	import util
	import typeconvert

	lines = """if __name__ == "__main__": 
				print("starting")
				lst = []
				for i in range(1000000):
					if i % 5 == 0 and i % 3 == 0:
						print("fizzbuzz")
					elif i % 5 == 0:
						if True:
							print("test")
						print("fizz")
					elif i % 3 == 0:
						print("buzz")
					else:
						print(i)
				print("ending")""".split("\n")  # 15

	code = util.Code(lines)

	assert typeconvert.getImports(code) == "import Sys.print;"


def ASTRunnerTest():
	import util

	print(util)

CodeNestingTest()

UtilVarReplaceTest()

GetImportsTest()

ASTRunnerTest()