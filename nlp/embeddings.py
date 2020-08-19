

import numpy as np
from gensim.models import KeyedVectors
import psycopg2
import numpy



class Embeddings:
    def __init__(self, db_host = None, db_name = None, db_user = None, db_pw = None, db_port = 25060, embeddings_path = None):
        """
        Constructor for Model object.
        Input: 
            embeddings_path: string representing filepath to the word embeddings
        """
        self.db_connection = None
        self.embeddings = None
        # DB/embeddings connection/filepath details
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.db_port = db_port
        self.embeddings_path = embeddings_path


        if db_host is not None and db_name is not None and db_user is not None and db_pw is not None and db_port is not None:
            self.__connect_to_db()

        elif embeddings_path is not None and self.db_connection is None: 
            self.embeddings = KeyedVectors.load_word2vec_format(embeddings_path, binary = True)

        else:
            # We have a problem...
            raise Exception("Please initialize Embeddings with fuil DB connection parameters or provide path to embeddings file.")

    def __del__(self):
        self.db_connection.close()

    def __connect_to_db(self):
        if self.db_connection is None:
            conn_str = "host={} user={} password={} port={} dbname={}".format(self.db_host, self.db_user, self.db_pw, self.db_port, self.db_name)
            self.db_connection = psycopg2.connect(conn_str)

    def __get_embedding_vector(self, word):
        # TODO: select multiple vectors in one sql execution
        vec = None
        # If we have loaded embeddings, use it
        if self.embeddings is not None: 
            vec = self.embeddings[word.strip()]
        else: # use db to get the embedding 
            self.__connect_to_db()
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT key, embedding FROM embeddings WHERE key=%s', (word.strip(),))
            data = cursor.fetchone()
            vec = numpy.array(data[1])
            assert type(vec) is numpy.ndarray
        return vec

    def __cosine_similarity(self, vec1, vec2):
        """
        Calculates cosine similarity between two vectors.
        Input:
            vec1: numpy array representing a word vector
            vec2: numpy array representing a word vector
        Output:
            cosine similarity between 0 and 1. 1 is most similar
        """
        if not(isinstance(vec1, np.ndarray) and isinstance(vec2, np.ndarray)):
            raise TypeError("input(s) not vector")
        dot = np.dot(vec1, vec2) 
        norma = np.linalg.norm(vec1) 
        normb = np.linalg.norm(vec2) 
        return dot / (norma * normb)



    def get_distance(self, word1, word2):
        """
        Calculate distance between two words based on cosine similarity
        Input:
            word1: string repreentation of first word
            word2: string representation of second word
        Output:
            distance between word1 and word 2. 0 is smallest distance (most similar).
        """
        if word1 is None or word2 is None:
            raise TypeError("input(s) None")
        if not(isinstance(word1, str) and isinstance(word2, str)):
            raise TypeError("input(s) not str") 
        try:
            vec1 = self.__get_embedding_vector(word1)  #self.embeddings[word1.strip()]
            vec2 = self.__get_embedding_vector(word2)  #self.embeddings[word2.strip()]
        except KeyError:
            return float("inf") # cannot find one of the words. Give largest distance.
        dist =  1 - self.__cosine_similarity(vec1, vec2)
        return dist

    def get_sorted_distances(self, word, word_list, ascend = True):
        """
        Given a center-word and a list of words, sort the words based on distance to the center words
        Input:
            word: string representation of the center word
            word_list: list of words to calcuate distance to the center word
            ascend: sort from nearest to furtherest
        Output: 
            sorted list of (word, distance) tuples 
        """
        if word is None or word_list is None:
            raise TypeError("input(s) None")
        if not(isinstance(word, str) and isinstance(word_list, list)):
            raise TypeError("input(s) type mismatch")
        lst = [(target_word, self.get_distance(word, target_word)) for target_word in word_list]
        return sorted(lst, key = lambda x: x[1], reverse = not ascend)


    

 