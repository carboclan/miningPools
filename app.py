from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/spider"
mongo = PyMongo(app)
api = Api(app)


class Pools(Resource):
    def get(self):
        powers = mongo.db.pools.find({}, {"_id": 0})
        return list(powers)


api.add_resource(Pools, "/")

if __name__ == "__main__":
    app.run(debug=False)
