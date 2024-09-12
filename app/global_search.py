import pandas as pd
import tiktoken
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.query.structured_search.global_search.community_context import GlobalCommunityContext
from graphrag.query.indexer_adapters import read_indexer_entities, read_indexer_reports
from ollama_wrapper import ChatOllama
from settings import load_settings_from_yaml
from constants import COMMUNITY_REPORT_TABLE, ENTITY_TABLE, ENTITY_EMBEDDING_TABLE

settings = load_settings_from_yaml("settings.yml")

def setup_global_search():
    llm_model = settings.GRAPHRAG_LLM_MODEL
    llm_api_base = settings.LLM_MODEL_API_BASE
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

    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)
    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)

    context_builder = GlobalCommunityContext(
        community_reports=reports,
        entities=entities,
        token_encoder=token_encoder,
    )

    search_engine = GlobalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        max_data_tokens=12_000,
        map_llm_params={
            "max_tokens": 1000,
            "temperature": 0.0,
        },
        reduce_llm_params={
            "max_tokens": 2000,
            "temperature": 0.0,
        },
        allow_general_knowledge=True,
        json_mode=False,
        context_builder_params={
            "use_community_summary": True,
            "shuffle_data": True,
            "include_community_rank": True,
            "min_community_rank": 0,
            "community_rank_name": "rank",
            "include_community_weight": True,
            "community_weight_name": "occurrence weight",
            "normalize_community_weight": True,
            "max_tokens": 12_000,
            "context_name": "Reports",
        },
        concurrent_coroutines=32,
        response_type="single paragraph",
    )

    return search_engine