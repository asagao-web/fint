
from OANDA_FUNC_CONF import *
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pickle
import random


class Trade:
    def __init__(self, arr):
        self.position = 0
        self.inPrice = 0
        self.timeAfterOrder = 0
        self.profit = 0
        self.arr = arr
        self.won = 0
        self.lost = 0
    def long(self,i,  ):
        if self.position == 0:
            self.inPrice = self.arr[i]
            self.position = 1
            self.timeAfterOrder = 0
            # print(">>> LONG")
        elif self.position == 1:
            pass
        elif self.position == -1:
            self.close(i)
    def short(self, i, ):
        if self.position == 0:
            self.inPrice = self.arr[i]
            self.position = -1
            self.timeAfterOrder = 0
            # print(">>> SHORT")
        elif self.position == 1:
            self.close(i)
        elif self.position == -1:
            pass  
    def close(self,i):
        if self.position > 0:
            profit = self.arr[i] - self.inPrice
        elif self.position < 0:
            profit = self.inPrice - self.arr[i]
        else:
            profit = None
        if profit != None:
            # print("profit: ", profit)
            pass
        else:
            print("WARNING >>>>> DID NOT HAVE ANY POSITION BUT CLOSING...")
        self.profit += profit
        self.position = 0  
        self.timeAfterOrder = 0
        # update win ratio
        if profit > 0:
            self.won += 1
        elif profit < 0:
            self.lost += 1
        # print("total profit: ", self.profit)

def bbSimulate(SPAN, LENGTH, optW): # SPAN is oanda granularity
	data = Data(SPAN, LENGTH)
	bb = data.bband(window=optW,)
	i = optW 
	t = Trade(bb["raw"].to_numpy() )
	inAbove = False
	inBelow = False
	# fromAbove = False
	# fromBelow = False

	while i < len(bb):
		row = bb.iloc[i]
		if row["raw"] > row["upper"]:
			if t.position == 1:
				t.short(i)
				# print(row["time"])
			if inAbove:
				pass
			else:
				inAbove = True
		elif row["raw"] < row["lower"]:
			if t.position == -1:
				t.long(i)
				# print(row["time"])
			if inBelow:
				pass
			else:
				inBelow = True
		else:
			if inAbove:
				t.short(i)
				inAbove = False
			elif inBelow:
				t.long(i)
				inBelow = False
			else:
				pass
		i += 1
		
	# print("************\n*************END") 
	return round(t.profit,2), round(t.won / (t.won + t.lost),2)

