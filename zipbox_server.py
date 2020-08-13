
from flask import Flask, request, make_response, abort, logging
from flask_restx import Api, Resource
import json

import logging
from nlp.embedding import Embedding


app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

api = Api(app, version='0.1', title='ZipBox', description='API for ZipNLP, an Open-Sourced NLP toolbox. [Source Code](https://github.com/eugenelin89/zipbox)')
name_space = api.namespace('nlp', description='NLP APIs')

embedding = None #Model("./nlp/embeddings.bin")




@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(401)


@name_space.route('/ping')
class Pinger(Resource):
    def get(self):
        return "Pong!"

@name_space.route('/loadEmbedding')
class EmbeddingLoader(Resource):
    def get(self):
        global embedding
        path = './nlp/embeddings.bin'
        if embedding is None:
            logger.info('Loading model from %s', path)
            embedding = Embedding(path)
            logger.info('Model loaded.')
        else:
            logger.info('Model already loaded.')
        return "Embedding Loaded"
        



@name_space.route('/distance')
class Distance(Resource):
    @api.doc(params={'origin': 'first word, eg. "dog"', 'destination': 'second word, eg. "cat"'})
    def get(self):
        """
        Get distance between two words.
        Minimum distance 0.
        Maximum distance 1.
        Example: curl 'http://localhost:5555/nlp/distance?origin=dog&destination=cat'
        Input:
            origin: first word
            destination: second word
        Output:
            {
                "distance": "0.23905432224273682"
            }
        """
        word1 = request.args.get("origin")
        word2 = request.args.get("destination")
        if word1 is None or word2 is None:
            api.abort(400, "Missing required parameter(s). Make sure to supply both origin and destination")
        dist = embedding.get_distance(word1, word2)
        res = {"distance": str(dist)}
        res = json.dumps(res, indent=4)
        # print(res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r

@name_space.route('/destinations')
class Destinations(Resource):
    @api.doc(params={'origin': 'first word, eg. "dog"', 'destinations': 'list of words in json format, eg. ["car","boat","dog","man","chair"]'})
    def get(self):
        """
        Calculate the distance between origin word and a list of destination words.
        Minimum distance 0.
        Maximum distance 1.
        Example: curl --globoff 'http://localhost:5000/api/destinations?origin=dog&destinations=["bike","horse","cat","plane"]'
        Input:
            origin: word to compute distance to list of destination words
            destinations: list of destination words to compute distance to the origin word, e.g. ["car","boat","dog","man","chair"]
        Output: 
            {
                "origin":"dog",
                "destinations": [
                    "cat",
                    "horse",
                    "bike",
                    "plane"
                ],
                "distances": [
                    "0.23905432224273682",
                    "0.5174192488193512",
                    "0.6601129174232483",
                    "0.8033067882061005"
                ]
            }
        """
        center_word = request.args.get("origin")
        neighbor_words = request.args.get("destinations")
        if center_word is None or neighbor_words is None:
            api.abort(400, "Missing required parameter(s). Make sure to supply both origin and destinations")

        try:
            neighbor_words_list = json.loads(neighbor_words.strip())
        except:
            api.abort(400,"Unable to parse destinations. Check correct json format.")
        
        if not isinstance(neighbor_words_list, list):
            api.abort(400, "Destinations must be a json array of words")
        
        sorted_neighbors_dists = embedding.get_sorted_distances(center_word.strip(), neighbor_words_list)
        sorted_neighbors = [word for (word, _) in  sorted_neighbors_dists]
        sorted_dists = [str(dist) for (_, dist) in sorted_neighbors_dists]
        res_json = {"origin":center_word, "destinations" : sorted_neighbors, "distances" : sorted_dists}
        res_str= json.dumps(res_json, indent=4)
        r = make_response(res_str)
        r.headers['Content-Type'] = 'application/json'
        return r
