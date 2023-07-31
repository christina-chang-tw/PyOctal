from lib.sweeps.dc import DCSweeps
from lib.util.util import get_callable_funcs


sweep = DCSweeps(0)
docs = get_callable_funcs(sweep, "run")
print(docs)