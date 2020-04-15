from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import psycopg2
import json
import time
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = '***'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///***'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


# class Network(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     ssid = db.Column(db.String(50))
#     user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # ============================== T O  D E L E T E ==============================
        #print(request.headers)
        # ============================== T O  D E L E T E ==============================

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user:
        return jsonify({'message' : 'User already exist!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # ============================== T O  D E L E T E ==============================
    #db_exec("INSERT INTO uzytkownicy (id_klient) VALUES(%s)", data['username'])
    # ============================== T O  D E L E T E ==============================

    return jsonify({'message' : 'New user created!'})


@app.route('/delete_user', methods=['DELETE'])
@token_required
def delete_user(current_user):
	num_of_collections = db_exec("SELECT COUNT(*) FROM uzytkownicy WHERE id_klient = %s", current_user.username)
	num_of_collections = num_of_collections[0][0]
	if num_of_collections != 0:
		return jsonify({'message' : 'Failed, there is a collection assigned to the user!'})

	db.session.delete(current_user)
	db.session.commit()

	return jsonify({'message' : 'The user has been deleted!'})


@app.route('/add_collection', methods=['PUT'])
@token_required
def add_collection(current_user):
    data = request.get_json()

    if 'collection' not in data or 'name' not in data:
    	return jsonify({'message' : 'invalid argument set!'})

    all_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy")
    list_of_collections = []
    for row in all_collections:
        if row[0] is not None:
            list_of_collections.append(row[0])

    if data['collection'] in list_of_collections:
        return jsonify({'message' : 'collection already in use!'})
        
    db_exec("INSERT INTO uzytkownicy (id_klient, id_kolekcja, nazwa_kolekcji) values (%s, %s, %s);", current_user.username, data['collection'], data['name'])
    return jsonify({'message' : 'collection assigned correctly!'})


@app.route('/rename_collection', methods=['PUT'])
@token_required
def rename_collection(current_user):
	data = request.get_json()

	if 'collection' not in data or 'new name' not in data:
		 return jsonify({'message' : 'invalid argument set!'})

	user_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s", current_user.username)
	list_of_collections = []
	for row in user_collections:
		if row[0] is not None:
			list_of_collections.append(row[0])
	
	if data['collection'] in list_of_collections:
		db_exec("UPDATE uzytkownicy SET nazwa_kolekcji = %s WHERE id_kolekcja = %s", data['new name'], data['collection'])
		return jsonify({'message' : 'collection name updated successfully!'})

	return jsonify({'message' : 'operation not permitted!'})


@app.route('/share_collection', methods=['POST'])
@token_required
def share_collection(current_user):
	data = request.get_json()

	if 'collection' not in data or 'successor' not in data:
		return jsonify({'message' : 'invalid argument set!'})

	user_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s", current_user.username)
	list_of_collections = []
	for row in user_collections:
		if row[0] is not None:
			list_of_collections.append(row[0])
	if data['collection'] not in list_of_collections:
		return jsonify({'message' : 'operation not permitted!'})

	successor = User.query.filter_by(username=data['successor']).first()
	if not successor:
		return jsonify({'message' : 'successor does not exist!'})

	if 'name' not in data:
		data['name'] = 'Shared collection' 

	db_exec("INSERT INTO uzytkownicy (id_klient, id_kolekcja, nazwa_kolekcji) VALUES (%s, %s, %s)", data['successor'], data['collection'], data['name'])
	return jsonify({'message' : 'collection shared successfully'})


@app.route('/delete_collection', methods=['DELETE'])
@token_required
def delete_collection(current_user):
	data = request.get_json()

	if 'collection' not in data:
		 return jsonify({'message' : 'invalid argument set!'})

	user_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s", current_user.username)
	list_of_collections = []
	for row in user_collections:
		if row[0] is not None:
			list_of_collections.append(row[0])

	if data['collection'] not in list_of_collections:
		return jsonify({'message' : 'operation not permitted!'})

	num_of_owners = db_exec("SELECT COUNT(*) FROM uzytkownicy WHERE id_kolekcja = %s", data['collection'])
	if num_of_owners[0][0] > 1:
		db_exec("DELETE FROM uzytkownicy WHERE id_kolekcja = %s AND id_klient = %s", data['collection'], current_user.username)
		return jsonify({'message' : 'collection dropped successfully!'})

	num_of_devices = db_exec("SELECT COUNT(*) FROM informacje WHERE id_kolekcja = %s", data['collection'])
	num_of_devices = num_of_devices[0][0]
	if num_of_devices > 0:
		return jsonify({'message' : 'this collection is not empty!'})

	db_exec("DELETE FROM uzytkownicy WHERE id_kolekcja = %s", data['collection'])
	return jsonify({'message' : 'collection deleted successfully!'})


@app.route('/add_device', methods=['PUT'])
@token_required
def add_device(current_user):
    data = request.get_json()

    current_user_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s", current_user.username)
    list_of_collections = []
    for row in current_user_collections:
        if row[0] is not None:
            list_of_collections.append(row[0])

    if data["collection"] not in list_of_collections:
        return jsonify({'message' : 'you don\'t manage this collection!'})

    all_devices = db_exec("SELECT id_urzadz FROM informacje")
    list_of_devices = []
    for row in all_devices:
        if row[0] is not None:
            list_of_devices.append(row[0])

    if data['device'] in list_of_devices:
        return jsonify({'message' : 'device already assigned to another collection!'})

    if 'name' not in data:
    	data['name'] = "My device"	# device name isn't mandatory argument

    db_exec("INSERT INTO informacje (id_urzadz, id_kolekcja, nazwa_urzadz) VALUES (%s, %s, %s)", data['device'], data['collection'], data['name'])
    return jsonify({'message' : 'device added to collection!'})


@app.route('/rename_device', methods=['PUT'])
@token_required
def rename_device(current_user):
	data = request.get_json()

	if 'device' not in data or 'new name' not in data:
		 return jsonify({'message' : 'invalid argument set!'})

	user_devices = db_exec("SELECT id_urzadz FROM informacje WHERE id_kolekcja IN (SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s)", current_user.username)
	list_of_devices = []
	for row in user_devices:
		if row[0] is not None:
			list_of_devices.append(row[0])
	
	if data['device'] in list_of_devices:
		db_exec("UPDATE informacje SET nazwa_urzadz = %s WHERE id_urzadz = %s", data['new name'], data['device'])
		return jsonify({'message' : 'device name updated successfully!'})

	return jsonify({'message' : 'operation not permitted!'})


@app.route('/delete_device', methods=['DELETE'])
@token_required
def delete_device(current_user):
	data = request.get_json()

	if 'device' not in data:
		 return jsonify({'message' : 'invalid argument set!'})

	user_devices = db_exec("SELECT id_urzadz FROM informacje WHERE id_kolekcja IN (SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s)", current_user.username)
	list_of_devices = []
	for row in user_devices:
		if row[0] is not None:
			list_of_devices.append(row[0])

	if data['device'] in list_of_devices:
		db_exec("DELETE FROM informacje WHERE id_urzadz = %s", data['device'])
		return jsonify({'message' : 'device deleted successfully!'})

	return jsonify({'message' : 'operation not permitted!'})


@app.route('/add_wifi', methods=['PUT'])
@token_required
def add_wifi(current_user):
	data = request.get_json()

	if 'ssid' not in data:
		return jsonify({'message' : 'invalid argument set!'})

	db_exec("INSERT INTO wifi (id_klient, ssid) VALUES (%s, %s)", current_user.username, data['ssid'])
	return jsonify({'message' : 'ssid added successfully!'})

@app.route('/delete_wifi', methods=['DELETE'])
@token_required
def delete_wifi(current_user):
	data = request.get_json()

	if 'ssid' not in data:
		return jsonify({'message' : 'invalid argument set!'})

	user_networks = db_exec("SELECT ssid FROM wifi WHERE id_klient = %s", current_user.username)
	list_of_networks = []
	for row in user_networks:
		list_of_networks.append(row[0])

	if data['ssid'] not in list_of_networks:
		return jsonify({'message' : 'Failed, SSID does not exist!'})

	db_exec("DELETE FROM wifi WHERE id_klient = %s AND ssid = %s", current_user.username, data['ssid'])
	return jsonify({'message' : 'ssid deleted successfully!'})


@app.route('/get_all_data', methods=['GET'])
@token_required
def get_all_data(current_user):
    user_networks = db_exec("SELECT ssid FROM wifi WHERE id_klient = %s", current_user.username)
    list_of_networks = []
    for row in user_networks:
        list_of_networks.append(row[0])
        
    result = {
        "user" : {
            "username" : current_user.username,
            "networks" : list_of_networks,
            "collections": []
        }
    }
    
    current_user_collections = db_exec("SELECT id_kolekcja FROM uzytkownicy WHERE id_klient = %s", current_user.username)
    list_of_collections = []
    for row in current_user_collections:
        if row[0] is not None:
            list_of_collections.append(row[0])
    
    for collection_ID in list_of_collections:
        psql_collection_entries = db_exec("SELECT * FROM informacje WHERE id_kolekcja = %s", collection_ID)
        collection_name = db_exec("SELECT nazwa_kolekcji FROM uzytkownicy WHERE id_kolekcja = %s", collection_ID)
        
        collection_dictionary = {}
        collection_dictionary["colID"] = collection_ID
        collection_dictionary["collectionName"] = collection_name[0][0]
        collection_dictionary["devices"] = []
        
        for single_device in psql_collection_entries:
            temporary_dictionary = {}
            temporary_dictionary["lastStateChange"] = single_device[0]
            temporary_dictionary["devID"] = single_device[1]
            temporary_dictionary["deviceName"] = single_device[2]
            temporary_dictionary["isClosed"] = single_device[3]
        
            collection_dictionary["devices"].append(temporary_dictionary)
        
        result["user"]["collections"].append(collection_dictionary)
        
    #return jsonify({'message' : 'ok', 'result' : json.dumps(result).replace('{', 'Object {').replace('[', 'Array [')})
    return jsonify({'message' : 'ok', 'result' : json.dumps(result, ensure_ascii=False)})		# oryginal JSON form


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({'message' : 'Login and password required!'}), 401, {'WWW-Authenticate' : 'Basic realm="Login and password required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response(jsonify({'message' : 'User doesn\'t exist!'}), 401, {'WWW-Authenticate' : 'Basic realm="User doesn\'t exist!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'username' : user.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        # token = jwt.encode({
        # 	'username' : user.username, 
        # 	'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30), 
        # 	'salt' : random.randrange(10**9)
        # 	}, app.config['SECRET_KEY'])	# token with salting

        return jsonify({'message' : 'ok', 'token' : token.decode('UTF-8')})

    return make_response(jsonify({'message' : 'Login and password don\'t match!'}), 401, {'WWW-Authenticate' : 'Basic realm="Login and password don\'t match!"'})


@app.route('/validate', methods=['GET'])
@token_required
def validate(current_user):
	token = request.headers['x-access-token']
	data = jwt.decode(token, app.config['SECRET_KEY'])
	exp = data['exp']
	return jsonify({'message' : 'ok', 'Token expiration date' : time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(exp))})


def db_exec(inquiry, *args):
    connection = psycopg2.connect(user="postgres", password="postgres",
                                  host="localhost", port="5432", database="dane_sensory")
    try:
        cursor=connection.cursor()
        cursor.execute(inquiry, args)
        connection.commit()
        result = cursor.fetchall()
        return result

    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


# ============================== T O  D E L E T E ==============================
# def select_all():
#     connection = psycopg2.connect(user="postgres", password="postgres",
#                                   host="localhost", port="5432", database="dane_sensory")
#     try:
#         cursor=connection.cursor()

#         cursor.execute("SELECT * from informacje;")

#         records = cursor.fetchall()
#         print(records)

#     except (Exception, psycopg2.Error) as error :
#         print("Error while connecting to PostgreSQL", error)

#     finally:
#         if (connection):
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")

# @app.route('/list_users', methods=['GET'])
# @token_required
# def get_all_users(current_user):
#     users = User.query.all()

#     output = []

#     for user in users:
#         user_data = {}
#         user_data['username'] = user.username
#         user_data['password'] = user.password
#         output.append(user_data)

#     return jsonify({'users' : output})
# ============================== T O  D E L E T E ==============================


if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True, host='0.0.0.0')	# TURN OFF DEBUGGER ON THE FINAL RELEASE !!!
