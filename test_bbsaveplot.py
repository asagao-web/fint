
import numpy as np
from OandaTrade import OandaTrade
import datetime
import time
from mod_bb import Trade, bbSimulate
from OANDA_FUNC_CONF import Data
import matplotlib.pyplot as plt


o = OandaTrade("USD_JPY", "S30", "1000", live=True) # any pram ok for bb version

dd = Data("H1", 5000)
bb = dd.bband(200,)
fig = bb[["raw","upper","lower"]].plot(figsize=(16, 4), grid=True).get_figure()
fig.savefig("{}.png".format(o.instrument))			
o.line_important("test for image")