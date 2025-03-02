import re
import os
import json
import time
import aiohttp
from datetime import datetime
from typing import Optional
from dataclasses import asdict
from pathlib import Path
from openai import AsyncOpenAI

from apis.nasa import NASADataFetcher
from apis.met import MetDataFetcher


class ArtGenerator: 
    PROMPT_SYSTEM_MESSAGE = """
    You are a creative prompt engineer specializing in visual art generation.
    Given historical archive information, create an engaging and detailed DALL-E prompt.
    Focus on visual elements, artistic style, and mood while incorporating historical context.
    Keep prompts concise but descriptive, under 200 characters.
    """

    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=openai_api_key) 
        script_dir = Path(__file__).parent.parent.absolute()
        self.data_dir = script_dir / "data"
        self.nasa_fetcher = NASADataFetcher()
        self.met_fetcher = MetDataFetcher()

    
    def _get_save_directory(self) -> Path:
        now = datetime.now()
        save_dir = self.data_dir / f"{now.year}_{now.strftime('%b')}_{now.day}" / f"{now.strftime('%H_%M')}"
        save_dir.mkdir(parents=True, exist_ok=True)  # This is equivalent to os.makedirs with exist_ok=True
        return save_dir

    def _get_image_name(self, item, time_of_day) -> str:
        elements = item.get_prompt_elements()
        title = elements.get('title')
        clean_title = re.sub(r'[^\w\s-]', '', title).strip()
        title = clean_title.replace(" ", "_").lower()
        return f"{time_of_day}_{title}"


    def _get_time_of_day(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12: 
            return "morning"
        if 12 <= hour < 17: 
            return "afternoon"
        if 17 <= hour < 20: 
            return "sunset"
        return "night"


    async def _generate_prompt(self, item, time_of_day: str) -> str:
        try:
            elements = item.get_prompt_elements()
            
            element_str = "\n".join([
                f"- {key.title()}: {value if isinstance(value, str) else ', '.join(value)}"
                for key, value in elements.items()
            ])

            print(element_str)

            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {"role": "system", "content": self.PROMPT_SYSTEM_MESSAGE},
                    {"role": "user", "content": f"""
                    Create a DALL-E prompt based on:
                    {element_str}
                    - Time of day: {time_of_day}
                    """}
                ],
                max_tokens=100
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating prompt: {e}")
            return f"A {time_of_day} scene inspired by {item.title}, artistic style"


    async def generate(self) -> tuple[Optional[Path], Optional[Path]]:
        fetcher = self.met_fetcher
        item = await fetcher.get_random_item()
        
        if not item:
            print("[ERROR] No item retrieved. Stopping generation.")
            return None
        
        if os.getenv('DEBUG_MODE', '').upper() == 'TRUE':
            input("[DEBUG] Press Enter to continue to prompt generation...")

        time_of_day = self._get_time_of_day()
        prompt = await self._generate_prompt(item, time_of_day) if item else f"A {time_of_day} scene, trending on artstation, highly detailed"
        
        print(f"Generating with prompt: {prompt}")
        
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            if not response.data or not response.data[0].url:
                print("Image generation failed: No valid response from OpenAI.")
                return None, None
            
        
            save_dir = self._get_save_directory()
            img_name = self._get_image_name(item, time_of_day)

            img_path = save_dir / f"{img_name}.png"
            meta_path = save_dir / f"{img_name}_metadata.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(response.data[0].url) as img_response:
                    if img_response.status == 200:
                        image_data = await img_response.read()
                        with open(img_path, "wb") as f:
                            f.write(image_data)
                    else:
                        print(f"Failed to download image: HTTP {img_response.status}")
                        return None, None
            
            metadata = {
                'timestamp': str(int(time.time())),
                'archive_data': asdict(item) if item else None,
                'prompt': prompt,
                'environmental_factors': {'time_of_day': time_of_day}
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return img_path, meta_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None, None
        

