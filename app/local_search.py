import pandas as pd
import tiktoken
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_covariates,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from ollama_wrapper import ChatOllama, OllamaEmbedding
from settings import load_settings_from_yaml
from constants import (
    COMMUNITY_REPORT_TABLE,
    ENTITY_TABLE,
    ENTITY_EMBEDDING_TABLE,
    RELATIONSHIP_TABLE,
    COVARIATE_TABLE,
    TEXT_UNIT_TABLE,
)

settings = load_settings_from_yaml("settings.yml")

def setup_local_search():
    llm_model = settings.GRAPHRAG_LLM_MODEL
    llm_api_base = settings.LLM_MODEL_API_BASE
    embedding_model = settings.GRAPHRAG_EMBEDDING_MODEL
    embedding_api_base = settings.EMBEDDING_MODEL_API_BASE
    claim_extraction_enabled = settings.GRAPHRAG_CLAIM_EXTRACTION_ENABLED
    INPUT_DIR = settings.INPUT_DIR
    COMMUNITY_LEVEL = settings.COMMUNITY_LEVEL

    llm = ChatOllama(
        api_base=llm_api_base,
        model=llm_model,
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")

    entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
    entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")
    report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
    relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
    covariate_df = pd.read_parquet(f"{INPUT_DIR}/{COVARIATE_TABLE}.parquet") if claim_extraction_enabled else pd.DataFrame()
    text_unit_df = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")

    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)
    relationships = read_indexer_relationships(relationship_df)
    claims = read_indexer_covariates(covariate_df) if claim_extraction_enabled else []
    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)
    text_units = read_indexer_text_units(text_unit_df)

    description_embedding_store = LanceDBVectorStore(
        collection_name="entity_description_embeddings",
    )
    description_embedding_store.connect(db_uri=f"{INPUT_DIR}/lancedb")
    store_entity_semantic_embeddings(entities=entities, vectorstore=description_embedding_store)

    context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities,
        relationships=relationships,
        covariates={"claims": claims} if claim_extraction_enabled else None,
        entity_text_embeddings=description_embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,
        text_embedder=OllamaEmbedding(
            api_base=embedding_api_base,
            model=embedding_model,
            max_retries=20,
        ),
        token_encoder=token_encoder,
    )

    search_engine = LocalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        llm_params={
            "max_tokens": 2_000,
            "temperature": 0.0,
        },
        context_builder_params={
            "use_community_summary": True,
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": True,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,
            "max_tokens": 12_000,
        },
        response_type="single paragraph",
    )

    return search_engine