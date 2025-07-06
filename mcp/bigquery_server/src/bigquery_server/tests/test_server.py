import os
import pytest
from unittest.mock import AsyncMock, patch
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent

from bigquery_server.server import create_server


@pytest.fixture
def mock_bq_client():
    with patch("bigquery_server.server.BigQueryClient") as mock_client:
        # Create a mock instance
        client_instance = mock_client.return_value

        # Mock the async methods
        client_instance.list_datasets = AsyncMock()
        client_instance.list_tables = AsyncMock()
        client_instance.execute_query = AsyncMock()

        yield client_instance


@pytest.fixture
def server(mock_bq_client):
    return create_server()


@pytest.mark.asyncio
async def test_list_datasets(server, mock_bq_client):
    # Prepare mock response
    mock_datasets = [
        {
            "id": "test_dataset_1",
            "name": "Test Dataset 1",
        },
        {
            "id": "test_dataset_2",
            "name": "Test Dataset 2",
        },
    ]
    mock_bq_client.list_datasets.return_value = mock_datasets

    # Call the tool
    result = await server.call_tool("list_datasets", {})

    # Verify the result matches the mock response
    mock_bq_client.list_datasets.assert_called_once()
    assert isinstance(result, tuple)  # FastMCP returns a tuple
    content_blocks, structured_data = result
    assert isinstance(content_blocks, list)  # List of content blocks
    assert len(content_blocks) == 1  # Should have one content block
    content = content_blocks[0]
    assert isinstance(content, TextContent)  # Should be a TextContent block
    assert content.type == "text"  # Should be a text content block
    assert structured_data == {"result": {"datasets": mock_datasets}}


@pytest.mark.asyncio
async def test_list_tables(server, mock_bq_client):
    # Prepare mock response
    mock_tables = [
        {
            "id": "test_table_1",
            "name": "Test Table 1",
            "schema": {
                "fields": [{"name": "column1", "type": "STRING"}]
            },
        },
        {
            "id": "test_table_2",
            "name": "Test Table 2",
            "schema": {
                "fields": [{"name": "column2", "type": "INTEGER"}]
            },
        },
    ]
    mock_bq_client.list_tables.return_value = mock_tables

    # Call the tool
    result = await server.call_tool(
        "list_tables",
        {"dataset_id": "test_dataset"}
    )

    # Verify the result matches the mock response
    mock_bq_client.list_tables.assert_called_once_with("test_dataset")
    assert isinstance(result, tuple)  # FastMCP returns a tuple
    content_blocks, structured_data = result
    assert isinstance(content_blocks, list)  # List of content blocks
    assert len(content_blocks) == 1  # Should have one content block
    content = content_blocks[0]
    assert isinstance(content, TextContent)  # Should be a TextContent block
    assert content.type == "text"  # Should be a text content block
    assert structured_data == {"result": {"tables": mock_tables}}


@pytest.mark.asyncio
async def test_execute_query(server, mock_bq_client):
    # Prepare mock response
    mock_results = [
        {"column1": "value1", "column2": 1},
        {"column1": "value2", "column2": 2},
    ]
    mock_bq_client.execute_query.return_value = mock_results

    # Call the tool
    result = await server.call_tool(
        "execute_query",
        {"query": "SELECT * FROM test_table"}
    )

    # Verify the result matches the mock response
    mock_bq_client.execute_query.assert_called_once_with(
        "SELECT * FROM test_table"
    )
    assert isinstance(result, tuple)  # FastMCP returns a tuple
    content_blocks, structured_data = result
    assert isinstance(content_blocks, list)  # List of content blocks
    assert len(content_blocks) == 1  # Should have one content block
    content = content_blocks[0]
    assert isinstance(content, TextContent)  # Should be a TextContent block
    assert content.type == "text"  # Should be a text content block
    assert structured_data == {"result": {"results": mock_results}}


@pytest.mark.asyncio
async def test_list_datasets_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.list_datasets.side_effect = ValueError("Permission denied")

    # Call the tool and expect error
    error_msg = "Error executing tool list_datasets: Permission denied"
    with pytest.raises(ToolError, match=error_msg):
        await server.call_tool("list_datasets", {})


@pytest.mark.asyncio
async def test_list_tables_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.list_tables.side_effect = ValueError("Dataset not found")

    # Call the tool and expect error
    error_msg = "Error executing tool list_tables: Dataset not found"
    with pytest.raises(ToolError, match=error_msg):
        await server.call_tool(
            "list_tables",
            {"dataset_id": "non_existent_dataset"}
        )


@pytest.mark.asyncio
async def test_execute_query_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.execute_query.side_effect = ValueError("Invalid query")

    # Call the tool and expect error
    error_msg = "Error executing tool execute_query: Invalid query"
    with pytest.raises(ToolError, match=error_msg):
        await server.call_tool(
            "execute_query",
            {"query": "INVALID SQL"}
        )