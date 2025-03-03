from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv(dotenv_path='dot.env')
api_key = os.getenv("OPENAI_API_KEY")

# Initialize embeddings model
embedding_model = OpenAIEmbeddings(openai_api_key=api_key)

# Neo4j connection setup
neo4j_url = os.getenv("NEO4J_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
graph = Neo4jGraph(url=neo4j_url, username=neo4j_username, password=neo4j_password)


# Generate and store embeddings as arrays using `graph.query()`
def embed_and_store_descriptions():
    query = """ 
    MATCH (c:CoffeeBlend) 
    RETURN c.name AS name, c.description AS description 
    """

    # Fetch coffee blends
    coffee_blends = graph.query(query)

    for record in coffee_blends:
        name = record["name"]
        description = record["description"]

        # Generate the embedding for the description
        embedding = embedding_model.embed_query(description)
        embedding = [float(x) for x in embedding]  # Ensure correct float format

        # Store embedding in Neo4j
        update_query = """
        MATCH (c:CoffeeBlend {name: $name})
        SET c.embedding = $embedding
        """
        graph.query(update_query, params={"name": name, "embedding": embedding})


# Run the function
embed_and_store_descriptions()
