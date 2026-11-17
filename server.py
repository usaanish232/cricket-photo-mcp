import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CricketPhotoFinder")

@mcp.tool()
def get_player_photo(player_name: str) -> str:
    """Finds the official Wikipedia photo URL for a cricket player."""
    url = "https://wikipedia.org"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "titles": player_name,
        "pithumbsize": 800,
        "redirects": 1
    }
    headers = {"User-Agent": "CricketVideoBot/1.0"}
    response = requests.get(url, params=params, headers=headers).json()
    pages = response.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if "thumbnail" in page_data:
            return page_data["thumbnail"]["source"]
    return f"No photo found for {player_name}"

if __name__ == "__main__":
    mcp.run(transport="sse")
