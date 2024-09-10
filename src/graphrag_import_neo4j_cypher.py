import os
from dotenv import load_dotenv
import time
import pandas as pd
from neo4j import GraphDatabase

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the root directory (one level up from src)
root_dir = os.path.dirname(current_dir)

# Load environment variables from the root directory
load_dotenv(os.path.join(root_dir, ".env"))

# Neo4j connection details
GRAPHRAG_FOLDER = os.path.join(
    root_dir, "rag", "output", "20240906-214626", "artifacts"
)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

# Print connection details for debugging (don't print the actual password)
print(f"NEO4J_URI: {NEO4J_URI}")
print(f"NEO4J_USER: {NEO4J_USERNAME}")
print(f"NEO4J_PASSWORD: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else 'Not set'}")
print(f"NEO4J_DATABASE: {NEO4J_DATABASE}")

# Create a Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

try:
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        print(f"Connection test result: {result.single()['num']}")
except Exception as e:
    print(f"Connection error: {e}")
finally:
    driver.close()


def batched_import(driver, statement, df, batch_size=1000):
    """
    Import a dataframe into Neo4j using a batched approach.

    Parameters: statement is the Cypher query to execute, df is the dataframe to import, and batch_size is the number of rows to import in each batch.
    """
    total = len(df)
    start_s = time.time()

    with driver.session(database=NEO4J_DATABASE) as session:
        for start in range(0, total, batch_size):
            batch = df.iloc[start : min(start + batch_size, total)]
            try:
                result = session.run(
                    "UNWIND $rows AS value " + statement, rows=batch.to_dict("records")
                )
                print(result.consume().counters)
            except Exception as e:
                print(f"Error in batch import: {e}")

    print(f"{total} rows in {time.time() - start_s} s.")
    return total


def create_constraints(driver):
    statements = """
    CREATE CONSTRAINT IF NOT EXISTS FOR (c:__Chunk__) REQUIRE c.id IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR (d:__Document__) REQUIRE d.id IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR (c:__Community__) REQUIRE c.community IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR (e:__Entity__) REQUIRE e.id IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR (e:__Entity__) REQUIRE e.name IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR (e:__Covariate__) REQUIRE e.title IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS FOR ()-[rel:RELATED]->() REQUIRE rel.id IS UNIQUE;
    """.split(";")

    with driver.session(database=NEO4J_DATABASE) as session:
        for statement in statements:
            if len((statement or "").strip()) > 0:
                print(f"Executing constraint: {statement.strip()}")
                session.run(statement.strip())


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    try:
        # Create constraints
        create_constraints(driver)

        # Import documents
        documents_df = pd.read_parquet(
            f"{GRAPHRAG_FOLDER}/create_final_documents.parquet"
        )
        document_statement = """
        MERGE (d:__Document__ {id: value.id})
        SET d.title = value.title
        """
        batched_import(driver, document_statement, documents_df)

        # Import chunks
        chunks_df = pd.read_parquet(
            f"{GRAPHRAG_FOLDER}/create_final_text_units.parquet"
        )
        chunk_statement = """
        MERGE (c:__Chunk__ {id: value.id})
        SET c.text = value.text, c.n_tokens = value.n_tokens
        WITH c, value
        UNWIND value.document_ids AS doc_id
        MERGE (d:__Document__ {id: doc_id})
        MERGE (d)-[:CONTAINS]->(c)
        """
        batched_import(driver, chunk_statement, chunks_df)

        # Import entities (Handling Hebrew UTF-8 text encoding and entity types)
        entities_df = pd.read_parquet(
                f"{GRAPHRAG_FOLDER}/create_final_entities.parquet"
        )
        entities_df["type"] = entities_df["type"].map(
                {
                        "character"     : "דמויות",
                        "magical_object": "חפצים קסומים",
                        "place"         : "מקומות",
                        "event"         : "אירועים",
                        "institution"   : "מוסדות",
                }
        )
        entities_df = entities_df.dropna(subset=["type"])
        
        entity_statement = """
        MERGE (e:__Entity__ {id: value.id})
        SET e.name = value.name,
            e.type = value.type,
            e.description = value.description
        """
        batched_import(driver, entity_statement, entities_df)
        
        # Import relationships (Ensuring Hebrew names and relationships are handled)
        relationships_df = pd.read_parquet(
                f"{GRAPHRAG_FOLDER}/create_final_relationships.parquet"
        )
        relationships_df = relationships_df.dropna(subset=["source", "target"])
        
        relationship_statement = """
        MATCH (source:__Entity__ {name: value.source})
        MATCH (target:__Entity__ {name: value.target})
        MERGE (source)-[r:RELATED {id: value.id}]->(target)
        SET r.rank = value.rank, r.weight = value.weight,
            r.human_readable_id = value.human_readable_id, r.description = value.description
        WITH source, target, value
        UNWIND value.text_unit_ids AS chunk_id
        MERGE (c:__Chunk__ {id: chunk_id})
        MERGE (source)-[:MENTIONED_IN]->(c)
        MERGE (target)-[:MENTIONED_IN]->(c)
        """
        batched_import(driver, relationship_statement, relationships_df)
        
        # Import communities
        communities_df = pd.read_parquet(
                f"{GRAPHRAG_FOLDER}/create_final_communities.parquet"
        )
        communities_df = communities_df.dropna(subset=["id", "title"])
        
        community_statement = """
        MERGE (c:__Community__ {community: value.id})
        SET c.level = value.level, c.title = value.title
        WITH c, value
        UNWIND value.text_unit_ids AS chunk_id
        MERGE (chunk:__Chunk__ {id: chunk_id})
        MERGE (c)-[:CONTAINS]->(chunk)
        WITH c, value
        UNWIND value.relationship_ids AS rel_id
        MATCH ()-[r:RELATED {id: rel_id}]->()
        WITH c, startNode(r) AS start, endNode(r) AS end
        MERGE (c)-[:RELATED_TO]->(start)
        MERGE (c)-[:RELATED_TO]->(end)
        """
        batched_import(driver, community_statement, communities_df)

        # Import covariates
        covariates_df = pd.read_parquet(
            f"{GRAPHRAG_FOLDER}/create_final_community_reports.parquet"
        )
        covariates_df.drop_duplicates(subset=["title"], inplace=True)
        
        covariate_statement = """
        MERGE (c:__Covariate__ {title: value.title})
        SET c.community = value.community,
            c.level = value.level,
            c.summary = value.summary,
            c.explanation = value.explanation,
            c.rank = value.rank,
            c.rank_explanation = value.rank_explanation,
            c.full_content = value.full_content
        """
        batched_import(driver, covariate_statement, covariates_df)

    except Exception as e:
        print(f"Error during import: {e}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
