from contextlib import redirect_stderr
from flask import Flask, render_template,request,url_for,redirect,session
from flask import json
from flask.json import jsonify
from flask_pymongo import PyMongo
from pymongo import message

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://loddrik:hermosilla@eggcuabtor.juckj.mongodb.net/EggCubator?retryWrites=true&w=majority'
app.secret_key = 'a'
cliente = PyMongo(app)
db = cliente.db



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
            return jsonify(message = "Usuario ya registrado")
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
                return 'Error en el ingreso de datos.'
    
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
                return jsonify(message = "Nombre de usuario y/o contrasena incorrectos")
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
                    return jsonify(message= "Error, no existe tu incubadora.")
                else:
                    if incubadora['incubacion_actual'] == None:
                        return redirect('/nueva_incubacion')
                    
                    else:
                        print('a')
                        session['incubacion_actual'] = incubadora['incubacion_actual']
                        session['incubaciones'] = incubadora['incubaciones']
                        return redirect ('/')
                        # ENVIAR A NOTIFICACIONES 
                       
        except:
            # Enviar a vista de error
            return jsonify(message = "Something is wrong with connection to database")
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
    if request.method == 'POST':
        
        if request.form['n_formulario'] == 'personalizada':

            if db.Incubacion.find_one({
                "id_incubadora" : session.get('id_incubadora'),
                "nombre" : request.form['nombre']
            }):
                return 'Ya existe una incubacion con ese nombre'
            
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
                    }
                })
                session['incubacion_actual'] = request.form['nombre']
                return redirect('/status')
        else:
            if db.Incubacion.find_one({
                "id_incubadora" : session.get('id_incubadora'),
                "nombre" : request.form['nombre']
            }):
                return 'Ya existe una incubacion con ese nombre'
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
                    "adv_config": i_elegida['adv_config']
                })
                session['incubacion_actual'] = request.form['nombre']
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
        incubacion = db.Incubacion.find_one({
            "nombre" : session.get('incubacion_actual'),
            "id_incubadora" : session.get('id_incubadora')
        })

        if not incubacion:
            return redirect('/nueva_incubacion')
        else:
            print(incubacion['adv_config']['humedad'][0])
            return render_template('/logged/status.html', incubacion = incubacion)


    except:
        return jsonify(message = 'Error')