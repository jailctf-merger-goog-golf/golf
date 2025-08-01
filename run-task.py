import matplotlib.pyplot as plt

from code_golf_utils import *
from sys import argv

if len(argv) == 1:
    task_num = int(input("task num > "))
else:
    task_num = int(argv[1])
examples = load_examples(task_num)
verify_program(task_num, examples)
