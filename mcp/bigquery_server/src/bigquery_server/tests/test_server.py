import os
import pytest
from unittest.mock import AsyncMock, patch

from bigquery_server.server import create_server
from bigquery_server.bigquery_client import BigQueryClient


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
            "dataset_id": "test_dataset",
            "friendly_name": "Test Dataset",
            "full_dataset_id": "project.test_dataset",
        }
    ]
    mock_bq_client.list_datasets.return_value = mock_datasets

    # Call the tool
    result = await server.call_tool(
        tool={"name": "list_datasets", "arguments": {}},
    )

    # Verify the result
    assert result == {"datasets": mock_datasets}
    mock_bq_client.list_datasets.assert_called_once()


@pytest.mark.asyncio
async def test_list_tables(server, mock_bq_client):
    # Prepare mock response
    mock_tables = [
        {
            "table_id": "test_table",
            "full_table_id": "project.dataset.test_table",
            "schema": [
                {
                    "name": "column1",
                    "type": "STRING",
                    "mode": "REQUIRED",
                    "description": "Test column",
                }
            ],
            "num_rows": 100,
            "created": "2024-01-01T00:00:00Z",
        }
    ]
    mock_bq_client.list_tables.return_value = mock_tables

    # Call the tool
    result = await server.call_tool(
        tool={"name": "list_tables", "arguments": {"dataset_id": "test_dataset"}},
    )

    # Verify the result
    assert result == {"tables": mock_tables}
    mock_bq_client.list_tables.assert_called_once_with("test_dataset")


@pytest.mark.asyncio
async def test_execute_query(server, mock_bq_client):
    # Prepare mock response
    mock_query_result = {
        "rows": [{"column1": "value1", "column2": 123}],
        "total_rows": 1,
        "schema": [
            {"name": "column1", "type": "STRING", "mode": "REQUIRED"},
            {"name": "column2", "type": "INTEGER", "mode": "REQUIRED"},
        ],
    }
    mock_bq_client.execute_query.return_value = mock_query_result

    # Call the tool
    result = await server.call_tool(
        tool={"name": "execute_query", "arguments": {"query": "SELECT * FROM test_dataset.test_table"}},
    )

    # Verify the result
    assert result == mock_query_result
    mock_bq_client.execute_query.assert_called_once_with(
        "SELECT * FROM test_dataset.test_table"
    )


@pytest.mark.asyncio
async def test_list_datasets_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.list_datasets.side_effect = ValueError("Permission denied")

    # Call the tool and expect error
    with pytest.raises(ValueError, match="Permission denied"):
        await server.call_tool(tool={"name": "list_datasets", "arguments": {}})


@pytest.mark.asyncio
async def test_list_tables_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.list_tables.side_effect = ValueError("Dataset not found")

    # Call the tool and expect error
    with pytest.raises(ValueError, match="Dataset not found"):
        await server.call_tool(
            tool={"name": "list_tables", "arguments": {"dataset_id": "nonexistent_dataset"}},
        )


@pytest.mark.asyncio
async def test_execute_query_error(server, mock_bq_client):
    # Mock error response
    mock_bq_client.execute_query.side_effect = ValueError("Invalid query")

    # Call the tool and expect error
    with pytest.raises(ValueError, match="Invalid query"):
        await server.call_tool(
            tool={"name": "execute_query", "arguments": {"query": "INVALID SQL"}},
        )