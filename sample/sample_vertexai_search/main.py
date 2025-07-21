import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from google.cloud import discoveryengine
from google.cloud.discoveryengine_v1beta import SearchRequest

# Load environment variables from .env file
load_dotenv()


def init_search_client() -> discoveryengine.SearchServiceClient:
    """Initialize the Vertex AI Search client."""
    return discoveryengine.SearchServiceClient()


def get_search_service_path() -> str:
    """Get the formatted search service path."""
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("LOCATION")
    engine_id = os.getenv("ENGINE_ID")

    if not all([project_id, location, engine_id]):
        raise ValueError(
            "Missing required environment variables. "
            "Please set GCP_PROJECT_ID, LOCATION, and SEARCH_DATASTORE_ID"
        )

    return (
        f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}"
    )


def search_documents(
    query: str,
    page_size: int = 10,
    filter: Optional[str] = None,
    chunk_size: int = 1000,
    max_chunks: int = 3
) -> List[Dict]:
    """
    Search documents using Vertex AI Search with content chunks.

    Args:
        query: Search query string
        page_size: Number of results to return
        filter: Optional filter string
        chunk_size: Size of each content chunk in characters
        max_chunks: Maximum number of chunks to return per document

    Returns:
        List of search results with chunks
    """
    client = init_search_client()
    serving_config = (
        f"{get_search_service_path()}/servingConfigs/default_config"
    )

    # Create content search spec for chunk-based search
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
            #model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
            #    preamble="YOUR_CUSTOM_PROMPT"
            #),
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                version="stable",
            ),
        ),
        # search_result_mode はデフォルトが DOCUMENTS であるため記載しなくても良い
        search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.DOCUMENTS,
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            return_extractive_segment_score=True, # 関連スコアを返す
        ),
    )

    request = SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        filter=filter,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)

    results = []
    for result in response.results:
        # debug
        # print(result)

        document = result.document
        relevance_score = result.model_scores["relevance_score"]

        results.append({
            "id": document.id,
            "name": document.name,
            "relevance_score": relevance_score
        })

    return results


def main():
    """Main function to demonstrate search functionality."""
    try:
        # Example search
        query = "リクルートの有価証券報告書"
        print(f"Searching for: {query}")

        results = search_documents(
            query=query,
            page_size=5,
            # filter="language = 'en'"  # Optional filter example
        )

        print(f"\nFound {len(results)} results:")
        for idx, result in enumerate(results, 1):
            print(f"\nResult {idx}:")
            print(f"ID: {result['id']}")
            print(f"Name: {result['name']}")
            print(f"Relevance Score: {result['relevance_score']}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()