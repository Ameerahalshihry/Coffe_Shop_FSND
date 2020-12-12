import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():

        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks':[drink.long() for drink in drinks]
        }),200
        

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detail_drinks(f):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }),200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(f):
    body = request.get_json()
    new_drink_title = body.get('title')
    new_drink_recipe = json.dumps(body.get('recipe')) #json.dumps() function converts a Python object into a json string.

    try:
        new_drink = Drink(title=new_drink_title, recipe=new_drink_recipe )
        new_drink.insert()

        return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })
    
    except:
        abort(422)
    
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_specific_drink(f, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
        
    if drink is None:
        abort(404)
        
    body = request.get_json()
    drink.title = body.get('title')
    drink.recipe = json.dumps(body.get('recipe')) #json.dumps() function converts a Python object into a json string.

    try:
        drink.update()

        return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })
    
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_specific_drink(f, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
        
    if drink is None:
        abort(404)
        
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
            })

    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
    'success': False,
    'message': "method not allowed",
    'error': 405
    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
    'success': False,
    'message': "bad request",
    'error': 400
    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
    'success': False,
    'message': "Internal server error",
    'error': 500
    }), 500
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
    'success': False,
    'message': "Unauthorized",
    'error': 401
    }), 401


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
    'success': False,
    'message': error.status_code,
    'error': error.error['description']
    }), error.status_code











    # JWT for manager
    # eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijl5Rl9meEl4d3hmVzBmVUhIakt4VSJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHljb2ZmZXNob3AudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmZDM2ZjAwZmY4MzdlMDA2ODE1NDUzMCIsImF1ZCI6ImRyaW5rIiwiaWF0IjoxNjA3ODA4MTUzLCJleHAiOjE2MDc4MTUzNTMsImF6cCI6IkVHTWpGNzhMRktVZG8wM3lGdzhzMVFYWHR4aE02VjVBIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.XnrF-a476m8DiR84Kq0-Q8ro-HyjphujAlwP90FhUhhKviXEi1tE_1SdkwgHJ9l-tlDiQXpFVzLSJuteTaomtobqtYZ9Wp7iPAdWfSbiYSPWkFstOcL9Vs1Ztm3her9kbh3Ao3Br2fFp5iVfpR9c6QrOTqHY2AHi3BrY4icvKDp3xBHTHq2YEI4Yzrwk8lBOdoqJaG3Ks_qjwRKf1IjV12ID7tR2mv64Y0jQirzkzxBH84JaXs_L41Q2WwslUjnOeEJyvbdBAHXpWKUv_HAA5NnOBz-6lZtBeJNkchJ5oSOljw7sYDTaeFARuPES_gFc0jhyfGGV2dKqAddAj9wdJg

    #barista
    #eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijl5Rl9meEl4d3hmVzBmVUhIakt4VSJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHljb2ZmZXNob3AudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmYzgzYWVkZjA4YTRlMDA3NmE5ZWEwNiIsImF1ZCI6ImRyaW5rIiwiaWF0IjoxNjA3ODA5NTgyLCJleHAiOjE2MDc4MTY3ODIsImF6cCI6IkVHTWpGNzhMRktVZG8wM3lGdzhzMVFYWHR4aE02VjVBIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.mK0PnrhDm3NH3hyN6nWrvuUcbD1laCbpRW7egmRPIeaWeg0T-YjFXu9vAWA1VRsOJnOZ1wb5dVBcaOdMXwifL-nQQBJqy0K0-S3mqQhrJjCuFk_EWRwqw_CVktGeu8oyM-dNk27KCbkVpw7Onwf6ai0K44yo_xYUGdLQbKNqy30MLurPc5OzP9imq4vEs3QiruFLm3V2Gscl6NJvBoJu8vD9QDnVIrju1i1-ppWdtHMCk4iyN7NOJcXUw545Bat4GL6NZORBYfYBXrWAry2h_9O1-TmOEC8bwP31yl-D57WXwEki4lHe_2oNiAuOSOAoeMwG3ZNxMIBQdOYilDOA3gol