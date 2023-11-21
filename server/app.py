#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]

        return campers, 200
    
    def post(self):
        try:
            new_camper = Camper(
            name = request.get_json()['name'],
            age = request.get_json()['age']
            )
            db.session.add(new_camper)
            db.session.commit()
        except ValueError:
            return { "errors": ["validation errors"] }, 400

        new_camper_dict = new_camper.to_dict()
        return new_camper_dict, 200

api.add_resource(Campers, "/campers")
 
class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return { "error": 'Camper not found' }, 404
        return camper.to_dict(), 200

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {"error": "Camper not found"}, 404
        
        data = request.get_json()
        for key in data:
            try:
                setattr(camper, key, data[key])
            except:
                return {"errors": ["validation errors"]}, 400
        db.session.add(camper)
        db.session.commit()

        camper_dict = camper.to_dict()
        return camper_dict, 202
    
api.add_resource(CamperByID, "/campers/<int:id>")

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=('-signups')) for activity in Activity.query.all()]
        return activities, 200
    
api.add_resource(Activities, "/activities")

class ActivityByID(Resource):
    def get(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return {"error": "Activity not found"}, 404

        activity_dict= activity.to_dict()
        return activity_dict, 200
    
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return {"error": "Activity not found"}, 404
        db.session.delete(activity)
        db.session.commit()
        return "", 204

api.add_resource(ActivityByID, "/activities/<int:id>")

class SignUps(Resource):
    def get(self):
        signups = [signup.to_dict() for signup in Signup.query.all()]
        return signups, 200
    
    def post(self):
        camper = Camper.query.filter_by(id=request.json["camper_id"]).first()
        activity = Activity.query.filter_by(id=request.json["activity_id"]).first()
        if not camper:
            abort(404, "Camper not found :(")
        if not activity:
            abort(404, "Activity not found :(")
        try:
            new_signup = Signup(
            camper = camper,
            activity = activity,
            time = request.json["time"]
            )
            db.session.add(new_signup)
            db.session.commit()
        except ValueError:
            return { "errors": ["validation errors"] }, 400
        return new_signup.to_dict(), 201

api.add_resource(SignUps, "/signups")


@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
