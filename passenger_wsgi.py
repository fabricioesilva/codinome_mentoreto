import os
import sys


sys.path.insert(0, os.path.dirname(__file__))


import core.wsgi

application = core.wsgi.application
