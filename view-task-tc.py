from code_golf_utils import *
import matplotlib.pyplot as plt
from sys import argv
from os import makedirs

makedirs("./working/viewtc/", exist_ok=True)

if len(argv) < 2:
    task_num = int(input("task num > "))
else:
    task_num = int(argv[1])
if len(argv) < 3:
    tc_num = int(input("tc num > "))
else:
    tc_num = int(argv[2])
if os.path.isfile(f"./working/viewtc/task{task_num:03d}-{tc_num}.png"):
    print(f"./working/viewtc/task{task_num:03d}-{tc_num}.png", 'already there')
    exit(0)
show_legend()
examples = load_examples(task_num)
all_ex = examples['train'] + examples['test'] + examples["arc-gen"]
show_examples(all_ex[(tc_num-1) % len(all_ex):][:1])
plt.savefig(f"./working/viewtc/task{task_num:03d}-{tc_num}.png", dpi=600, bbox_inches='tight')
