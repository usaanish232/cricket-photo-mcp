import os
import re
import json
import requests
import uvicorn
from bs4 import BeautifulSoup
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Mount
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CricketPhotoFinder")

def fetch_web_images(player_name: str, limit: int = 3) -> list:
    query = f"{player_name} cricketer match photo"
    url = "https://bing.com"
    params = {"q": query, "form": "HDRSC2", "first": 1}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
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
        return [f"Error fetching image: {str(e)}"]

@mcp.tool()
def get_player_photo(player_name: str) -> str:
    """Finds up to 3 high-quality web photo URLs for any international cricket player."""
    photos = fetch_web_images(player_name, limit=3)
    if not photos:
        return f"No photos found for {player_name}"
    return "\n".join(photos)

async def home(request):
    return PlainTextResponse("Cricket Photo Finder (Web Image Search) is LIVE and Working!")

async def test_search(request):
    player = request.query_params.get("player", "Virat Kohli")
    photos = fetch_web_images(player, limit=3)
    return PlainTextResponse(f"Photos for {player}:\n" + "\n".join(photos))

app = Starlette(routes=[
    Route("/", home),
    Route("/test", test_search),
    Mount("/", app=mcp.streamable_http_app())
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
