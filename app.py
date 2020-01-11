import os
from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_restful import reqparse


app = Flask(__name__)
app.config["MONGO_URI"] = (
    os.environ.get("MONGO_URI", "mongodb://localhost:27017")
) + "/spider"
mongo = PyMongo(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("id", type=str)
parser.add_argument("ts1")
parser.add_argument("ts2")


class Pools(Resource):
    def get(self):
        powers = mongo.db.pools.find({}, {"_id": 0})
        return list(powers)


class Snapshot(Resource):
    def get(self):
        args = parser.parse_args()
        _id = args["id"]
        ts1 = int(args["ts1"])
        ts2 = int(args["ts2"])
        snapshots = mongo.db.snapshot.find(
            {"id": _id, "update_time": {"$gte": ts1, "$lt": ts2}}, {"_id": 0}
        )
        return list(snapshots)


api.add_resource(Pools, "/")
api.add_resource(Snapshot, "/snapshot")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
