import random
from datetime import date, datetime
import json
from flask import Flask, render_template,request,url_for,redirect,session, Response
random.seed()

def gen_temp(t_inf,t_sup):
    return random.randint(int(t_inf) + 3,int(t_sup) + 3)

def gen_hum(hum_inf,hum_sup):
    return random.randint(int(hum_inf) + 3,int(hum_sup)+ 3 )

def notify_temp(min,max,data):
    if data > max:
        return "Temperatura sobre los rangos"
    else:
        return "Temperatura bajo los rangos"

def notify_hum(min,max,data):
    if data > max:
        return "Humedad sobre los rangos"
    else:
        return "Humedad bajo los rangos"


