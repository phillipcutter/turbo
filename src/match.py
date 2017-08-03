# This file is designed to aid the compiler in matching syntax so it knows what it's dealing with
import re

expInfoPatt = re.compile(r"([A-Za-z0-9_]+)\s*([=+\*/\-]|\+=)\s*(\".+\"|[0-9._\[\]]+|[A-Za-z0-9_]+)")

def expInfo(string):
	if not bool(expInfoPatt.match(string)):
		return False
	else:
		search = expInfoPatt.search(string)

		info = {}

		if not search:
			return False
		else:
			info["name"] = search.group(1)
			info["exp"] = search.group(2)
			info["val"] = search.group(3)

		return info