import matplotlib.pyplot as plt

from code_golf_utils import *
from sys import argv

if len(argv) == 1:
    task_num = int(input("task num > "))
else:
    task_num = int(argv[1])
show_legend()
examples = load_examples(task_num)
show_examples(examples['train'] + examples['test'])
plt.savefig(f"./working/view/task{task_num:03d}.png", dpi=600, bbox_inches='tight')
