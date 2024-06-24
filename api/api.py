import json
from flask import Flask, jsonify, request
from helpers import get_anp, get_anps, get_grid_anp, insert_colouration, \
    login, encrypt_bearer_token, validate_bearer_token, get_cells_by_polygon, \
    get_dashboard_data
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
    
    response = app.make_default_options_response()
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    headers['Access-Control-Allow-Headers'] = 'Content-Type'

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

    response = app.make_default_options_response()
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    headers['Access-Control-Allow-Headers'] = 'Content-Type'

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


@app.route('/get_cells', methods=['POST'])
def get_cells():
    data = {'cells': []}
    try:
        body = request.get_json()
        polygon = body['polygon']['geometry']
        id_anp = body['id_anp']
        data['cells'] = [
                {
                    'id': t[0], 
                    'border': json.loads(t[1]), 
                    'id_colour': t[2]
                } for t in get_cells_by_polygon(json.dumps(polygon), id_anp)]
    except Exception as e:
        data['success'] = False
        print(str(e))
    return jsonify(data)

@app.route('/getDashboardData', methods=['GET'])
def getDashboardData():
    data = get_dashboard_data()
    data = {
        'success': True,
        'data': data
    }
    return jsonify(data)