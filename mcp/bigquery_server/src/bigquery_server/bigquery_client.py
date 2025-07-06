from typing import Any, Dict, List, Optional
from google.cloud import bigquery
from google.api_core import exceptions


def serialize_value(value: Any) -> Any:
    """Convert non-serializable types to strings."""
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if hasattr(value, "isoformat"):  # datetime, date, time objects
        return value.isoformat()
    return value


class BigQueryClient:
    def __init__(self, project_id: Optional[str] = None):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id or self.client.project

    async def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in the project."""
        try:
            datasets = list(self.client.list_datasets())
            return [
                {
                    "dataset_id": dataset.dataset_id,
                    "friendly_name": dataset.friendly_name,
                    "full_dataset_id": (
                        f"{self.project_id}.{dataset.dataset_id}"
                    ),
                }
                for dataset in datasets
            ]
        except exceptions.PermissionDenied:
            raise ValueError("Permission denied to access datasets")
        except Exception as e:
            raise ValueError(f"Failed to list datasets: {str(e)}")

    async def list_tables(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List all tables in a dataset with their schemas."""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            tables = list(self.client.list_tables(dataset_ref))

            result = []
            for table in tables:
                table_obj = self.client.get_table(table)
                schema = [
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                        "description": field.description,
                    }
                    for field in table_obj.schema
                ]

                result.append({
                    "table_id": table.table_id,
                    "full_table_id": (
                        f"{self.project_id}.{dataset_id}.{table.table_id}"
                    ),
                    "schema": schema,
                    "num_rows": table_obj.num_rows,
                    "created": serialize_value(table_obj.created),
                })
            return result
        except exceptions.NotFound:
            raise ValueError(f"Dataset {dataset_id} not found")
        except exceptions.PermissionDenied:
            msg = f"Permission denied to access dataset {dataset_id}"
            raise ValueError(msg)
        except Exception as e:
            raise ValueError(f"Failed to list tables: {str(e)}")

    async def get_table_schema(
        self, dataset_id: str, table_id: str
    ) -> Dict[str, Any]:
        """Get schema for a specific table."""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)

            schema = [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description,
                }
                for field in table.schema
            ]

            return {
                "table_id": table.table_id,
                "full_table_id": (
                    f"{self.project_id}.{dataset_id}.{table.table_id}"
                ),
                "schema": schema,
                "num_rows": table.num_rows,
                "created": serialize_value(table.created),
            }
        except exceptions.NotFound:
            raise ValueError(
                f"Table {dataset_id}.{table_id} not found"
            )
        except exceptions.PermissionDenied:
            raise ValueError(
                f"Permission denied to access table {dataset_id}.{table_id}"
            )
        except Exception as e:
            raise ValueError(f"Failed to get table schema: {str(e)}")

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a SQL query and return results with optional pagination."""
        try:
            job_config = bigquery.QueryJobConfig()

            # Set query parameters if provided
            if params:
                job_config.query_parameters = [
                    bigquery.ScalarQueryParameter(
                        name,
                        self._get_param_type(value),
                        value
                    )
                    for name, value in params.items()
                ]

            query_job = self.client.query(query, job_config=job_config)

            # Handle pagination
            if page_size:
                results = query_job.result(
                    page_size=page_size,
                    start_index=0 if not page_token else int(page_token)
                )
                next_token = str(
                    int(page_token or 0) + page_size
                ) if len(list(results.pages)) > 1 else None
            else:
                results = query_job.result()
                next_token = None

            # Convert results to a list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    row_dict[key] = serialize_value(value)
                rows.append(row_dict)

            return {
                "rows": rows,
                "total_rows": results.total_rows,
                "schema": [
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                    }
                    for field in results.schema
                ],
                "next_page_token": next_token,
            }
        except exceptions.BadRequest as e:
            raise ValueError(f"Invalid query: {str(e)}")
        except exceptions.PermissionDenied:
            raise ValueError("Permission denied to execute query")
        except Exception as e:
            raise ValueError(f"Failed to execute query: {str(e)}")

    def _get_param_type(self, value: Any) -> str:
        """Get BigQuery parameter type based on Python value type."""
        if isinstance(value, bool):
            return "BOOL"
        elif isinstance(value, int):
            return "INT64"
        elif isinstance(value, float):
            return "FLOAT64"
        elif isinstance(value, str):
            return "STRING"
        elif hasattr(value, "isoformat"):  # datetime, date objects
            return "TIMESTAMP"
        else:
            return "STRING"  # Default to string for unknown types