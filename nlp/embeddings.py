
import sys
import numpy as np
from gensim.models import KeyedVectors
import psycopg2
import numpy


class Embeddings:
    def __init__(self, db_host = None, db_name = None, db_user = None, db_pw = None, db_port = 25060):
        """
        Constructor for Model object.
        Input: 
            embeddings_path: string representing filepath to the word embeddings
        """
        print('Initializing Embedding Object')
        self.db_connection = None
        # DB/embeddings connection/filepath details
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.db_port = db_port

        if db_host is not None and db_name is not None and db_user is not None and db_pw is not None and db_port is not None:
            self.__connect_to_db()
        else:
            # We have a problem...
            raise Exception("Please initialize Embeddings with fuil DB connection parameters.")


    def __del__(self):
        if self.db_connection is not None:
            self.db_connection.close()


    def __connect_to_db(self):
        if self.db_connection is None:
            conn_str = "host={} user={} password={} port={} dbname={}".format(self.db_host, self.db_user, self.db_pw, self.db_port, self.db_name)
            self.db_connection = psycopg2.connect(conn_str)


    def __get_embedding_vectors_from_db(self, *words):
        query_string = 'SELECT key, embedding FROM embeddings WHERE key = ANY(%s);'
        params = list(map(str.strip, words))
        self.__connect_to_db()
        cursor = self.db_connection.cursor()
        cursor.execute(query_string, (params,))
        data = cursor.fetchall() #[(word1, vec1), (word2, vec2)...]
        result = {}
        for tup in data:
            result[tup[0]] = numpy.array(tup[1])
        return result
        
            
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
            distance between word1 and word2. 0 is smallest distance (most similar), and 1 is most dissimilar.
            If one or more of the words does not exist in the embeddings, infinity (inf) is returned.
        """
        if word1 is None or word2 is None:
            raise TypeError("input(s) None")
        if not(isinstance(word1, str) and isinstance(word2, str)):
            raise TypeError("input(s) not str") 
        try:
            word1 = word1.strip()
            word2 = word2.strip()
            vec_dic = self.__get_embedding_vectors_from_db(word1, word2)
            vec1 = vec_dic[word1]
            vec2 = vec_dic[word2]
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
        try:
            lst = []
            vec_dic = self.__get_embedding_vectors_from_db(*(word_list+[word]))
            word_vec = vec_dic[word]
            for target_word in word_list:
                target_vec = vec_dic.get(target_word, None)
                dist = float('inf')
                if target_vec is not None:
                    dist = 1 - self.__cosine_similarity(word_vec, target_vec)
                lst.append((target_word, dist))
        except KeyError:
            lst = [float('inf')] * len(word_list)
            return list(zip(word_list, lst))
        return sorted(lst, key = lambda x: x[1], reverse = not ascend)


    

if __name__ == '__main__':
    
    db_host = sys.argv[1]
    db_name = sys.argv[2]
    db_user = sys.argv[3]
    db_pw = sys.argv[4]
    db_port = int(sys.argv[5])
    embeddings = Embeddings(db_host, db_name, db_user, db_pw, db_port)
    dic = embeddings._Embeddings__get_embedding_vectors_from_db(*['dog','cat','horse'])
    print(dic) 
