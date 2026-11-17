import os
import json
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

port = int(os.environ.get("PORT", 10000))
mcp = FastMCP("CricketPhotoFinder", host="0.0.0.0", port=port)

def fetch_web_images(player_name: str, limit: int = 3) -> list:
    query = f"{player_name} cricketer match photo"
    search_url = "https://bing.com" + "/images/search"
    params = {"q": query, "form": "HDRSC2", "first": 1}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(search_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        image_urls = []
        for a in soup.find_all("a", class_="iusc"):
            m = a.get("m")
            if m:
                data = json.loads(m)
                img_url = data.get("murl")
                if img_url and img_url.startswith("http"):
                    image_urls.append(img_url)
                if len(image_urls) >= limit:
                    break
        return image_urls
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def get_player_photo(player_name: str) -> str:
    """Finds up to 3 high-quality web photo URLs for any international cricket player."""
    photos = fetch_web_images(player_name, limit=3)
    if not photos:
        return f"No photos found for {player_name}"
    return "\n".join(photos)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
