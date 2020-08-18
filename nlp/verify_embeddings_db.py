from gensim.models import KeyedVectors
import numpy
import psycopg2

embeddings_file_path = '[file path to embeddings]'
is_embedding_binary = True

# Connection to PostgreSql
conn_str = "host=[db url] user=[db user] password=[db password] port=[25060] dbname=[defaultdb]"
dim = 300

connection = psycopg2.connect(conn_str)

cursor = connection.cursor()

########
# Read #
########
i = 0
embeddings = KeyedVectors.load_word2vec_format(embeddings_file_path, binary = is_embedding_binary)
for key in embeddings.vocab:
    cursor.execute('SELECT key, embedding FROM embeddings WHERE key=%s', (key,))
    data = cursor.fetchone()
    value = numpy.array(data[1])
    assert type(value) is numpy.ndarray
    assert len(value) == dim
    i = i + 1
    if i % 100 == 0:
        print('{}: {}'.format(str(i), key))


connection.close()
