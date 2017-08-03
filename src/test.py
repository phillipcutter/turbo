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

	assert code.getParentNestFirstLineNotIfLineNumber(9) == 7
	assert code.getParentNestFirstLineNotIfLineNumber(8) == 7
	pass
CodeNestingTest()