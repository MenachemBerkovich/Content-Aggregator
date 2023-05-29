"""_summary_#TODO
"""

import os
import subprocess


if 'website' not in os.getcwd():
    current_file_path = os.path.realpath(__file__)
    os.chdir(os.path.join(current_file_path[:current_file_path.rfind('/')], 'website'))

subprocess.run('pc run', shell=True)