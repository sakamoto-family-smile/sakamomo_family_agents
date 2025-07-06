import os
import logging
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP
from bigquery_server.bigquery_client import BigQueryClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    logger.info("Creating BigQuery MCP server...")
    mcp = FastMCP(name="bigquery-mcp-server")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    bq_client = BigQueryClient(project_id=project_id)
    logger.info("BigQuery client initialized with project: %s", project_id)

    @mcp.resource("config://version")
    def get_version():
        return "1.0.0"

    @mcp.tool()
    async def list_datasets() -> Dict[str, Union[List[Dict[str, Any]], str]]:
        """Lists all available datasets in the project."""
        logger.info("Listing datasets...")
        try:
            datasets = await bq_client.list_datasets()
            return {"datasets": datasets}
        except ValueError as e:
            logger.error("Failed to list datasets: %s", str(e))
            return {"error": str(e)}

    @mcp.tool()
    async def list_tables(
        dataset_id: str
    ) -> Dict[str, Union[List[Dict[str, Any]], str]]:
        """Lists all tables and their schemas in a specified dataset."""
        logger.info("Listing tables for dataset: %s", dataset_id)
        try:
            tables = await bq_client.list_tables(dataset_id)
            return {"tables": tables}
        except ValueError as e:
            logger.error("Failed to list tables: %s", str(e))
            return {"error": str(e)}

    @mcp.tool()
    async def get_table_schema(
        dataset_id: str, table_id: str
    ) -> Dict[str, Any]:
        """Gets the schema for a specific table."""
        logger.info("Getting schema for table: %s.%s", dataset_id, table_id)
        try:
            schema = await bq_client.get_table_schema(dataset_id, table_id)
            return {"schema": schema}
        except ValueError as e:
            logger.error("Failed to get table schema: %s", str(e))
            return {"error": str(e)}

    @mcp.tool()
    async def execute_query(
        query: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes a SQL query and returns the results with optional pagination."""
        logger.info("Executing query: %s", query)
        try:
            if not query.strip():
                raise ValueError("Query cannot be empty")

            results = await bq_client.execute_query(
                query,
                params=params,
                page_size=page_size,
                page_token=page_token
            )
            return results
        except ValueError as e:
            logger.error("Failed to execute query: %s", str(e))
            return {"error": str(e)}

    return mcp


server = create_server()


if __name__ == "__main__":
    logger.info("Server created, starting to run...")
    server.run(transport="http", path="/mcp", host="0.0.0.0", port=8080)
