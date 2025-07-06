from fastmcp import Client
import asyncio


def inspect_object(obj, prefix=""):
    """Recursively inspect an object's attributes."""
    if hasattr(obj, "__dict__"):
        print(f"{prefix}Object attributes:")
        for key, value in obj.__dict__.items():
            print(f"{prefix}- {key}: {value}")
            if hasattr(value, "__dict__"):
                inspect_object(value, prefix + "  ")
    else:
        print(f"{prefix}Value: {obj}")


async def main():
    # Connect to the local BigQuery MCP server using HTTP transport
    server_url = "http://localhost:8080/mcp"
    async with Client(server_url) as client:
        try:
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {tools}")

            # List available datasets first
            print("\nFetching available datasets...")
            datasets_result = await client.call_tool("list_datasets")
            print("\nInspecting response object:")
            inspect_object(datasets_result)

            # Extract datasets from the response
            try:
                content = datasets_result.structured_content or {}
                datasets = content.get("datasets", [])
            except Exception as e:
                print(f"Failed to parse datasets response: {e}")
                datasets = []

            print("\nAvailable Datasets:")
            for dataset in datasets:
                dataset_id = dataset["dataset_id"]
                full_id = dataset["full_dataset_id"]
                print(f"- {dataset_id} ({full_id})")

            # After seeing the available datasets, we can create a proper query
            if datasets:
                # Get the first dataset for testing
                dataset = datasets[0]
                dataset_id = dataset["dataset_id"]
                print(f"\nFetching tables from dataset: {dataset_id}")
                tables_result = await client.call_tool(
                    "list_tables",
                    {"dataset_id": dataset_id}
                )
                print("\nInspecting tables response:")
                inspect_object(tables_result)

                # Extract tables from the response
                try:
                    content = tables_result.structured_content or {}
                    tables = content.get("tables", [])
                except Exception as e:
                    print(f"Failed to parse tables response: {e}")
                    tables = []

                print("\nTables in dataset:")
                for table in tables:
                    print(
                        f"- {table['table_id']} "
                        f"({table['full_table_id']})"
                    )
                    print("  Rows:", table['num_rows'])
                    print("  Schema:")
                    for field in table['schema']:
                        print(
                            f"    - {field['name']} "
                            f"({field['type']}, {field['mode']})"
                        )

                # Now that we have table information, let's run a query
                if tables:
                    table = tables[0]
                    table_id = table["full_table_id"]
                    print(f"\nExecuting sample query on {table_id}")
                    query = f"""
                    SELECT *
                    FROM `{table_id}`
                    LIMIT 5
                    """
                    query_result = await client.call_tool(
                        "execute_query",
                        {"query": query}
                    )
                    print("\nInspecting query response:")
                    inspect_object(query_result)

                    # Extract results from the response
                    try:
                        results = query_result.structured_content or {}
                    except Exception as e:
                        print(f"Failed to parse query response: {e}")
                        results = {}

                    print("\nQuery Results:")
                    total_rows = results.get('total_rows', 0)
                    rows = results.get('rows', [])
                    print(f"Total rows: {total_rows}")
                    print("Rows:")
                    for row in rows:
                        print(row)

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())