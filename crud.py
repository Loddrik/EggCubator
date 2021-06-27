from app import *

db.Predeterminadas.insert_many({
    "nombre": 'Gallina',
    "adv_config" : {
        "humedad" : ['60','100'],
        "temperatura" : ['37','38'],
        "rotaciones" : '4',
        "dias" : '21'
    }
},
{
    "nombre": 'Codorniz',
    "adv_config" : {
        "humedad" : ['60','90'],
        "temperatura" : ['37','38'],
        "rotaciones" : '2',
        "dias" : '17'
    }
},
{
    "nombre": 'Pato',
    "adv_config" : {
        "humedad" : ['55','75'],
        "temperatura" : ['37','38'],
        "rotaciones" : '3',
        "dias" : '30'
    }
},
{
    "nombre": 'Avestruz',
    "adv_config" : {
        "humedad" : ['20','30'],
        "temperatura" : ['36','37'],
        "rotaciones" : '10',
        "dias" : '39'
    }
})