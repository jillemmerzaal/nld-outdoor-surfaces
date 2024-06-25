from support_functions.grab import grab
from support_functions.engine import engine


def nld_analysis(fld):
    fl = engine(path=fld, extension=".zoo")

    for f in fld:
        data = grab(f)
