"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap, send_mail
from models import db, User, Lawyer, Answers, Question
from sqlalchemy import Column, ForeignKey, Integer, String
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Setup the Flask-JWT-Simple extension for example
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    kind = params.get('kind', None)
    if not email:
        return jsonify({"msg": "Missing email in request"}), 400
    if not password:
        return jsonify({"msg": "Missing password in request"}), 400
    # check for user in database
    kind = 'user'
    usercheck = User.query.filter_by(email=email, password=password).first()
    if usercheck is None:
        kind = 'lawyer'
        usercheck = Lawyer.query.filter_by(email=email, password=password).first()
    
    # if user not found
    if usercheck == None:
        return jsonify({"msg": "Invalid credentials provided"}), 401
    #if user found, Identity can be any data that is json serializable
    ret = {
        'jwt': create_jwt(identity=email),
        'user': usercheck.serialize(),
        'kind': kind
    }
    return jsonify(ret), 200

@app.route('/user', methods=['POST', 'GET'])
def get_user():

#Create a contact and retrieve all contacts!!

    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if "name" not in body:
            raise APIException('You need to specify the name', status_code=400)
        if 'password' not in body:
            raise APIException('You need to specify the password', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)
        if 'zipcode' not in body:
            body['zipcode'] = None
        if 'phone' not in body:
            raise APIException('You need to specify the phone', status_code=400)
        if 'kind' not in body:
            raise APIException('You need to specify the kind', status_code=400)
        
        user1 = User(name=body['name'], password = body['password'], email = body['email'], zipcode = body['zipcode'], kind= body['kind'], phone=body['phone'])
            
        db.session.add(user1)
        db.session.commit()

        return "ok", 200
    
# GET request
    if request.method == 'GET':
        all_user = User.query.all()
        all_user = list(map(lambda x: x.serialize(), all_user))
        return jsonify(all_user), 200

    return "Invalid Method", 404

@app.route('/user/<int:user_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_contact(user_id):
    """
    Single contact
    """

# PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        user1 = User.query.get(user_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)

        if "name" in body:
            user1.name = body["name"]
        if "password" in body:
            user1.password = body["password"]
        if "email" in body:
            user1.email = body["email"]
        if "zipcode" in body:
            user1.zipcode = body["zipcode"]
        db.session.commit()

        return jsonify(user1.serialize()), 200

# GET request
    if request.method == 'GET':
        user1 = User.query.get(user_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        return jsonify(user1.serialize()), 200

# DELETE request
    if request.method == 'DELETE':
        user1 = User.query.get(user_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(user1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404


# tables for lawyer


@app.route('/lawyer', methods=['POST', 'GET'])
def get_lawyer():

#Create a contact and retrieve all contacts!!

    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'name' not in body:
            raise APIException('You need to specify the name', status_code=400)
        if 'password' not in body:
            raise APIException('You need to specify the password', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)
        if 'zipcode' not in body:
            raise APIException('You need to specify the zipcode', status_code=400)
        if 'kind' not in body:
            raise APIException('You need to specify the kind', status_code=400)
        if 'phone' not in body:
            body['phone'] = None

        lawyer1 = Lawyer(name=body['name'], password = body['password'], email = body['email'], zipcode = body['zipcode'],phone = body['phone'], lawfirm= body['lawfirm'], kind= body['kind'])
        db.session.add(lawyer1)
        db.session.commit()

        return "ok", 200
    
# GET request
    if request.method == 'GET':
        all_lawyer = Lawyer.query.all()
        all_lawyer = list(map(lambda x: x.serialize(), all_lawyer))
        return jsonify(all_lawyer), 200

    return "Invalid Method", 404


@app.route('/lawyer/<int:lawyer_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_contact_lawyer(lawyer_id):
    """
    Single contact
    """

# PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        lawyer1 = Lawyer.query.get(lawyer_id)
        if lawyer1 is None:
            raise APIException('Lawyer not found', status_code=404)

        if "name" in body:
            lawyer1.name = body["name"]
        if "password" in body:
            lawyer1.password = body["password"]
        if "email" in body:
            lawyer1.email = body["email"]
        if "zipcode" in body:
            lawyer1.zipcode = body["zipcode"]
        if "phone" in body:
            lawyer1.phone = body["phone"]
        db.session.commit()

        return jsonify(lawyer1.serialize()), 200

# GET request
    if request.method == 'GET':
        lawyer1 = Lawyer.query.get(lawyer_id)
        if lawyer1 is None:
            raise APIException('Lawyer not found', status_code=404)
        return jsonify(lawyer1.serialize()), 200

# DELETE request
    if request.method == 'DELETE':
        lawyer1 = Lawyer.query.get(lawyer_id)
        if lawyer1 is None:
            raise APIException('Lawyer not found', status_code=404)
        db.session.delete(lawyer1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404
################################################################################################################################################################

# @app.route('/test_email', methods=['POST'])
# def test_send_email():
#     body = request.get_json()
#     print("####",body)
#     # body = ["abelsegui@hotmail.com", "eduardopuermas@hotmail.com"]
#     send_mail(body['list'], body['object'], body['message'])

#     return "Succesfully sent", 200

@app.route('/test_email', methods=['GET'])
def test_send_email():
    send_mail(["abelsegui@hotmail.com", "eduardopuermas@hotmail.com", "juanfco0128@gmail.com"], "A user has submitted a question", 
    "Hello! Thank you for using DiscoverLaw!" " "
    "A user has submitted a question, please follow the link below to answer" " "
    "https://8080-e4fcd649-6811-4b59-880c-956e7030f32c.ws-us02.gitpod.io/askalawyer")

    return "Succesfully sent", 200

# Beginning of Question
@app.route('/question', methods=['POST', 'GET'])
def get_question():
    
# GET request
    if request.method == 'GET':
        all_question = Question.query.all()
        all_question = list(map(lambda x: x.serialize(), all_question))
        return jsonify(all_question), 200

# POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'question' not in body:
            raise APIException('You need to specify the question', status_code=400)

        question1 = Question(question=body['question'], user_id=body['user_id'])
        db.session.add(question1)
        db.session.commit()

        return "ok", 200
    
##### END POST AND GET####################

@app.route('/question/<int:question_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_question(question_id):

# PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        question1 = Question.query.get(question_id)
        if question1 is None:
            raise APIException('Question not found', status_code=404)

        if "question" in body:
            question1.name = body["question"]
        db.session.commit()

        return jsonify(question1.serialize()), 200
    
# GET request
    if request.method == 'GET':
        question1 = Question.query.get(question_id)
        if question1 is None:
            raise APIException('Question not found', status_code=404)
        return jsonify(question1.serialize()), 200

# DELETE request
    if request.method == 'DELETE':
        question1 = Question.query.get(question_id)
        if question1 is None:
            raise APIException('Question not found', status_code=404)
        db.session.delete(question1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404
##### GET, PUT, AND DELETE####################
# End of Questions



############Beginning of Answers#################
@app.route('/answers', methods=['POST', 'GET'])
def get_answers():


# POST request
    if request.method == 'POST':
        body = request.get_json()
        print(body)

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'answers' not in body:
            raise APIException('You need to specify the answer', status_code=400)

        answers1 = Answers(answers=body['answers'])#, lawyer_id=body['lawyer_id'])
        db.session.add(answers1)
        db.session.commit()

        return "ok", 200

# GET request
    if request.method == 'GET':
        all_answers = Answers.query.all()
        all_answers = list(map(lambda x: x.serialize(), all_answers))
        return jsonify(all_answers), 200

    return "Invalid Method", 404
############End of POST, GET###############

@app.route('/answers/<int:answers_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_answers(answers_id):

# PUT Request
        if request.method == 'PUT':
            body = request.get_json()
            if body is None:
                raise APIException("You need to specify the request body as a json object", status_code=400)
            answers1 = Answers.query.get(answers_id)
            if "answers" in body:
                answers1.answers = body["answers"]
                
            db.session.commit()
            return jsonify(answers1.serialize()), 200

# GET request
        if request.method == 'GET':
            answers = Answers.query.get(answers_id)
            if answers is None:
                raise APIException('Question not found', status_code=404)
            return jsonify(answers.serialize()), 200
# DELETE request
        if request.method == 'DELETE':
            answers1 = Answers.query.get(answers_id)
            if answers1 is None:
                raise APIException('Answer not found', status_code=404)
            db.session.delete(answers1)
            db.session.commit()
            return "ok", 200

        return "Invalid Method", 404
#################End of PUT, GET, DELETE###########
#################End of Answers###################

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
