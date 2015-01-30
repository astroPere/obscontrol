#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys,time


def Init(pins):
    GPIO.setwarnings(False) # suppress GPIO used message
    GPIO.setmode(GPIO.BOARD) # use BOARD pin numbers (instead BCM!!!)
    #~ GPIO.setup(pins,GPIO.OUT, pull_up_down=GPIO.PUD_UP) #NOT WORKS
    GPIO.setup(pins,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #OK!! but init state inverted
    #~ GPIO.setup(pins,GPIO.OUT, pull_up_down=GPIO.PUD_DOWN) #NOT WORKS
    #~ GPIO.setup(pins,GPIO.IN, pull_up_down=GPIO.PUD_UP) #OK! but state inverted 1=Off 0=On
    return

def RelayState(pin_num):
    state=GPIO.input(pin_num)
    return state

def RelayAllStates(pins):
    pins_state=[]
    for pin_num in pins:
        pins_state.append(RelayState(pin_num))
    return pins_state


def RELAYon(pin_num,state):
    GPIO.setup(pin_num,GPIO.OUT)
    GPIO.output(pin_num,0)
    time.sleep(0.2)
    return


def RELAYoff(pin_num,state):
    GPIO.setup(pin_num,GPIO.OUT)
    GPIO.output(pin_num,1)
    time.sleep(0.2)
    return


def SetRELAY(pin_num,state):
    if int(state) == 1:
        RELAYon(pin_num,state)
    else:
        RELAYoff(pin_num,state)
    return
