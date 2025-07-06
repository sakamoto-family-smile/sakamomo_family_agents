from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_tools(session: ClientSession):
    """Test all available tools"""
    # List available tools
    tools = await session.list_tools()
    print("\n=== Available Tools ===")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    # Test echo tool
    print("\n=== Testing Echo Tool ===")
    echo_result = await session.call_tool("echo", {"message": "Hello MCP!"})
    print(f"Echo response: {echo_result}")

    # Test get_current_time tool
    print("\n=== Testing Current Time Tool ===")
    time_result = await session.call_tool("get_current_time", {})
    print(f"Current time: {time_result}")


async def test_resources(session: ClientSession):
    """Test all available resources"""
    # List available resources
    resources = await session.list_resources()
    print("\n=== Available Resources ===")
    for resource in resources:
        print(f"- {resource.uri}")

    # Test version resource
    print("\n=== Testing Version Resource ===")
    version_content = await session.read_resource("config://version")
    print(f"Version: {version_content}")


async def main():
    # Connect to the MCP server running as HTTP server
    print("Connecting to MCP server...")
    async with streamablehttp_client("http://localhost:8080/mcp") as (read, write, _):
        # Create a session using the client streams
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected successfully!")

            # Test tools
            await test_tools(session)

            # Test resources
            await test_resources(session)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
