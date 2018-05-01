arr = []
for i in range(10000):
	arr.append(i)
print(len(arr))
print(sum(arr))


def F(n):
	if n == 0:
		return 0
	elif n == 1:
		return 1
	else:
		return F(n-1)+F(n-2)

print(F(32))
