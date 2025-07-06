import os
import logging
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from .bigquery_client import BigQueryClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    logger.info("Creating BigQuery MCP server...")
    mcp = FastMCP(name="bigquery-mcp-server", host="0.0.0.0", port=8080)
    bq_client = BigQueryClient(project_id=os.getenv("GOOGLE_CLOUD_PROJECT"))
    logger.info("BigQuery client initialized with project: %s", os.getenv("GOOGLE_CLOUD_PROJECT"))

    @mcp.tool()
    async def list_datasets() -> Dict[str, List[Dict[str, Any]]]:
        """Lists all available datasets in the project."""
        logger.info("Listing datasets...")
        datasets = await bq_client.list_datasets()
        return {"datasets": datasets}

    @mcp.tool()
    async def list_tables(dataset_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Lists all tables and their schemas in a specified dataset."""
        logger.info("Listing tables for dataset: %s", dataset_id)
        tables = await bq_client.list_tables(dataset_id)
        return {"tables": tables}

    @mcp.tool()
    async def execute_query(query: str) -> Dict[str, Any]:
        """Executes a SQL query and returns the results."""
        logger.info("Executing query: %s", query)
        results = await bq_client.execute_query(query)
        return {"results": results}

    return mcp


if __name__ == "__main__":
    logger.info("Starting server...")
    server = create_server()
    logger.info("Server created, starting to run...")
    server.run(transport="sse")
