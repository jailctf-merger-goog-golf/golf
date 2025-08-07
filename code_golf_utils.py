# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing utilities for the 2025 Google Code Golf Championship."""

import copy
import importlib.util
import json
import os
import sys

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams['text.antialiased'] = False
os.makedirs("working", exist_ok=True)

code_golf_dir = "./infos/"
libraries = ["collections", "itertools", "math", "operator", "re", "string",
             "struct"]
colors = [
    (0, 0, 0),
    (30, 147, 255),
    (250, 61, 49),
    (78, 204, 48),
    (255, 221, 0),
    (153, 153, 153),
    (229, 59, 163),
    (255, 133, 28),
    (136, 216, 241),
    (147, 17, 49),
]
task_zero = {
    "train": [{
        "input": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        ],
        "output": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 5, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 0, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 0, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 0, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 0, 5, 5],
            [5, 1, 1, 1, 1, 1, 1, 0, 5, 5],
            [5, 5, 0, 0, 0, 0, 0, 0, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        ],
    }],
    "test": [{
        "input": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 4, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 4, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 5, 5, 5],
            [5, 5, 4, 5, 5, 5, 4, 5, 5, 5],
            [5, 5, 4, 5, 5, 5, 4, 5, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        ],
        "output": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 4, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 4, 0, 5],
            [5, 5, 5, 0, 0, 0, 0, 0, 0, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 5, 5, 5],
            [5, 5, 4, 0, 0, 0, 4, 0, 5, 5],
            [5, 5, 4, 0, 5, 5, 4, 0, 5, 5],
            [5, 5, 4, 4, 4, 4, 4, 0, 5, 5],
            [5, 5, 5, 0, 0, 0, 0, 0, 5, 5],
        ],
    }],
    "arc-gen": [{
        "input": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 2, 2, 2, 2, 2, 2, 5, 5],
            [5, 5, 2, 5, 5, 5, 5, 2, 5, 5],
            [5, 5, 2, 5, 5, 5, 5, 2, 5, 5],
            [5, 5, 2, 5, 5, 5, 5, 2, 5, 5],
            [5, 5, 2, 5, 5, 5, 5, 2, 5, 5],
            [5, 5, 2, 2, 2, 2, 2, 2, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        ],
        "output": [
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [5, 5, 2, 2, 2, 2, 2, 2, 5, 5],
            [5, 5, 2, 0, 0, 0, 0, 2, 0, 5],
            [5, 5, 2, 0, 5, 5, 5, 2, 0, 5],
            [5, 5, 2, 0, 5, 5, 5, 2, 0, 5],
            [5, 5, 2, 0, 5, 5, 5, 2, 0, 5],
            [5, 5, 2, 2, 2, 2, 2, 2, 0, 5],
            [5, 5, 5, 0, 0, 0, 0, 0, 0, 5],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        ],
    }],
}


def load_examples(task_num):
    """Loads relevant data from ARC-AGI and ARC-GEN."""
    if not task_num:
        return task_zero
    with open(code_golf_dir + f"task{task_num:03d}.json") as f:
        examples = json.load(f)
    return examples


def show_legend():
    image = [[(255, 255, 255) for _ in range(10)] for _ in range(1)]
    for idx, color in enumerate(colors):
        image[0][idx] = color
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_axes([0, 0, 1, 1])
    for idx, _ in enumerate(colors):
        color = "white" if idx in [0, 9] else "black"
        ax.text(idx - 0.1, .1, str(idx), color=color, size=22)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(np.array(image))

    fig.savefig('./legend.png', dpi=300, bbox_inches='tight', pad_inches=0)


def show_examples(examples, bgcolor=(255, 255, 255), name=""):
    # Determine the dimensions of the image to be rendered.
    width, height, offset = 0, 0, 1
    for example in examples:
        grid, output = example["input"], example["output"]
        if not isinstance(output, list):
            raise NotImplementedError("result not 2d list: " + str(output))
        if not isinstance(output[0], list):
            raise NotImplementedError("result not 2d list: " + str(output))
        if len(output[0])==0:
            raise NotImplementedError("result is [[]] which is not ok")
        width += len(grid[0]) + 1 + len(output[0]) + 6
        height = max(height, max(len(grid), len(output)) + 4)
    # Determine the contents of the image.
    image = [[bgcolor for _ in range(width)] for _ in range(height+1)]
    for example in examples:
        grid, output = example["input"], example["output"]
        grid_width, output_width = len(grid[0]), len(output[0])
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                try:
                    image[r + 3][offset + c + 1] = colors[cell]
                except (IndexError, TypeError) as e:
                    raise NotImplementedError("bad color:" + repr(cell))
        offset += grid_width + 3
        for r, row in enumerate(output):
            for c, cell in enumerate(row):
                if isinstance(cell, list):
                    raise NotImplementedError("result not 2d list: " + str(output))
                try:
                    image[r + 3][offset + c + 1] = colors[cell]
                except (IndexError, TypeError) as e:
                    raise NotImplementedError("bad color:" + repr(cell))
        offset += output_width + 4
    # Draw the image.
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(np.array(image))
    # Draw the horizontal and vertical lines.
    offset = 1
    fs=min([max(1.3, 20 / ((len(example['input'][0])+len(example['output'][0])) ** 0.6)) for example in examples])
    for example in examples:
        grid, output = example["input"], example["output"]
        grid_width, grid_height = len(grid[0]), len(grid)
        output_width, output_height = len(output[0]), len(output)
        grid_cell_size = min(grid_width+output_width, grid_height+output_height)
        lw=1.3/(grid_cell_size ** 0.5)
        # input
        ax.hlines([r + 2.5 for r in range(grid_height + 1)],
                  xmin=offset - 0.5, xmax=offset + grid_width + 0.5, linewidth=lw, color="black")
        ax.vlines([offset + c + 0.5 for c in range(grid_width + 1)], linewidth=lw,
                  ymin=1.5, ymax=grid_height + 2.5, color="black")
        for x in range(grid_width):
            ax.text(x + 0.69 + offset, 2.37, str(x % 10), color=(0, 0, 0), size=fs)
            if x > 9:
                ax.text(x + 0.69 + offset, 1.37, str(x // 10), color=(0, 0, 0), size=fs)
        for y in range(grid_height):
            ax.text(offset - 0.3 + [0,-0.4][y>9], y + 3.37, str(y), color=(0, 0, 0), size=fs)
        offset += grid_width + 3

        # output
        ax.hlines([r + 2.5 for r in range(output_height + 1)],
                  xmin=offset - 0.5, xmax=offset + output_width + 0.5, linewidth=lw, color="black")
        ax.vlines([offset + c + 0.5 for c in range(output_width + 1)], linewidth=lw,
                  ymin=1.5, ymax=output_height + 2.5, color="black")
        for x in range(output_width):
            ax.text(x + 0.69 + offset, 2.37, str(x % 10), color=(0, 0, 0), size=fs)
            if x > 9:
                ax.text(x + 0.69 + offset, 1.37, str(x // 10), color=(0, 0, 0), size=fs)
        for y in range(output_height):
            ax.text(offset - 0.3 + [0,-0.4][y>9], y + 3.37, str(y), color=(0, 0, 0), size=fs)
        offset += output_width + 2

        # barrier
        ax.vlines([offset + 0.5], ymin=-0.5, ymax=height + 0.5, color="black")
        offset += 2
    ax.set_xticks([])
    ax.set_yticks([])
    if len(name) != 0:
        plt.savefig(f'./working/{name}', dpi=600, bbox_inches='tight')


def verify_program(task_num, examples):
    task_name, task_path = f"task_with_imports{task_num:03d}", f"./sols/task{task_num:03d}.py"
    module_path = f"./working/task_with_imports/task_with_imports{task_num:03d}.py"
    with open(task_path, "rb") as file:
        file_content = file.read()
        # if "import" in file_content:
        #     print("Error: Imports are not permitted")
        #     return
    with open(module_path, "wb") as file:
        # for library in libraries:
        #     file.write(f"from {library} import *\n")
        file.write(file_content)
    spec = importlib.util.spec_from_file_location(task_name, module_path)
    if spec is None:
        print("Error: Unable to import task.py.")
        return
    module = sys.modules[task_name] = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "p"):
        print("Error: Unable to locate function p() in task.py.")
        return
    program = getattr(module, "p")
    if not callable(program):
        print("Error: Function p() in task.py is not callable.")
        return
    print()
    has_printed_first_err = False

    def verify(example_subset):
        nonlocal has_printed_first_err
        right, wrong, expected, index = 0, 0, None, -1
        for index, example in example_subset:
            example_copy = copy.deepcopy(example)
            try:
                if program(example_copy["input"]) == example_copy["output"]:
                    right += 1
                else:
                    expected = copy.deepcopy(example)
                    wrong += 1
            except Exception as e:
                if not has_printed_first_err:
                    import traceback
                    print("ERROR:")
                    traceback.print_exc(file=sys.stdout)
                has_printed_first_err = True
                wrong += 1
        return right, wrong, expected, index

    train_test_examples = []
    i=0
    for ex in examples["train"] + examples["test"]:
        train_test_examples.append((i, ex))
        i += 1
    gen_examples = []
    for ex in examples["arc-gen"]:
        gen_examples.append((i, ex))
        i += 1
    arc_agi_right, arc_agi_wrong, arc_agi_expected, agi_index = verify(train_test_examples)
    arc_gen_right, arc_gen_wrong, arc_gen_expected, gen_index = verify(gen_examples)
    print(f"Results on ARC-AGI exaples: {arc_agi_right} pass, {arc_agi_wrong} fail")
    print(f"Results on ARC-GEN exaples: {arc_gen_right} pass, {arc_gen_wrong} fail")
    print()
    if arc_agi_wrong + arc_gen_wrong == 0:
        task_length = os.path.getsize(task_path)
        print("Your code IS READY for submission!")
        print("Its length appears to be " + str(task_length) + " bytes.")
    else:
        print("Your code IS NOT ready for submission.")
        expected = arc_agi_expected if arc_agi_expected else arc_gen_expected
        index = max(agi_index, gen_index)
        print(f"Your code failed on test case #{index+1}")
        if not expected:
            from PIL import Image, ImageDraw

            img = Image.new('RGB', (100, 30), color=(73, 109, 137))

            d = ImageDraw.Draw(img)
            d.text((10,10), "ERROR!", fill=(255,255,0))

            img.save(f'./working/expected/{task_num:03d}.png')
            img.save(f'./working/actual/{task_num:03d}.png')
            return
        actual = {"input": expected["input"], "output": program(copy.deepcopy(expected["input"]))}
        print("The expected result is shown in green; your actual result is shown in red.")
        show_examples([expected], bgcolor=(200, 255, 200), name=f'expected/{task_num:03d}.png')
        show_examples([actual], bgcolor=(255, 200, 200), name=f'actual/{task_num:03d}.png')
