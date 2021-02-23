"""
The flask application package.
"""
# pylint: disable=wrong-import-position, cyclic-import
import sys
from flask import Flask
app = Flask(__name__)

import iot_statistics.views

if __file__.rfind('\\') < 0:
    DELIMITER = '/'
else:
    DELIMITER = '\\'

current_dir = __file__[:__file__.rfind(DELIMITER) - len(__file__)]
if current_dir not in sys.path:
    sys.path.append(current_dir)
model_dir = f"{current_dir}{DELIMITER}model"
if model_dir not in sys.path:
    sys.path.append(model_dir)
view_dir = f"{current_dir}{DELIMITER}view"
if view_dir not in sys.path:
    sys.path.append(view_dir)
