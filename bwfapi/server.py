from flask import Flask, request
from flask_restful import Resource, Api
from web_scraper import set_db_login_credentials, initialize_db, BwfScraper
import asyncio


app = Flask(__name__)
api = Api(app)
mysql = set_db_login_credentials(app)

class HelloWorld(Resource):
    def get(self):
        return {"about": "Hello World!"}
    
    def post(self):
        return {"you sent" : request.get_json()}, 201

class Multi(Resource):
    def get(self, num):
        return {"result": num*10}

class InitializeDB(Resource):
    def get(self):
        try:
            initialize_db(mysql)
            return {"database": "success"}
        except:
            return {"database": "ERROR!"}



api.add_resource(HelloWorld, '/')
api.add_resource(Multi, '/multi/<int:num>')
api.add_resource(InitializeDB, '/init')

if __name__ == "__main__":
    app.run(debug=True)
    