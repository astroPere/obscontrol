#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import  Flask,request, session, g, redirect, url_for, abort, render_template, flash, make_response
from CTois_2 import CTois
import RPi.GPIO as GPIO
import requests
import random
import datetime,time,os
import pins
import indiclient


ctois=CTois()

app = Flask(__name__)


indi = indiclient.indiclient("127.0.0.1", 7624)


### RELAYS ###
relays_DATA = {}
relays_numbers = ['0','1','2','3','4','5','6','7']
relays_names=["Camera","AO Dev.","Rotator","Mount","Focuser","Fans","USB Hub","Flats lamp"]
ports_numbers=[11,12,13,15,16,18,22,7] #BOARD mode numbers , not GPIO mode!!

### TELESCOPE ###
telescope_DATA = {}
telescope_names = ['CDK','OTHER']
telescope_numbers = [0,1]
tel_data0 = ['DATE','LOCAL','UTC','LST']
tel_data00 = ['aa-aa-aa','00:00:00','11:11:11','22:22:22']
tel_data = dict(zip(tel_data0,tel_data00))


pins.Init(ports_numbers)


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')
#~
@app.route('/telescope')
def telescope():

    InitData_Telescope()

    return render_template('telescope.html', **telescope_DATA)


@app.route('/relays')
def relays():

    InitData_Relays()

    return render_template('relays.html', **relays_DATA)


@app.route("/relays/<dev>/<state>/<name>")
def change_state(dev,state,name):
    global relays_DATA

    port= relays_DATA['dev'][str(dev)]['port']
    state = relays_DATA['dev'][str(dev)]['state']

    print '         SWITCHING RELAY:',dev,port,state

    pins.SetRELAY(int(port),int(state))

    return redirect(url_for('relays'))


@app.route("/relays/all/<state>")
def change_ALLstates(state):
    global relays_DATA
    global ports_numbers

    for port in ports_numbers:

        print '     SWITCHING ALL RELAYS:',port,state
        pins.SetRELAY(int(port),int(state))

    return redirect(url_for('relays'))


def InitData_Relays():

    global relays_DATA, ports_numbers,relays_names,relays_numbers
    dev=[]
    timeUTC = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
    states = pins.RelayAllStates(ports_numbers)

    print '     INIT STATES:',states

    for x in relays_numbers:
        i = int(x)
        dev.append({'relay':x,'state':states[i],'port':ports_numbers[i],'name':relays_names[i]})
        print '         ',repr(dev[i])
    dev=dict(zip(relays_numbers,dev))
    relays_DATA={'dev':dev,'dataR':{'time':timeUTC}}

def InitData_Telescope():
    global telescope_DATA,tel_data,telescope_numbers
    tel=[]
    #~ for i in telescope_numbers:
        #~ tel.append(({tel_data}))
    tel = dict(zip(telescope_numbers,telescope_names))
    timeUTC = datetime.datetime.utcnow().strftime("%H:%M:%S")
    dateUTC = datetime.datetime.utcnow().strftime("%Y / %m / %d")
    tel_data['UTC'] = timeUTC
    tel_data['DATE'] = dateUTC
    tel_data['JD'] = ctois.UT2jd(datetime.datetime.utcnow())
    tel_data['LOCAL'] = datetime.datetime.now().strftime("%H:%M:%S")
    tel_data['LST'] = ctois.UT2LST(datetime.datetime.utcnow())
    telescope_DATA={'dataT':tel_data}

    #~ vector=indi.get_vector("Telescope Simulator","CONNECTION")
    #~ vector.set_by_elementname("CONNECT")
    indi.set_and_send_switchvector_by_elementlabel("Telescope Simulator", "CONNECTION", "On")
    print '     connect: ON'
    indi.set_and_send_switchvector_by_elementlabel("Telescope Simulator", "ON_COORD_SET", "Goto")
    indi.set_and_send_float("Telescope Simulator", "EQUATORIAL_EOD_COORD", "RA", 22.5213698547)
    print '     goto RA:22.5213698547'
    #~ indi.send_vector(vector)
    time.sleep(1)
    #~ vector.tell()
#~
    print '++++',indi.tell()
    #~ print '     DataT:', telescope_DATA
    #~ return telescope_DATA

if __name__ == '__main__':

    app.run(host='192.168.2.6',debug=True)

    InitData_Relays()
    InitData_Telescope()

#~ TODO: VERIFY RELAY's STATES (ON HARDWARE) AFTER CHANGE IT.
