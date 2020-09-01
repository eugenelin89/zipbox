import sys
import psycopg2

class Levenshtein:
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

    def _delete_letter(self, word):
        """
        Input:
            word: the string/word for which you will generate all possible words 
                in the vocabulary which have 1 missing character
        Output:
            delete_l: a list of all possible strings obtained by deleting 1 character from word
        """
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        delete_l = [ L + R[1:] for L, R in split_l if R]
        return delete_l

    def _switch_letter(self, word):
        """
        Input:
            word: input string
        Output:
            switches: a list of all possible strings with one adjacent charater switched
        """ 
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        switch_l = [L[:-1]+R[0]+L[-1]+R[1:] for L, R in split_l if L and R]
        return switch_l

    def _replace_letter(self, word):
        """
        Input:
            word: the input string/word 
        Output:
            replaces: a list of all possible strings where we replaced one letter from the original word. 
        """ 
        letters = 'abcdefghijklmnopqrstuvwxyz'
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        replace_set = set([a[:-1]+ c + b for a, b in split_l if a for c in letters])
        if word in replace_set:
            replace_set.remove(word)
        # turn the set back into a list and sort it, for easier viewing
        replace_l = sorted(list(replace_set))
        return replace_l

    def _insert_letter(self, word):
        """
        Input:
            word: the input string/word 
        Output:
            inserts: a set of all possible strings with one new letter inserted at every offset
        """ 
        letters = 'abcdefghijklmnopqrstuvwxyz'
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        insert_l = [a + c + b for a, b in split_l for c in letters]
        return insert_l

    def _edit_one_letter(self, word):
        """
        Input:
            word: the string/word for which we will generate all possible wordsthat are one edit away.
        Output:
            edit_one_set: a set of words with one possible edit. Please return a set. and not a list.
        """
        word_list = self._replace_letter(word) + self._insert_letter(word) + self._delete_letter(word) + self._switch_letter(word)
        edit_one_set = set(word_list)
        return edit_one_set

    def _edit_two_letters(self, word):
        """
        Input:
            word: the input string/word 
        Output:
            edit_two_set: a set of strings with all possible two edits
        """
        edit_two_set = set()    
        first_edit_set = self._edit_one_letter(word)
        for word in first_edit_set:
            tmp_set = self._edit_one_letter(word)
            edit_two_set  = edit_two_set.union(tmp_set)
    
        return edit_two_set

    def get_corrections(self, word, edit_two = False):
        suggestions = {word}.union(self._edit_one_letter(word))#.union(self._edit_two_letters(word))
        if edit_two:
            suggestions = suggestions.union(self._edit_two_letters(word))
        #print(suggestions)
        query_string = 'SELECT key FROM embeddings WHERE key = ANY(%s);'
        params = list(map(str.strip, suggestions))
        self.__connect_to_db()
        cursor = self.db_connection.cursor()
        cursor.execute(query_string, (params,))
        data = cursor.fetchall() #[(word1, vec1), (word2, vec2)...]       
        return [tup[0] for tup in data]



if __name__ == '__main__':
    
    db_host = sys.argv[1]
    db_name = sys.argv[2]
    db_user = sys.argv[3]
    db_pw = sys.argv[4]
    db_port = int(sys.argv[5])
    lev = Levenshtein(db_host, db_name, db_user, db_pw, db_port)

    #r = lev._delete_letter(word="cans")
    #print(r)
    r = lev.get_corrections("phootsynthesis")
    print(r)
    print(len(r))
    