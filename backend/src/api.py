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
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        return json.dumps({
            'success':
            True,
            'drinks': [drink.short() for drink in Drink.query.all()]
        }), 200
    except:
        return json.dumps({
            'success': False,
            'error': "An Error Occurred"
        }), 500

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    all_drinks = []
    drinks=Drink.query.all()
    for drink in drinks:
        all_drinks.append(drink.long())
        
    return jsonify({
        'success': True,
        'drinks': all_drinks
    })

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
def create_drink(payload):
    # Get the body
    data = request.get_json()
    try:
        # create new Drink
        drink = Drink()
        drink.title = data['title']
        # convert recipe to String
        drink.recipe = json.dumps(data['recipe'])
        # insert the new Drink
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})

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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            abort(404)

        if title is None:
            abort(400)
        else:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        updated_drink = Drink.query.filter_by(id=drink_id).first()

        return jsonify({
            'success': True,
            'drinks': [updated_drink.long()]
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
def delete_drink(jwt, id):

    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink.id
    })
# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(AuthError)
def auth_error(error: AuthError):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401

if __name__ == "__main__":
    app.debug = True
    app.run()