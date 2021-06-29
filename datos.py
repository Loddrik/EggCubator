import random
from datetime import date, datetime
import json
from flask import Flask, render_template,request,url_for,redirect,session, Response
random.seed()

def gen_temp(t_inf,t_sup):
    a_list = int()
    return random.randint(int(t_inf) -1,int(t_sup))

def gen_hum(hum_inf,hum_sup):
    return random.randint(int(hum_inf) - 3,int(hum_sup)+ 3 )

def gen_puerta():
    a_list= [0,1]
    distribucion = [.95, .05]
    return random.choices(a_list,distribucion)


