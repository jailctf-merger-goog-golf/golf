from code_golf_utils import *
import matplotlib.pyplot as plt

from sys import argv

if len(argv) == 1:
    task_num = int(input("task num > "))
else:
    task_num = int(argv[1])
if os.path.isfile(f"./working/view/task{task_num:03d}.png"):
    print(f"./working/view/task{task_num:03d}.png", 'already there')
    exit(0)
show_legend()
examples = load_examples(task_num)
show_examples(examples['train'] + examples['test'])
plt.savefig(f"./working/view/task{task_num:03d}.png", dpi=600, bbox_inches='tight')
