from re import I
from OANDA_FUNC_CONF import *
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pickle
import random
from pathlib import Path


class OandaTrade:
	def __init__(self, instrument, span, count, live=True):
		if live:
			self.accountID = '001-011-4552395-001'
			access_token = 'd0d8f6874507f43902f7f30de35b7464-c5d19825c0a11a8e211d9b7f6fa0eb86'
			self.api = API(access_token=access_token, environment = "live")
		else:
			self.accountID = '101-011-15612193-001'
			access_token = '2897d1ae787989d30996a8a9d0a2c03d-7304ab578b56ccb454d311ecbc90cfdb'
			self.api = API(access_token=access_token, environment="practice")
		
		# init param 
		self.instrument = instrument
		self.span = span
		self.count = count
		self.dataPath = "tradestate_{}.pkl".format(instrument)
		# /init param	
		

		# status param
		self.stateDict = {}
		self.stateDict["position"] = 0
		self.stateDict["inPrice"] = 0
		self.stateDict["profit"] = 0
		# for bb
		self.stateDict["inAbove"] = False
		self.stateDict["inBelow"] = False
		# /for bb
		self.arr = np.zeros(int(self.count))
		# status param
		# load last state
		self.loadState()
		

	def convertFtime(self, strf):
		fmt = "%Y-%m-%dT%H:%M:%S.000000000Z"
		ptime = datetime.strptime(strf, fmt)
		ptime = ptime.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=+7)))
		return ptime

	def getprice(self):
		# instrument:USD_JPY, span:S30, count:5000
		params = {
        "alignmentTimezone": "Japan",
		"count": self.count,
		"granularity": self.span
		}
		r = instruments.InstrumentsCandles(instrument=self.instrument, params=params)
		res = self.api.request(r)
		y = []
		t = []
		for n, can in enumerate(res['candles']):
			cvalue = float(res['candles'][n]['mid']['c'])
			y.append(cvalue)
			t.append(res['candles'][n]['time'])
		t = list(map(self.convertFtime, t))
		return t, y

	def getpricenow(self):
		params = {
		"count": 1,
		"granularity": "S5"
		}
		r = instruments.InstrumentsCandles(instrument=self.instrument, params=params)
		res = self.api.request(r)
		pricenow = res['candles'][0]['mid']['c']                               #CからLへ
		return pricenow

	def check_status(self):
		r = positions.OpenPositions(accountID=self.accountID)
		res = self.api.request(r)
		return res
	def has_position(self, r_check_status):
		return len(r_check_status['positions'])

	def line(self, text,):
		text = '"'+text+'"'
		url = "https://notify-api.line.me/api/notify"
		access_token = 'UBEC8XgdJ8c0KZj7mGTVTKymMlkT4t2K8XmJqgBIE1c'
		headers = {'Authorization': 'Bearer ' + access_token}
		message = text
		files = {'imageFile': open("{}.png".format(self.instrument), "rb")}
		payload = {'message': message}
		r = requests.post(url, headers=headers, params=payload, files=files)

	def line_important(self, text,):
		text = '"'+text+'"'
		url = "https://notify-api.line.me/api/notify"
		access_token = 'Dstmvjq7hEPsgbp4cXiQqlI7ulHporflzQpi5ZCyMrg'
		headers = {'Authorization': 'Bearer ' + access_token}
		message = text
		files = {'imageFile': open("{}.png".format(self.instrument), "rb")}
		payload = {'message': message}
		r = requests.post(url, headers=headers, params=payload, files=files)

	def linetext(self, text):
		text = '"'+text+'"'
		url = "https://notify-api.line.me/api/notify"
		access_token = 'UBEC8XgdJ8c0KZj7mGTVTKymMlkT4t2K8XmJqgBIE1c'
		headers = {'Authorization': 'Bearer ' + access_token}
		message = text
		payload = {'message': message}
		r = requests.post(url, headers=headers, params=payload)   

	def graphSave(self, y):
		x = np.arange(len(y))
		x = x/2/60
		plt.plot(x,y)
		plt.grid(True)
		plt.savefig("{}.png".format(self.instrument))
		plt.clf()

	def saveState(self):
		# backup
		if Path(self.dataPath).is_file():
			with open(self.dataPath, 'rb') as f:
				lastState = pickle.load(f)
			with open(self.dataPath + ".backup", "wb") as f:
				pickle.dump(lastState, f) 	
		# save
		with open(self.dataPath, 'wb') as f:
			pickle.dump(self.stateDict, f)
	def loadState(self):
		if Path(self.dataPath).is_file():
			with open(self.dataPath, 'rb') as f:
				self.stateDict = pickle.load(f)
		else:
			pass
	def order(self, LONGSHORT, amount):
		if LONGSHORT == "LONG":
			orderAmount = "+" + str(amount)
		elif LONGSHORT == "SHORT":
			orderAmount = "-" + str(amount)
		# amount 250000
		data = {
			"order": {
				"instrument": self.instrument,
				"units": orderAmount,
				"type": "MARKET",
				"positionFill": "DEFAULT",
				}
		}
		r = orders.OrderCreate(self.accountID, data=data)
		# print("debug r: ", r)
		res = self.api.request(r)
		print("debug res: ", res)
		self.stateDict["inPrice"] = float(res['orderFillTransaction']['price'])
		if LONGSHORT == "LONG":
			self.stateDict["position"] = 1	
		elif LONGSHORT == "SHORT":
			self.stateDict["position"] = -1
		return self.stateDict["inPrice"] 

	def close(self):
		if self.stateDict["position"] == 1:
			data = {
				"longUnits" : "ALL"
			}
			longshort = "long"
		elif self.stateDict["position"] == -1:
			data = {
				"shortUnits" : "ALL"
			}
			longshort = "short"
		else:
			print("Postion state is 0, no action taken")
			return
		r = positions.PositionClose(accountID=self.accountID,
								instrument=self.instrument,
								data=data)
		res = self.api.request(r)
		self.stateDict["position"] = 0
		return res[longshort+"OrderFillTransaction"]['pl']

	def checkBalance(self):
		r = accounts.AccountSummary(self.accountID)
		response = self.api.request(r)
		return (float(response["account"]["balance"]))
	
	def unitsToOrder(self):
		return int(self.checkBalance() * 0.2 * 100) # * invest rate 0.4 * leverage 100
		

if __name__ == "__main__":
	o = OandaTrade("USD_JPY", "S30", "5000", live=True)
	t,y = o.getprice()
	print(t[-1])


	# test order
	# o.order("LONG", 5000)
	# o.updateState()	
	# o.close()
	# o.updateState()
	# o.saveState()
	# o.loadState()
	# o.graphSave(y)
	# o.line_important("test line sending")
	# print(o.stateDict["position"])

	# check exisiting position
	# testp = o.has_position(o.check_status())
	# print(testp)

	# check balance
	print(o.unitsToOrder())


