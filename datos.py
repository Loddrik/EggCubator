import random
from datetime import date, datetime
import json
from flask import Flask, render_template,request,url_for,redirect,session, Response
random.seed()

def gen_temp(t_inf,t_sup):
    return random.randint(int(t_inf) -1,int(t_sup))

def gen_hum(hum_inf,hum_sup):
    return random.randint(int(hum_inf) - 3,int(hum_sup)+ 3 )


