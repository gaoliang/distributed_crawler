__version__ = "0.2"

try:
  import pathlib
  import configparser
  import xmlrpc
  import futures
except:
  import os
  os.system('pip install pathlib')
  os.system('pip install configparser')
  os.system('pip install xmlrpc')
  os.system('pip install futures')


