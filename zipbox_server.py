
from flask import Flask, request, make_response, abort, logging
from flask_restx import Api, Resource
import json

import logging
from nlp.embeddings import Embeddings


app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

api = Api(app, version='0.1', title='ZipBox', description='API for ZipNLP, an Open-Sourced NLP toolbox. [Source Code](https://github.com/eugenelin89/zipbox)')
name_space = api.namespace('nlp', description='NLP APIs')

embeddings = None #Model("./nlp/embeddings.bin")




@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(401)


@name_space.route('/ping')
class Pinger(Resource):
    def get(self):
        return "Pong!"

@name_space.route('/loadEmbeddings')
class EmbeddingsLoader(Resource):
    @api.doc(params={'db_host': 'DB address', 'db_name': 'DB name', 'db_user': 'DB login user',
     'db_pw':'DB login password', 'db_port' :'DB port (Default 25060)'})
    def get(self):
        """
        Load embeddings database. 
        """
        msg = 'Load Embeddings'
        db_host = request.args.get('db_host').strip()
        db_name = request.args.get('db_name').strip()
        db_user = request.args.get('db_user').strip()
        db_pw = request.args.get('db_pw').strip()
        db_port = int(request.args.get('db_port').strip())
        global embeddings
        if embeddings is None:
            logger.info('Loading embeddings model')

            try:
                embeddings = Embeddings(db_host, db_name, db_user, db_pw, db_port)
            except:
                embeddings = None
                api.abort(400, "Unable to load embedding. Please check connection info.")

            if embeddings is not None:
                msg = 'Embeddings Loaded'
                logger.info(msg)
            else:
                msg = 'Unable to load embedding. Please check connection info.'
                logger.info(msg)
        else:
            msg = 'Embeddings already loaded.'
            logger.info(msg)
        return msg
        



@name_space.route('/distance')
class Distance(Resource):
    @api.doc(params={'origin': 'first word, eg. "dog"', 'destination': 'second word, eg. "cat"'})
    def get(self):
        """
        Get distance between two words.
        Minimum distance 0.
        Maximum distance 1.
        """
        if embeddings is None:
            api.abort(503, "Model not loaded")
        word1 = request.args.get("origin")
        word2 = request.args.get("destination")
        if word1 is None or word2 is None:
            api.abort(400, "Missing required parameter(s). Make sure to supply both origin and destination")
        dist = embeddings.get_distance(word1, word2)
        res = {"distance": str(dist)}
        res = json.dumps(res, indent=4)
        # print(res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r

@name_space.route('/destinations')
class Destinations(Resource):
    @api.doc(params={'origin': 'first word, eg. "dog"', 'destinations': 'list of words in valid json array, eg. ["car","boat","dog","man","chair"]'})
    def get(self):
        """
        Calculate the distance between origin word and a list of destination words.
        Minimum distance 0.
        Maximum distance 1.
        """
        if embeddings is None:
            api.abort(503, "Model not loaded")
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
        
        sorted_neighbors_dists = embeddings.get_sorted_distances(center_word.strip('"').strip("'").strip(), neighbor_words_list)
        sorted_neighbors = [word for (word, _) in  sorted_neighbors_dists]
        sorted_dists = [str(dist) for (_, dist) in sorted_neighbors_dists]
        res_json = {"origin":center_word, "destinations" : sorted_neighbors, "distances" : sorted_dists}
        res_str= json.dumps(res_json, indent=4)
        r = make_response(res_str)
        r.headers['Content-Type'] = 'application/json'
        return r
