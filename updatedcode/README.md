# Coffee Knowledge GraphRAG

This folder contains updated scripts for implementing GraphRAG with both LangChain and the Neo4j GraphRAG library. The code has been updated to use the latest LangChain libraries and refactored for better organization by separating scripts based on their specific functions.

## Scripts Overview

### `coffeeknowledgetoembeddings.py`
This script is responsible for creating the vector index and generating embeddings for coffee blend descriptions. The embeddings created here are used for retrieval in GraphRAG implementations.

### `coffeeknowledgetorag.py`
This script implements GraphRAG using LangChain. It utilizes the vector index and embeddings to retrieve relevant information for answering queries related to coffee blends.

### `coffeegraphragwithneo4jgraphraglibrary.py`
This script implements GraphRAG using the Neo4j GraphRAG library. It leverages the existing vector index and embeddings created in `coffeeknowledgetoembeddings.py` to enhance retrieval and generate knowledge-grounded responses.


