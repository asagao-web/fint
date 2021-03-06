
# from typing import type_check_only
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
		self.binHistory = [] # only 1 win 0 lose
		self.weightedWinRatio = 0

	def calcWeightedWinRatio(self, arr, result):
		arr.append(result)
		def weightedAve(arr):
			w = np.linspace(0.1,1,len(arr))
			return (w * arr).sum() / len(arr) 
		self.weightedWinRatio = weightedAve(arr)


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
			self.calcWeightedWinRatio(self.binHistory, 1)
		elif profit < 0:
			self.lost += 1
			self.calcWeightedWinRatio(self.binHistory, 0)
		# print("total profit: ", self.profit)
		
	def currentProfit(self, currentPrice):
		currentProf = 0
		if self.position == 1:
			currentProf = currentPrice - self.inPrice
		elif self.position == -1:
			currentProf = self.inPrice - currentPrice
		# update win ratio
		if currentProf > 0:
			self.won += 1
			self.calcWeightedWinRatio(self.binHistory, 1)
		elif currentProf < 0:
			self.lost += 1
			self.calcWeightedWinRatio(self.binHistory, 0)
		return currentProf 


def bbSimulate(SPAN, LENGTH, optW): # SPAN is oanda granularity
	data = Data(SPAN, LENGTH)
	bb = data.bband(window=optW,)
	i = optW 
	t = Trade(bb["raw"].to_numpy() )
	inAbove = False
	inBelow = False
	# fromAbove = False
	# fromBelow = False
	lastTouch = 0

	while i < len(bb):
		row = bb.iloc[i]
		if row["raw"] > row["upper"]:
			lastTouch = "Above"
			if t.position == 1:
				t.short(i)
				# print(row["time"])
			if inAbove:
				pass
			else:
				inAbove = True
		elif row["raw"] < row["lower"]:
			lastTouch = "Below"
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
	

	# add unclosed situtation
	row = bb.iloc[-1]
	t.profit += t.currentProfit(row["raw"])

	# print("************\n*************END") 
	# return > profit, win ratio, weighted ratio, trend
	return round(t.profit,2), round(t.won / (t.won + t.lost),2), round(t.weightedWinRatio, 2), lastTouch



if __name__ == "__main__":
	print(bbSimulate("H1", 2500, 170))