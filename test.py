
import sys
from lib.util.util import Tee

f = open('logfile.log', 'w')
backup = sys.stdout
sys.stdout = Tee(sys.stdout, f)

print("hello world")  # this should appear in stdout and in file