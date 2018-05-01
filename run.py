def params(param1):
	print("Param: " + str(param1))

def tab():
	print("Test func")

def spaces():
	print("Test spaces")

def old():
	print("Hello World")
	print("101111")
	print("Python->Haxe->C++->Binary")
	print("😀")

print("hi")

# ["8", "3.141"]

if __name__ == "__main__":
	print("starting")
	lst = []
	for i in range(1000000):
		abc = 123
		# print(abc)
		if i % 5 == 0 and i % 3 == 0:
			out = i * 8
		elif i % 5 == 0:
			out = i * 24
		elif i % 3 == 0:
			i = i / 3
		else:
			out = (i + 2) * 3
		lst.append(out)
		# print(out)
	for i in range(10):
		output2 = i

	print(output2)

	abc = 345
	print(abc)

	print("ended")

def nesting():
	print("nesting")
	def second():
		print("Second")
	def second2():
		print("second2")