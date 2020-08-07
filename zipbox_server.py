from flask import Flask, request, make_response, abort, logging
#from flask_restplus import Api, Resource
import json
from nlp.vector import Model


app = Flask(__name__)
#app = Api(app = flask_app)
#name_space = app.namespace('main', description='Main APIs')

model = Model("./nlp/embeddings.bin")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(401)




@app.route('/model/getDistance')
def get_distance():
    """
    Calculate distance between word1 and word2
    Example: curl 'http://localhost:5000/model/getDistance?word1=dog&word2=cat'
    Input:
        word1
        word2
    Output:
        {
            "distance": "0.23905432224273682"
        }
    """
    word1 = request.args.get("word1")
    word2 = request.args.get("word2")
    if word1 is None or word2 is None:
        raise TypeError("missing request argument(s)")
    dist = model.get_distance(word1, word2)
    res = {"distance": str(dist)}
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/model/sortedNeighbors')
def get_simularities():
    """
    Calculate the distance between center_word and a list of neighbor_words
    Example: curl --globoff 'http://localhost:5000/model/sortedNeighbors?center_word=dog&neighbor_words=["bike","horse","cat","plane"]'
    Input:
        center_word: word to compute distance to list of neighbor_words
        neighbor_words: list of words to compute distance to the center_word
    Output:
        {
            "sorted_neighbors": [
                "cat",
                "horse",
                "bike",
                "plane"
            ],
            "sorted_dists": [
                "0.23905432224273682",
                "0.5174192488193512",
                "0.6601129174232483",
                "0.8033067882061005"
            ]
        }
    """
    center_word = request.args.get("center_word")
    neighbor_words = request.args.get("neighbor_words")
    if center_word is None or neighbor_words is None:
        raise TypeError("missing request argument(s)")
    neighbor_words_list = json.loads(neighbor_words)
    if not isinstance(neighbor_words_list, list):
        raise TypeError("neighbor_words must be json array of string")
    sorted_neighbors_dists = model.get_sorted_distances(center_word, neighbor_words_list)
    sorted_neighbors = [word for (word, _) in  sorted_neighbors_dists]
    sorted_dists = [str(dist) for (_, dist) in sorted_neighbors_dists]
    res_json = {"sorted_neighbors" : sorted_neighbors, "sorted_dists" : sorted_dists}
    res_str= json.dumps(res_json, indent=4)
    r = make_response(res_str)
    r.headers['Content-Type'] = 'application/json'
    return r