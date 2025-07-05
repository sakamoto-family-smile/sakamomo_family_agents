import os
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from .bigquery_client import BigQueryClient


def create_server() -> FastMCP:
    mcp = FastMCP(name="bigquery-mcp-server")
    bq_client = BigQueryClient(project_id=os.getenv("GOOGLE_CLOUD_PROJECT"))

    @mcp.tool()
    async def list_datasets() -> Dict[str, List[Dict[str, Any]]]:
        """Lists all available datasets in the project."""
        datasets = await bq_client.list_datasets()
        return {"datasets": datasets}

    @mcp.tool()
    async def list_tables(dataset_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Lists all tables and their schemas in a specified dataset."""
        tables = await bq_client.list_tables(dataset_id)
        return {"tables": tables}

    @mcp.tool()
    async def execute_query(query: str) -> Dict[str, Any]:
        """Executes a SQL query and returns the results."""
        return await bq_client.execute_query(query)

    return mcp


if __name__ == "__main__":
    server = create_server()
    server.run()
