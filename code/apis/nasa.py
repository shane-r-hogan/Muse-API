from dataclasses import dataclass
from typing import Optional
import random
import aiohttp

@dataclass
class NASAItem:
    title: str
    date: str
    description: str
    keywords: list[str]
    nasa_id: str
    media_type: str

    def get_prompt_elements(self) -> dict[str, str | list[str]]:
        return {
            "title": self.title,
            "description": self.description[:200],
            "subjects": self.keywords
        }

    @classmethod
    def from_api_response(cls, item: dict) -> 'NASAItem':
        return cls(
            title=item.get('title', 'Unknown Title'),
            date=item.get('date_created', 'Unknown Date'),
            description=item.get('description', 'No description available.'),
            keywords=item.get('keywords', []),
            nasa_id=item.get('nasa_id', 'Unknown ID'),
            media_type=item.get('media_type', 'Unknown')
        )

class NASADataFetcher:
    API_URL = "https://images-api.nasa.gov/search"

    async def get_random_item(self) -> Optional[NASAItem]:
        params = {
            'q': random.choice(["galaxy", "mars", "satellite", "nebula", "earth", "astronaut"]),  # Ensuring variety
            'media_type': 'image',
            'page': random.randint(1, 4),
            # 'api_key':os.getenv('NASA_API_KEY')
        }

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.API_URL, params=params, headers=headers) as response:
                    if response.status != 200:
                        print(f"[ERROR] NASA API failed with status {response.status}")
                        print(response)
                        print(f"[DEBUG] Request URL: {response.url}")
                        return None
                    
                    data = await response.json()
                    if 'collection' not in data or 'items' not in data['collection']:
                        print("[ERROR] Unexpected NASA API response format.")
                        return None
                    
                    items = data['collection']['items']
                    if not items:
                        print("[ERROR] No results found from NASA API.")
                        print(f"[DEBUG] Request URL: {response.url}")
                        return None
                    
                    selected_item = random.choice(items)
                    metadata = selected_item.get("data", [{}])[0]  # Extracting metadata
                    
                    return NASAItem.from_api_response(metadata)

        except Exception as e:
            print(f"[ERROR] Exception fetching NASA data: {e}")
            return None
