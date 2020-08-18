from gensim.models import KeyedVectors
import numpy
import psycopg2
from psycopg2.extensions import register_adapter
from psycopg2.extras import Json




embeddings_file_path = '[file path to embeddings file]'
is_embedding_binary = True

# Connecting to PostgreSql
conn_str = "host=[db url] user=[db user name] password=[db password] port=[25060] dbname=[defaultdb]"


connection = psycopg2.connect(conn_str)


def adapt_numpy_ndarray(numpy_ndarray):
    return Json(numpy_ndarray.tolist())

register_adapter(numpy.ndarray, adapt_numpy_ndarray)
cursor = connection.cursor()

cursor.execute('CREATE TABLE embeddings (key varchar, embedding jsonb);')
connection.commit()

#########
# Write #
#########

embeddings = KeyedVectors.load_word2vec_format(embeddings_file_path, binary = is_embedding_binary)
i = 0
for word in embeddings.vocab:
    i = i + 1
    key = word
    emb = embeddings[word] # np array of vector
    cursor.execute('INSERT INTO embeddings (key, embedding) VALUES (%s, %s)', [key, emb])
    connection.commit()
    if i % 1000 == 0:
        print(i)

connection.close()
