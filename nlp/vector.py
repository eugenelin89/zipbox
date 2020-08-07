

import numpy as np
from gensim.models import KeyedVectors

class Model:
    def __init__(self, embedding_path = './embeddings.bin' ):
        """
        Constructor for Model object.
        Input: 
            embedding_path: string representing filepath to the word embeddings
        """
        self.embeddings = KeyedVectors.load_word2vec_format(embedding_path, binary = True)

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
        vec1 = self.embeddings[word1]
        vec2 = self.embeddings[word2]
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


    

 