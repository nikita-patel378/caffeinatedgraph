from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate

# Load environment variables
load_dotenv(dotenv_path='dot.env')

# Retrieve credentials from environment variables
api_key = os.getenv("OPENAI_API_KEY")
neo4j_url = os.getenv("NEO4J_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Initialize the language model for the QA Chain
llm = ChatOpenAI(openai_api_key=api_key)

# Neo4j's connection setup 
graph = Neo4jGraph(url=neo4j_url, username=neo4j_username, password=neo4j_password)

# Define a prompt template with Cypher query examples
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about coffee blends, tasting notes, and roasts.
The database schema includes:
- CoffeeBlends connected to TastingNotes
- CoffeeBlends connected to Roast types

If the user asks about similar coffee blends, use the Neo4j vector index on the embedding property to find similar blends.
For questions about tasting notes or roast type, use the following specific Cypher query templates:

1. **Find all tasting notes for a coffee blend with a specific tasting note**:
MATCH (c
)-[
]->(t
) WHERE toLower(t.name) CONTAINS toLower($tasting_note) WITH c MATCH (c)-[
]->(all_notes
) RETURN c.name AS CoffeeBlend, collect(all_notes.name) AS TastingNotes;

2. **Find coffee blends by roast type, including similar roast types**:
MATCH (c
)-[
]->(r
) WHERE r.name CONTAINS $roast_type RETURN c.name AS CoffeeBlend, r.name AS Roast;
- If the roast type is "Light," match "Light" and "Medium-Light".
- If the roast type is "Medium," match "Medium," "Medium-Light," and "Medium-Dark".
- If the roast type is "Dark," match "Dark" and "Medium-Dark".

Convert the user's question into a Cypher query based on this schema and these templates, using the vector index for blend similarity when relevant.

Schema: {schema}
Question: {question}
"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"],
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    allow_dangerous_requests=True,
    verbose=True
)


# Detect Question Type and Route to Vector or Cypher Query
def ask_coffee_question(question, purchased_blend=None):
    if purchased_blend:
        query = """
        MATCH (c:CoffeeBlend)
        WHERE c.name = $purchased_blend
        MATCH (recommend:CoffeeBlend)
        WHERE c <> recommend
        WITH recommend, gds.similarity.cosine(c.embedding, recommend.embedding) AS similarity
        RETURN recommend.name AS SimilarBlend, similarity
        ORDER BY similarity DESC
        LIMIT 3
        """
        # Execute the query using graph.query, passing parameters as a dict.
        results = graph.query(query, params={"purchased_blend": purchased_blend})
        return [
            {"SimilarBlend": record["SimilarBlend"], "Similarity": record["similarity"]}
            for record in results
        ]
    else:
        return cypher_chain.invoke({"query": question})


# Example usages
print(ask_coffee_question("Recommend some coffee blends I might like.", purchased_blend="Alpha Blend Dark Roast"))
print(ask_coffee_question("What coffee blends have vanilla notes?"))
print(ask_coffee_question("Show me all coffee blends that are light roast."))

graph.close()
