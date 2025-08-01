from code_golf_utils import *

task_num = int(input("task num > "))
show_legend()
examples = load_examples(task_num)
show_examples(examples['train'] + examples['test'])
plt.show()
