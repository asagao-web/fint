from Run_bbPolicy import getOptPolicy
from flask import Flask, jsonify, request, redirect, url_for
from flask import render_template
import numpy as np
from OandaTrade import OandaTrade
import datetime
import time
from mod_bb import Trade, bbSimulate
from OANDA_FUNC_CONF import Data
import matplotlib.pyplot as plt
from Run_bbPolicy import viewOptPolicy
from mod_system import SystemManagement

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="adfadkfjeiafjkdakinori"
)


@app.route("/")
def hello_world():
    return "<p>OT Finance</p>"

# just sample not use
@app.route("/test")
@app.route("/test/<name>")
def test(name=None):
    return render_template("viewRealtime.html", name=name)

@app.route("/now")
def viewRealtime():
    system = SystemManagement()
    system.load()
    lastupdate = system.lastLoopTime.strftime('%Y-%m-%d %H:%M')
    status = "stopped" if system.stop else "running"
    return render_template("viewRealtime.html",lastupdate=lastupdate, status=status)

@app.route("/stopOT", methods=["POST"])
def stopOT():
    system = SystemManagement()
    system.stop = True
    system.save()
    return redirect(url_for('viewRealtime'))

@app.route("/startOT", methods=["POST"])
def startOT():
    system = SystemManagement()
    system.stop = False
    system.save()
    return redirect(url_for('viewRealtime'))

@app.route("/calculate")
def calculate(): # JSON API
    (SPAN, bWindow), detailResult = viewOptPolicy()
    data = Data(SPAN, 3000)
    data = data.bband(window=bWindow)
    date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    fig = data[["raw", "upper", "lower"]].plot(figsize=(20,6), grid=True, title=date_time).get_figure()
    fig.tight_layout()
    fig.savefig("static/currentview.png")
    
    # test
    # SPAN = "span test"
    # bWindow = "window test"
    return jsonify(s=SPAN, w=bWindow, d=detailResult)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=17625)