from dotenv import load_dotenv

load_dotenv()

import sys

import os

INTERP = os.path.expanduser(os.environ.get("INTERP_PATH"))
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from src.main import application
