import random
from datetime import date, datetime
import json
random.seed()

def gen_temp(t_inf,t_sup):
    return str(random.randint(int(t_inf),int(t_sup)))

def gen_hum(hum_inf,hum_sup):
    return str(random.randint(int(hum_inf),int(hum_sup)))