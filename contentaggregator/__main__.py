"""_summary_#TODO
"""

import os
import subprocess

from contentaggregator.lib import config

config.SQL_USERNAME = os.environ['SQL_USERNAME']

config.SQL_HOST = os.environ['SQL_HOST']

config.SQL_PASSWORD = os.environ['SQL_PASSWORD']

config.DATABASE_NAME = os.environ['DATABASE_NAME']

config.RAPID_API_KEY = os.environ['RAPID_API_KEY']

config.EMAIL_SENDER_ADDRESS = os.environ['EMAIL_SENDER_ADDRESS']

config.EMAIL_SENDER_PWD = os.environ['EMAIL_SENDER_PWD']

if 'website' not in os.getcwd():
    current_file_path = os.path.realpath(__file__)
    os.chdir(os.path.join(current_file_path[:current_file_path.rfind('/')], 'website'))

subprocess.run('pc run', shell=True)
