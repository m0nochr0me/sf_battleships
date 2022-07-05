"""Utility functions"""

import sys
import os

# Return cls() function according to user system
if os.getenv('TERM'):
    if sys.platform == 'linux':
        def cls():
            os.system('clear')
    else:
        def cls():
            os.system('cls')
else:
    def cls():
        print('\n' * 100)  # PyCharm
