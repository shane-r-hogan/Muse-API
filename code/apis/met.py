from dataclasses import dataclass
from typing import Optional
import random
import aiohttp

@dataclass
class MetItem:
    title: str
    date: str
    description: str
    department: str
    artist_name: str
    artist_bio: str
    culture: str
    period: str
    object_id: str
    image_url: str
    medium: str


    def get_prompt_elements(self) -> dict[str, str | list[str]]:
        return {
            "title": self.title,
            "description": self.description,
            "style": f"{self.culture} {self.period}".strip(),
            "artist": f"{self.artist_name} {self.artist_bio}",
            "medium": self.medium,
            "context": self.department
        }

    @classmethod
    def from_api_response(cls, item: dict) -> 'MetItem':
        return cls(
            title = item.get('title', ''),
            date = item.get('objectDate', ''),
            description = item.get('objectName', ''),
            department = item.get('department', ''),
            artist_name = item.get('artistDisplayName', ''),
            artist_bio = item.get('artistDisplayBio', ''),
            culture = item.get('culture', ''),
            period = item.get('period', ''),
            object_id = str(item.get('objectID', '')),
            image_url=f"https://images.metmuseum.org/CRDImages/ep/original/{item.get('primaryImage', '')}" if item.get('primaryImage') else '',
            medium=item.get('medium', '')
        )

class MetDataFetcher:
    OBJECTS_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
    
    async def get_random_item(self) -> Optional[MetItem]:
        # First, get the list of all object IDs with images
        params = {
            'hasImages': 'true'
        }
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get list of all object IDs
                async with session.get(self.OBJECTS_URL, params=params, headers=headers) as response:
                    if response.status != 200:
                        print(f"[ERROR] Met API failed with status {response.status}")
                        print(f"[DEBUG] Request URL: {response.url}")
                        return None
                    
                    data = await response.json()
                    if 'objectIDs' not in data or not data['objectIDs']:
                        print("[ERROR] No objects found in Met API response.")
                        return None
                    
                    # Get a random object ID
                    object_id = random.choice(data['objectIDs'])

                    # Get the specific object's details
                    async with session.get(self.OBJECT_URL.format(object_id), headers=headers) as obj_response:
                        if obj_response.status != 200:
                            print(f"[ERROR] Met API object fetch failed with status {obj_response.status}")
                            return None
                        
                        object_data = await obj_response.json()
                        
                        return MetItem.from_api_response(object_data)
                        
        except Exception as e:
            print(f"[ERROR] Exception fetching Met data: {e}")
            print(f"[DEBUG] Request URL: {response.url}")
            return None