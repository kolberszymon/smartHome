#!/usr/bin/python
import paho.mqtt.client as mqtt
import datetime
import psycopg2

def on_connect(client, userdata, flags, rc):
    print( str(c))
    #client.subscribe(mqtt_topic)

def on_message(client,userdata,msg):
    print( msg.topic + '\nMessage: ' + str(msg.payload))
    topic = str(msg.topic)
    device_id = topic[topic.find('/')+1:len(topic)]
    print(device_id)
    print(type(msg.payload))
    time = datetime.datetime.now()
    arguments= (str(time), str(msg.payload), device_id)
    try:
        connection = psycopg2.connect(user='postgres', password='postgres',host='localhost', port='65432', database='dane_sensory')
        cursor = connection.cursor()
        cursor.execute("SELECT * from informacje where id_urzadz=%s",device_id)
        if(bool(cursor.rowcount)):
            cursor.execute("UPDATE informacje SET data=%s,stan=%s WHERE id_urzadz=%s",arguments)
            connection.commit()
        else:
            print("ID doesn't exist")

    except(Exception, psycopg2.Error) as error:
        if(connection):
            print('Error while connecting to psql', error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("Postgres connection is closed")

mqtt_topic = 'test/+'
mqtt_broker_ip = 'localhost'
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_ip, 1883, 60)
client.subscribe(mqtt_topic)
client.loop_forever()
