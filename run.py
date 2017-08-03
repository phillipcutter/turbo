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
		print(abc)
		if i % 5 == 0 and i % 3 == 0:
			out = "fizzbuzz"
		elif i % 5 == 0:
			out = "fizz"
		elif i % 3 == 0:
			out = "buzz"
		else:
			out = i
		lst.append(out)
		print(out)

	abc = 345
	print(abc)

	print("ended")

def nesting():
	print("nesting")
	def second():
		print("Second")
	def second2():
		print("second2")