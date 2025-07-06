from fastmcp import Client
import asyncio


async def main():
    # Connect to the local BigQuery MCP server
    # Using stdio transport since we're testing locally
    async with Client("python -m bigquery_server.server") as client:
        try:
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {tools}")

            # Example query to test the server
            query = """
            SELECT
                repository_name,
                COUNT(*) as commit_count
            FROM `bigquery-public-data.github_repos.commits`
            GROUP BY repository_name
            ORDER BY commit_count DESC
            LIMIT 5
            """

            # Call the query tool
            result = await client.call_tool(
                "execute_query",
                {"query": query}  # project_id is set in server environment
            )

            print("\nQuery Results:")
            print(result.data["results"])

            # List available datasets
            datasets = await client.call_tool("list_datasets")
            print("\nAvailable Datasets:")
            for dataset in datasets.data["datasets"]:
                print(f"- {dataset['dataset_id']}")

        except Exception as e:
            print(f"Error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())