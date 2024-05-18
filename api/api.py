import json
from flask import Flask, jsonify, request
from helpers import get_anp, get_anps, get_grid_anp, insert_colouration, \
    login, encrypt_bearer_token, validate_bearer_token
from flask_cors import CORS



app = Flask(__name__)
CORS(app)


@app.route('/')
def helloWorld():
    return "<p>Hello, World!</p>"


@app.route('/getANP/<int:anp_id>')
def getANP(anp_id):
    user_id = validate_bearer_token(request.headers)
    if user_id == None:
        return {
            'success': False,
            'border': None,
            'centroid': None
        }
    raw_data = get_anp(anp_id)
    data = {
        'success': True,
        'border': json.loads(raw_data[0]),
        'centroid': json.loads(raw_data[1])
    }
    return jsonify(data)


@app.route('/getANPs')
def getANPs():
    user_id = validate_bearer_token(request.headers)
    if user_id == None:
        return {
            'success': False,
            'anps': None
        }
    raw_data = get_anps(user_id)
    data = {
            'success': True,
            'anps': [
                {
                    'id': it[0],
                    'nombre': it[1],
                    'border': json.loads(it[2])
                }
                for it in raw_data
            ]
        }
    return jsonify(data)


@app.route('/getGridANP/<int:anp_id>')
def getGridANPId(anp_id):
    user_id = validate_bearer_token(request.headers)
    if user_id == None:
        return {
            'success': False,
            'grid': None
        }
    raw_data = get_grid_anp(anp_id, user_id)
    data = {
            'success': True,
            'grid': [
                {
                    'id': cell[0],
                    'border': json.loads(cell[1]),
                    'id_colour': cell[2],
                }
                for cell in raw_data
            ]}
    return jsonify(data)


@app.route('/createColouration/<int:anp_id>', methods=['POST'])
def createColouration(anp_id):
    user_id = validate_bearer_token(request.headers)
    if user_id == None:
        return {
            'success': False
        }
    colouration = request.get_json()['colouration']
    data = {
        'success': True
    }
    try:
        insert_colouration(colouration, user_id, anp_id)
    except Exception as e:
        print(str(e))
        data['success'] = False
    return jsonify(data)


@app.route('/login', methods=['POST'])
def login_ep():
    data = {'success': True, 'id_user': None, 'bearer_token': None}
    try:
        body = request.get_json()
        user = login(body['email'], body['password'])
        if user != None:
            data['id_user'] = user[0]
            data['bearer_token'] = encrypt_bearer_token(data['id_user'])
    except Exception as e:
        data['success'] = False
        print(str(e))
    return jsonify(data)

