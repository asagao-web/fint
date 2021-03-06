import numpy as np
from OandaTrade import OandaTrade
import datetime
import time
from mod_bb import Trade, bbSimulate
from OANDA_FUNC_CONF import Data
import matplotlib.pyplot as plt
from mod_system import SystemManagement
# test opt policy in jupyter


def testOptPolicy():
    spans = [("M30", 5000), ("H1", 2500), ("H2", 1250)]
    bbWindows = [i for i in range(30, 300, 10)]
    presults = []
    for span in spans:
        for bbWindow in bbWindows:
            r = bbSimulate(span[0], span[1], bbWindow)
            presults.append(((span, bbWindow), r))

    # sort by amount
    # optResult = [((o[0][0][0], o[0][1]),o[1] ) for o in sorted(presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.7]

    # sort by weighted ave
    optResult = [((o[0][0][0], o[0][1]), o[1]) for o in sorted(
        presults, key=lambda x:x[1][2], reverse=True) if o[1][1] > 0.6]
    opt = optResult[0][0]
    print(optResult)
    print(opt)
    return opt


def getOptPolicy2():
    spans = [("M30", 5000), ("H1", 2500), ("H3", 833)]  # maya from H3 1250
    bbWindows = [i for i in range(30, 300, 10)]
    presults = []
    for span in spans:
        for bbWindow in bbWindows:
            r = bbSimulate(span[0], span[1], bbWindow)
            presults.append(((span, bbWindow), r))

    # sort by amount
    # optResult = [((o[0][0][0], o[0][1]),o[1] ) for o in sorted(presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.7]

    # sort by weighted ave
    # 1st sorting
    preResult = [o for o in sorted(
        presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.6]
    # 2nd sorting
    optResult = [((o[0][0][0], o[0][1]), o[1]) for o in sorted(
        preResult, key=lambda x:x[1][2], reverse=True) if o[1][1] > 0.6]
    ### original opt
    # opt = optResult[0][0]
    ### new opt from 3 trend
    opt = getBestFrom3rangeTrend(_get3rangeTrend(optResult))[0]
    print("NORMAL:  ",opt)
    return opt


def viewOptPolicy2():
    spans = [("M30", 5000), ("H1", 2500), ("H3", 833)]  # maya from H3 1250
    bbWindows = [i for i in range(30, 300, 10)]
    presults = []
    for span in spans:
        for bbWindow in bbWindows:
            r = bbSimulate(span[0], span[1], bbWindow)
            presults.append(((span, bbWindow), r))

    # sort by amount
    # optResult = [((o[0][0][0], o[0][1]),o[1] ) for o in sorted(presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.7]

    # sort by weighted ave
    # 1st sorting
    preResult = [o for o in sorted(
        presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.6]
    # preresults is [ ( (span, window) ), ( profit, winratio, weightedratio, trend ) ), (...............) ]
    # 2nd sorting
    optResult = [((o[0][0][0], o[0][1]), o[1]) for o in sorted(
        preResult, key=lambda x:x[1][2], reverse=True) if o[1][1] > 0.6]
    # optResult list of ((span, widnow), (profit, winratio, weightedratio, trend)) <<<<<<<<<< use this param
    ### this is original result opt
    # opt = optResult[0][0] # get best one from top

    ## this is new result opt from 3 trend
    opt = getBestFrom3rangeTrend(_get3rangeTrend(optResult))[0]
    # return opt, optResult
    # 3 range version
    return opt, _get3rangeTrend(optResult)

def _get3rangeTrend(optResult):
    M30 = [o for o in optResult if o[0][0] == "M30"][0]
    H1 = [o for o in optResult if o[0][0] == "H1"][0]
    H3 = [o for o in optResult if o[0][0] == "H3"][0]
    return (M30, H1, H3)

def getBestFrom3rangeTrend(trends3):
    print("debug :", trends3[0])
    best = [trend for trend in sorted(trends3, key=lambda x:x[1][0], reverse=True)][0]
    return best
# get opt policy for production


def getOptPolicy():
    spans = [("M30", 5000), ("H1", 2500), ("H2", 1250)]
    bbWindows = [i for i in range(30, 300, 10)]
    presults = []
    for span in spans:
        for bbWindow in bbWindows:
            r = bbSimulate(span[0], span[1], bbWindow)
            presults.append(((span, bbWindow), r))

    optResult = [((o[0][0][0], o[0][1]), o[1]) for o in sorted(
        presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.7]
    opt = optResult[0][0]
    print(optResult)
    print(opt)
    return opt


def viewOptPolicy():
    spans = [("M30", 5000), ("H1", 2500), ("H2", 1250)]
    bbWindows = [i for i in range(30, 300, 10)]
    presults = []
    for span in spans:
        for bbWindow in bbWindows:
            r = bbSimulate(span[0], span[1], bbWindow)
            presults.append(((span, bbWindow), r))

    optResult = [((o[0][0][0], o[0][1]), o[1]) for o in sorted(
        presults, key=lambda x:x[1][0], reverse=True) if o[1][1] > 0.8]
    opt = optResult[0][0]
    # print(optResult)
    print(opt)
    return opt, optResult


def run(o, SPAN, LENGTH, optW):  # args: instance, opt[0], LENGTH=5000, opt[1]
    # dev, to see instance members in vscode
    # o = OandaTrade("USD_JPY", "S30", "5000", live=True)
    # /dev

    if not o.has_position(o.check_status()) and o.stateDict["position"] != 0:
        o.stateDict["position"] = 0
        o.saveState()
        o.linetext("Seems that position manually closed.")

    data = Data(SPAN, LENGTH)
    bb = data.bband(window=optW,)

    # o.stateDict["inAbove"] = False
    # o.stateDict["inBelow"] = False

    row = bb.iloc[-1]

    if row["raw"] > row["upper"]:
        # if o.stateDict["position"] == 1:
        # 	profit = o.close()
        # 	o.saveState()
        # 	# notify
        # 	fig = bb[["raw","upper","lower"]].plot(figsize=(16, 4), grid=True).get_figure()
        # 	fig.savefig("{}.png".format(o.instrument))
        # 	o.line_important("Long order Closed. Profit:".format(profit))
        # 	# /notify
        if o.stateDict["inAbove"]:
            pass
        else:
            o.stateDict["inAbove"] = True
            o.saveState()
    elif row["raw"] < row["lower"]:
        # if o.stateDict["position"] == -1:
        # 	profit = o.close()
        # 	o.saveState()
        # 	# notify
        # 	fig = bb[["raw","upper","lower"]].plot(figsize=(16, 4), grid=True).get_figure()
        # 	fig.savefig("{}.png".format(o.instrument))
        # 	o.line_important("Short order Closed. Profit:".format(profit))
        # 	# /notify
        if o.stateDict["inBelow"]:
            pass
        else:
            o.stateDict["inBelow"] = True
            o.saveState()
    else:
        if o.stateDict["position"] == 0:
            if o.stateDict["inAbove"]:
                unitsOrder = o.unitsToOrder()
                print("debug: order amount,", unitsOrder)
                orderedPrice = o.order("SHORT", unitsOrder)
                o.stateDict["inAbove"] = False
                o.saveState()
                # notify
                fig = bb[["raw", "upper", "lower"]].plot(
                    figsize=(16, 4), grid=True).get_figure()
                fig.savefig("{}.png".format(o.instrument))
                o.line_important("Ordered Short at {}, span={}, optW={}".format(
                    orderedPrice, SPAN, optW))
            elif o.stateDict["inBelow"]:
                unitsOrder = o.unitsToOrder()
                orderedPrice = o.order("LONG", unitsOrder)
                o.stateDict["inBelow"] = False
                o.saveState()
                # notify
                fig = bb[["raw", "upper", "lower"]].plot(
                    figsize=(16, 4), grid=True).get_figure()
                fig.savefig("{}.png".format(o.instrument))
                o.line_important("Ordered Long at {}, span={}, optW={}".format(
                    orderedPrice, SPAN, optW))
        # close better version
        else:

            if o.stateDict["inAbove"] and o.stateDict["position"] == 1:
                profit = o.close()
                o.stateDict["inAbove"] = False
                o.saveState()
                # notify
                fig = bb[["raw", "upper", "lower"]].plot(
                    figsize=(16, 4), grid=True).get_figure()
                fig.savefig("{}.png".format(o.instrument))
                o.line_important("Long order Closed. Profit:".format(profit))
                # /notify

            elif o.stateDict["inBelow"] and o.stateDict["position"] == -1:
                profit = o.close()
                o.stateDict["inBelow"] = False
                o.saveState()
                # notify
                fig = bb[["raw", "upper", "lower"]].plot(
                    figsize=(16, 4), grid=True).get_figure()
                fig.savefig("{}.png".format(o.instrument))
                o.line_important("Short order Closed. Profit:".format(profit))
                # /notify
        o.stateDict["inAbove"] = False
        o.stateDict["inBelow"] = False
        o.saveState()


if __name__ == "__main__":

    # any pram ok for bb version
    o = OandaTrade("USD_JPY", "S30", "1000", live=True)
    system = SystemManagement()
    print("Initionalized OandaTrade instance")
    print(o.stateDict)
    while True:
        # # check day of week and time and run
        time_now = datetime.datetime.now()
        system.load()
        system.lastLoopTime = time_now
        system.save()
        if system.stop:
            time.sleep(60)
            continue

        hour = time_now.hour
        youbi = time_now.weekday()
        # if youbi == 4 and hour >= 22:
        # 	print("Not active time")
        # 	time.sleep(360)
        if youbi == 5 and hour >= 5:
            print("Not active time")
            time.sleep(360)
        elif youbi == 6:
            print("Not active time")
            time.sleep(360)
        elif youbi == 0 and hour <= 6:
            print("Not active time")
            time.sleep(350)
# #         elif hour >= 1 and hour <= 5:
# #             print("Not active time")
# #             time.sleep(350)
        else:
            try:
                opt = getOptPolicy2()
                # print(opt)
                # args: instance, opt[0], LENGTH=5000, opt[1]
                run(o, opt[0], 5000, opt[1])
                print(o.stateDict)
            except Exception as e:
                print("error in exception....")
                print(e)
                time.sleep(5)
                continue
            time.sleep(60*5)
