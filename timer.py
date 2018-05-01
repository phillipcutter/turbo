# This is not a test file or file necessary for compilation, it just helps you time the difference of Python vs Turbo
# Todo - Add support for infinite file measuring
import argparse
import subprocess
import timeit
import os
from tqdm import tqdm

parser = argparse.ArgumentParser(description='time how long it takes to execute two different commands with accuracy')
parser.add_argument('files', metavar='files', type=str,
                    help='files to test', nargs="*")
parser.add_argument("iters", metavar='iters', type=int,
                    help='how many times to run each file')
parser.add_argument("-o", "--showoutput", action='store_true',
                    help='show output when testing files and base test')
args = parser.parse_args()

files = args.files
iters = args.iters
showOutput = args.showoutput

def call(command, **kwargs):
	# cwd = os.getcwd()
	# cwd = cwd.replace(' ','\ ')
	#
	# command = "cd \"" + os.getcwd() + "\"\n"
	return subprocess.check_call(command, shell=True, **kwargs)

# Try typing 'time echo' in a shell, it says it doesn't take any time so we'll use that as a base
# Below gets how long it takes to start a subprocess in python, this is so results are more accurate
baseTimes = []
for i in range(30):
	if showOutput:
		start = timeit.default_timer()
		call("echo")
		elapsed = timeit.default_timer() - start
	else:
		FNULL = open(os.devnull, 'w')
		start = timeit.default_timer()
		call("echo", stdout=FNULL, stderr=subprocess.STDOUT)
		elapsed = timeit.default_timer() - start
	baseTimes.append(elapsed)

baseAvg = sum(baseTimes)/len(baseTimes)
cmds = {}
i = 1
for file in files:
	cmds["File " + str(i)] = file
	i += 1
# cmds = {"File One": file1, "File Two": file2}
avgTimes = {}
individualTimes = {}
for name, cmd in tqdm(cmds.items()):
	times = []
	for i in tqdm(range(iters)):
		if showOutput:
			start = timeit.default_timer()
			call(cmd)
			elapsed = timeit.default_timer() - start
		else:
			FNULL = open(os.devnull, 'w')
			start = timeit.default_timer()
			call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)
			elapsed = timeit.default_timer() - start
		times.append(elapsed - baseAvg)
	individualTimes[cmd] = times
	avgTimes[cmd] = sum(times)/len(times)

results = ""
for name, avgTime in avgTimes.items():
	results += f"\"{name}\" Avg Time: {avgTime}\n"
if results.endswith("\n"):
	results = results[:-1]
print(f"""

{iters} Iterations Completed

{results}""")
