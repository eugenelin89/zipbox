ZipBox is an Open Source Natural Language Processing toolkit. It is the core NLP toolkit created and used by [ZipNLP](https://zipnlp.com) for building its proprietary Natural Language Platform. 
For more information, please visit the official [project page](https://eugenelin89.github.io/zipbox/), or try ZipBox on the [Online Rest API](https://box.zipnlp.com)

# Quick Start
We highly recommend the use of the ZipBox Docker container, which works off-the-shelf and you can find the image [here](https://hub.docker.com/r/eugenelin89/zipbox_image).

Of course you are welcome to clone the project and run the toolkit directly in a Python virtual environment. The toolbox is developed on Anaconda distribution of Python version 3.6.10. The easiest way to set up the environment is to instal Miniconda to run the appropriate version of Python, create a virtual environment and pip install -r requirements.txt.

The toolkit requires loading Word2Vec embeddings into a PostgreSQL. The embeddings can be downloaded from [Google's Pre-trained word and phrase vectors](https://code.google.com/archive/p/word2vec/). Download GoogleNews-vectors-negative300.bin.gz from [Google](https://code.google.com/archive/p/word2vec/), and run nlp/embeddings_to_db.py, substituting the connection information of your database instance in conn_str.

