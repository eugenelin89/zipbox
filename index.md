## Welcome to ZipBox

[Try ZipBox](https://box.zipnlp.com) right away, no installation!

### What is ZipBox?

ZipBox is an Open Sourced Natural Language Processing toolkit. It is the core NLP toolkit created and used by [ZipNLP](https://zipnlp.com) for building its proprietary Natural Language Platform. 

While ZipBox is still young and offers limited functionalities, it is fast-growing in order to support the development of its accompanying proprietary system. For details of ZipBox’s functionalities, check out the Online API documentation [here](https://box.zipnlp.com).


### How is ZipBox different?

The design principles behind ZipBox is to keep the system lean and fast. Models in Natural Language Processing often take up a large amount of computing resources.  Google’s popular pre-trained Word2Vec embeddings can take up to 4GB of RAM while Facebook’s fastText embeddings takes 10GB. It would be a challenge to use those tools with affordability even though there are abundant open-source tools available, such as the aforementioned Word2Vec and fastText.

ZipBox also uses the pre-trained Word2Vec embeddings. Instead of loading the embeddings into memory, it preloads embeddings onto an industry-leading DBMS, separating the concern of Natural Language Processing algorithms from the labors of carrying data in memory. This approach affords the toolkit to run on commodity machines while offering lightning speed. 



### How do I start?

#### Use ZipBox Online REST API
ZipBox is available right from the start, without any programming or installation! We offer the toolkit online via [Zipbox Online REST API](https://box.zipnlp.com). You can test-drive the toolkit and construct the complete request URL directly on the [documentation page](https://box.zipnlp.com)!

#### Clone ZipBox Github Repo
If you want to run ZipBox on your own machine, or simply want to explore deeper into the code, please feel free to clone the project from ZipBox’s [Github Repo](https://github.com/eugenelin89/zipbox).

#### Download ZipBox Docker Image

