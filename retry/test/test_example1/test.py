#!/usr/bin/env python
'''
This example demonstrates a simple use of pycallgraph.
'''
import numpy as np

import subprocess

# x = 0

# class Banana:
    
#     def eat(self):
#         pass

def print_Hello():
    print("Hello")

def list_files():
    """
    Uses subprocess to list files in the current directory and captures the output.
    """
    try:
        # Run the 'ls' command (use 'dir' for Windows)
        result = subprocess.run(
            ["ls"],  # Replace "ls" with "dir" if you're on Windows
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,  # Capture standard error
            text=True                # Decode the output as a string
        )
        
        # Check if the command ran successfully
        if result.returncode == 0:
            print("Files in the current directory:")
            print(result.stdout)
        else:
            print("An error occurred:")
            print(result.stderr)
    except FileNotFoundError:
        print("The command 'ls' is not found. Are you using the correct system command?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# class Person(Banana):

#     def __init__(self):
#         super().__init__()
#         self.no_bananas()
#         self.name = 'james'
#         self.gender = "male"

#     def no_bananas(self):
#         self.bananas = []

#     def add_banana(self, banana):
#         x = np.arange(15, dtype=np.int64).reshape(3, 5)
#         self.bananas.append(banana)
#         self.no_bananas()
#         return 0

#     def eat_bananas(self):
#         raise KeyError


# if __name__ == "main":
#     p1 = Person()
#     b1 = Banana()
#     x = p1.add_banana(b1)