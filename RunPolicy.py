import numpy as np
from OandaTrade import OandaTrade
import datetime
import time


def linearFit(arrY):
	y = arrY
	x = np.arange(len(y))
	coe = np.polyfit(x,y,1)
	y1 = np.poly1d(coe)(x)
	#     plt.scatter(x,y)
	#     plt.plot(x,y1)
	#     plt.show()
	# 決定関数
	k = np.corrcoef(y,y1)[0,1] **2
	#     print("A1:{:.5f} A2:{:.5f} A3{:.5f}".format(coe[0], coe[1], coe[2]))
	#     print("Fit rate is {}".format(k))
	return coe, k



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> POLICIES
W = 1200 # window length

# self.stateDict["position"] = 0
# self.stateDict["inPrice"] = 0
# self.stateDict["profit"] = 0

def run_policy0(o):
	#dev, to see instance members in vscode
	# o = OandaTrade("USD_JPY", "S30", "5000", live=True)
	#/dev

	# check exisiting position
	if not o.has_position(o.check_status()) and o.stateDict["position"] != 0:
		o.stateDict["position"] = 0
		o.saveState()
		o.linetext("Seems that position manually closed.")
		


	t, y = o.getprice()

	y = np.array(y)[-W:] 
	coe, k = linearFit(y)

	# control k thres
	if o.stateDict["position"] == 0:
		# trade in
		k_thres = 0.7
	else:
		# trade out
		k_thres = 0.7

	if coe[0] > 0 and k > k_thres:
		if o.stateDict["position"] == 0:
			print("Long Condtion: {:.5f}, {:.5f}".format(coe[0], k))
			orderedPrice = o.order("LONG", 50000)
			o.saveState()
			o.graphSave(y)
			o.line_important("Ordered Long at {}: {:.5f}, {:.5f}".format(orderedPrice, coe[0], k))
		elif o.stateDict["position"] == -1: 	
			profit = o.close()
			o.saveState()
			o.graphSave(y)
			o.line_important("Long order Closed. Profit:".format(profit))

		
	elif coe[0] < 0 and k > k_thres:
		if o.stateDict["position"] == 0:
			print("Short Condtion: {:.5f}, {:.5f}".format(coe[0], k))
			orderedPrice = o.order("SHORT", 50000)
			o.saveState()
			o.graphSave(y)
			o.line_important("Ordered Short at {}: {:.5f}, {:.5f}".format(orderedPrice, coe[0], k))
		elif o.stateDict["position"] == 1:
			profit = o.close()
			o.saveState()
			o.graphSave(y)
			o.line_important("Short order Closed. Profit:".format(profit))

if __name__ == "__main__":

	o = OandaTrade("USD_JPY", "S30", "2880", live=False)
	print("Initionalized OandaTrade instance")
	print(o.stateDict)
	while True:
        # # check day of week and time and run
		time_now = datetime.datetime.now()
		hour = time_now.hour
		youbi = time_now.weekday()
		if youbi == 4 and hour >= 22:
			print("Not active time")
			time.sleep(360)
		elif youbi == 5:
			print("Not active time")
			time.sleep(360)
		elif youbi == 6:
			print("Not active time")
			time.sleep(360)
		elif youbi == 0 and hour <= 5:
			print("Not active time")
			time.sleep(350)
#         elif hour >= 1 and hour <= 5:
#             print("Not active time")
#             time.sleep(350)
		else:
			try:	
				run_policy0(o)
			except:
				pass
			time.sleep(30)