from typing import Any, Dict, List, Optional
from google.cloud import bigquery
from google.api_core import exceptions


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
                    "full_dataset_id": f"{self.project_id}.{dataset.dataset_id}",
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
                    "full_table_id": f"{self.project_id}.{dataset_id}.{table.table_id}",
                    "schema": schema,
                    "num_rows": table_obj.num_rows,
                    "created": table_obj.created.isoformat() if table_obj.created else None,
                })
            return result
        except exceptions.NotFound:
            raise ValueError(f"Dataset {dataset_id} not found")
        except exceptions.PermissionDenied:
            raise ValueError(f"Permission denied to access dataset {dataset_id}")
        except Exception as e:
            raise ValueError(f"Failed to list tables: {str(e)}")

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            query_job = self.client.query(query)
            results = query_job.result()

            # Convert results to a list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # Convert non-serializable types to strings
                    if isinstance(value, (bytes, bytearray)):
                        value = value.hex()
                    row_dict[key] = value
                rows.append(row_dict)

            return {
                "rows": rows,
                "total_rows": len(rows),
                "schema": [
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                    }
                    for field in results.schema
                ],
            }
        except exceptions.BadRequest as e:
            raise ValueError(f"Invalid query: {str(e)}")
        except exceptions.PermissionDenied:
            raise ValueError("Permission denied to execute query")
        except Exception as e:
            raise ValueError(f"Failed to execute query: {str(e)}")