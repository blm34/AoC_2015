import time
import sys

import aoc_helper

START_TIME = time.time()

p1 = 0
p2 = 0

input_text = aoc_helper.read_input(sys.argv[1])
L = input_text.split('\n')
G = [list(line) for line in L]
R = len(G)
C = len(G[0])



END_TIME = time.time()
RUN_TIME = END_TIME - START_TIME
print(f'Part 1: {p1}')
print(f'Part 2: {p2}')
print(f'Run time: {1000*RUN_TIME:.3f} ms')
