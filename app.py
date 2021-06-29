from contextlib import redirect_stderr
from flask import Flask, render_template,request,url_for,redirect,session, Response
from flask import json
from flask.json import jsonify
from flask_pymongo import PyMongo
from pymongo import message
from datos import *
import time

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://loddrik:hermosilla@eggcuabtor.juckj.mongodb.net/EggCubator?retryWrites=true&w=majority'
app.secret_key = 'a'
cliente = PyMongo(app)
db = cliente.db

random.seed()

@app.route('/')
def home():
    if session:
        return render_template('logged/inicio_logged.html',name = session['username'])
    else:
        return render_template('inicio.html')



@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        id_incubadora = request.form['id_incubadora']

        # Verificamos que nadie este registrado con la misma incubadora, nombre y mail.
        if db.Usuario.find_one( { "$or":[{"id_incubadora" : id_incubadora} , {"username" : username}, {"mail" : mail}]}) != None :
            return render_template('registro.html',message = "Usuario ya registrado")
        # En caso de que no este registrado, lo registramos
        else:
            try:
                # Registro al usuario
                db.Usuario.insert({
                    'username' : username,
                    'mail': mail,
                    'password': password,
                    'id_incubadora' : id_incubadora,
                    'logged' : "False"
                })

                #Registro la incubadora
                db.Incubadora.insert({
                    'id_incubadora' : id_incubadora,
                    'incubacion_actual': None,
                    'incubaciones' : []

                })
                return redirect('/log_user')

            except:
                return render_template('registro.html',message = "Ha ocurrido un error con la conexion al cluster, por favor comuniquese con nosotros.")
    
    else:
        return render_template('registro.html')





@app.route('/log_user', methods = ['GET','POST'])
def log_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            usuario = db.Usuario.find_one({
            "username": username,
            "password" : password
            })
            

            if usuario == None:
                return render_template('login.html',message = "Usuario o contraseña incorrectos.")
            else:
                session['username'] = usuario['username']
                session['password'] = usuario['password']
                session['mail'] = usuario['mail']
                session['id_incubadora'] = usuario['id_incubadora']
                
                # Hasta ahora creamos la sesion, ahora debemos saber
                # si el ususario ta esta haciendo una incubacion o no,
                # la idea es que si no esta haciendo una, enviarlo a una pestaña
                # en donde inicie la neva incubacion, caso contrario, enviarlo a notificaciones.
                
                incubadora = db.Incubadora.find_one({
                "id_incubadora" : session.get('id_incubadora')
                })
                if incubadora == None:
                    return render_template('login.html',message = "No existe tu número de incubadora.")
                else:
                    if incubadora['incubacion_actual'] == None:
                        return redirect('/nueva_incubacion')
                    
                    else:
                        session['incubacion_actual'] = incubadora['incubacion_actual']
                        session['incubaciones'] = incubadora['incubaciones']
                        session['configs'] = db.Incubacion.find_one({ "nombre" : session.get('incubacion_actual'), "id_incubadora" : session.get('id_incubadora')})['adv_config']
                        return redirect ('/')
                        # ENVIAR A NOTIFICACIONES 
                       
        except:
            # Enviar a vista de error
            return render_template('login.html',message = "Error con la conexion a la base de datos, por favor comunicate con nosotros.")
    else:
        return render_template('login.html')




# DESDE AQUI LAS RUTAS PARA PERSONAS YA LOGGEADAS (SESSION != NONE)
@app.route('/logout')
def logout():
    username = session.get('username')
    try:
        session.clear()

        return redirect('/')
    except:
        return 'Not registered'



@app.route('/nueva_incubacion',methods = ['GET','POST'])
def nueva_incubacion():
    username = session.get('username')
    if username == None:
        return render_template('login.html')
    if request.method == 'POST':
        
        if request.form['n_formulario'] == 'personalizada':

            if db.Incubacion.find_one({
                "id_incubadora" : session.get('id_incubadora'),
                "nombre" : request.form['nombre']
            }):
                return render_template('login.html', message = "Ya existe una incubacion con ese nombre.")
            
            else:
                
                db.Incubadora.update_one({
                    "id_incubadora" : session.get('id_incubadora')},
                    {
                        "$set" : { "incubacion_actual" : request.form['nombre']},
                        "$push" : {"incubaciones" : request.form['nombre']}
                    })

                db.Incubacion.insert({
                    "nombre": request.form['nombre'],
                    "id_incubadora" : session.get('id_incubadora'),
                    "adv_config": {
                        "humedad" : [request.form['humedad_inf'],request.form['humedad_sup']],
                        "temperatura" : [request.form['temperatura_inf'],request.form['temperatura_sup']],
                        "rotaciones" : request.form['rotaciones'],
                        "dias" : request.form['dias']
                    },
                    "notificaciones" : []
                })
                session['incubacion_actual'] = request.form['nombre']
                session['configs'] = db.Incubacion.find_one({ "nombre" : session.get('incubacion_actual'), "id_incubadora" : session.get('id_incubadora')})['adv_config']
                return redirect('/status',)
        else:
            if db.Incubacion.find_one({
                "id_incubadora" : session.get('id_incubadora'),
                "nombre" : request.form['nombre']
            }):
                return render_template('login.html', message = "Ya existe una incubacion con ese nombre.")
            else:
                db.Incubadora.update_one({
                    "id_incubadora" : session.get('id_incubadora')},
                    {
                        "$set" : { "incubacion_actual" : request.form['nombre']},
                        "$push" : {"incubaciones" : request.form['nombre']}
                    })
                
                i_elegida = db.Predeterminadas.find_one(
                    {
                        "nombre" : request.form['nombre_i']

                    }
                )

                db.Incubacion.insert({
                    "nombre": request.form['nombre'],
                    "id_incubadora" : session.get('id_incubadora'),
                    "adv_config": i_elegida['adv_config'],
                    "notificaciones": []
                })
                session['incubacion_actual'] = request.form['nombre']
                session['configs'] = db.Incubacion.find_one({ "nombre" : session.get('incubacion_actual'), "id_incubadora" : session.get('id_incubadora')})['adv_config']
                return redirect('/status')


        #tomar datos del fomrulario
        # verificar si el id y el nombre de la incubacion existe
        # si existe, enviar respuesta de datos invalidos
        # si no existe, cambiar incubacion actual en base de datos y session
        
    else:
        predeterminated = list(db.Predeterminadas.find())
        return render_template('logged/nueva_incubacion.html', configurations = predeterminated)


@app.route('/status', methods = ['GET'])
def status():
    try:
        username = session.get('username')
        if username == None:
            return render_template('login.html')
        incubacion = db.Incubacion.find_one({
            "nombre" : session.get('incubacion_actual'),
            "id_incubadora" : session.get('id_incubadora')
        })

        if not incubacion:
            return redirect('/nueva_incubacion')
        else:
            return render_template('/logged/status.html', incubacion = incubacion)
    except:
        return jsonify(message = 'Error')

def generate_humedad(min,max):
    # incubacion = db.Incubacion.find_one({
    #             "id_incubadora" : session.get('id_incubadora'),
    #             "nombre" : session.get('incubacion_actual')
    #         })

    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "min" : min,
                "max" : max,
                "puerta": gen_puerta(),
                "value": gen_hum(min,max)
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(1)

def generate_temperatura(min,max):
    # incubacion = db.Incubacion.find_one({
    #             "id_incubadora" : session.get('id_incubadora'),
    #             "nombre" : session.get('incubacion_actual')
    #         })
    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "min" : min,
                "max" : max,
                "value": gen_temp(min,max)
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(1)

@app.route('/chart-data-hum')
def chart_data_hum():
    min = session.get('configs')['humedad'][0]
    max = session.get('configs')['humedad'][1]
    return Response(generate_humedad(min,max), mimetype = "text/event-stream")

@app.route('/chart-data-temp')
def chart_data_temp():
    min = session.get('configs')['temperatura'][0]
    max = session.get('configs')['temperatura'][1]
    return Response(generate_temperatura(min,max), mimetype = "text/event-stream")
        

@app.route('/notificaciones')
def notificaciones():
    username = session.get('username')
    if username == None:
        return render_template('login.html')
    return render_template('/logged/notificaciones.html')


@app.route('/historial', methods = ['GET'])
def historial():
    try:
        username = session.get('username')
        if username == None:
            return render_template('login.html')

        incubaciones = list(db.Incubacion.find({
            "id_incubadora" : session.get('id_incubadora')
        }))

        return render_template('/logged/historial.html' , incubaciones = incubaciones)


    except: return render_template('/logged/historial.html')





if __name__ == "__main__":
	app.run(debug=True)