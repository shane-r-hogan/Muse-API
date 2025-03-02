import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from art_generator import ArtGenerator
from email_sender import GmailSender

async def main():
    try:
        generator = ArtGenerator(openai_api_key=os.getenv('OPENAI_API_KEY'))
        img_path, meta_path = await generator.generate()
        if img_path and meta_path:
            print(f"Generated: {img_path}")
            print(f"Metadata: {meta_path}")

            if os.getenv("SEND_EMAIL").upper()=="TRUE":
                sender = GmailSender()
                if await sender.send_art(img_path, meta_path):
                    print("Art sent successfully via email")
                    
        else:
            print("Generation attempt failed.")

    except asyncio.CancelledError:
        print("Shutting down gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process interrupted. Exiting...")
