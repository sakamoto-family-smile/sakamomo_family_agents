"""BigQuery MCP Server package."""

from .server import create_server, server
from .bigquery_client import BigQueryClient

__all__ = ["create_server", "server", "BigQueryClient"]
__version__ = "0.1.0"