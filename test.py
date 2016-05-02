from os import listdir
from os.path import *

xml_files = [join('results/', f) for f in listdir('results/') if isfile(join('results/', f))]
print xml_files