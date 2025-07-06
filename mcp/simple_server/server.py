from fastmcp import FastMCP

server = FastMCP("simple_mcp_server", host="0.0.0.0", port=8080)


@server.resource("config://version")
def get_version():
    return "1.0.0"


# 日時ツール追加
@server.tool()
def get_current_time() -> str:
    """現在の日時を取得するツール"""
    from datetime import datetime
    now = datetime.now()
    return f"現在の日時: {now.strftime('%Y-%m-%d %H:%M:%S')}"


# エコーツール定義
@server.tool()
def echo(message: str) -> str:
    """入力されたメッセージをそのまま返す簡単なツール"""
    return f"Echo: {message}"


if __name__ == "__main__":
    server.run(transport="http", path="/mcp")
