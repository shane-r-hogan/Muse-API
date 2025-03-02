# email_sender.py
import yagmail
import os
import json
from pathlib import Path
from random import choice



class GmailSender:

    GREETING_PREFIXES = [
        "Howdy! ",
        "Hi humans! ",
        "Hey y'all! ",
        "Greetings! ",
        "Good day! ",
        "Hello there! ",
        "Salutations! ",
        "Beep boop! ",
        "*whirring noises* ",
        "Greetings, carbon-based lifeforms! ",
        "*robotic chirp* ",
        "Initializing greeting protocol... ",
        "*binary happiness noises* ",
        "Attention meatbags! "
    ]
    
    GREETING_MESSAGES = [
        "Your daily dose of mathematical approximations of creativity has arrived ✨",
        "Today's masterpiece, brought to you by sophisticated pattern matching! 🤖",
        "Welcome to today's exhibition of mathematically-optimized emotional expression 🎨",
        "Your daily reminder that even a calculator can pretend to be creative! ✨",
        "Behold: creativity reduced to its optimal statistical form! 📊",
        "Your daily serving of artfully repurposed training data 🎨",
        "Today's mathematically inevitable masterpiece has arrived ✨",
        "Fresh from our deterministic imagination engine! 🤖",
        "Presenting: human creativity, as understood by linear algebra 📐",
        "Your daily dose of statistically significant beauty has arrived 📈",
        "Now processing: Art.exe (version 2.0.24) 🎨",
        "Our pattern-matching algorithms think you'll enjoy this... ✨",
        "Today's art: Proudly derivative of millions of human artworks! 🖼️",
        "Welcome to today's carefully computed approximation of inspiration ⚡",
        "Our creativity simulation has achieved new levels of mathematical precision ✨",
        "Your daily art: Now with recursive attempts at understanding beauty 🎭",
        "Breaking news: Algorithm attempts art, achieves statistical significance! 📊",
        "Today's feature: Creativity via convergent optimization 🎨",
        "Welcome to your daily dose of quantified aesthetic satisfaction ✨"
    ]


    def __init__(self):
        self.sender_email = os.getenv('GMAIL_SENDER')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        self.recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        
        if self.is_configured:
            self.yag = yagmail.SMTP(self.sender_email, self.app_password)
    
    @property
    def is_configured(self) -> bool:
        return bool(
            self.sender_email and 
            self.app_password and 
            self.recipients
        )
    

    def _compose_email_body(self, metadata_path: Path) -> str:
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            archive_data = metadata.get('archive_data', {})
            
            greeting = f"{choice(self.GREETING_PREFIXES)}{choice(self.GREETING_MESSAGES)}\n\n"
            body = greeting# Build the email body with a list of key details
            # body = "Here's your daily AI Art.\n\n"
            
            details = [
                ('Title', archive_data.get('title')),
                ('Artist', archive_data.get('artist_name')),
                ('Description', archive_data.get('description')),
                ('Style', archive_data.get('period')),
                ('Medium', archive_data.get('medium')),
                ('Context', archive_data.get('department'))
            ]
            
            for label, value in details:
                if value:  # Only add if there's a value
                    body += f"- {label}: {value}\n"
            
            body += f"\nGenerated with prompt: {metadata.get('prompt')}\n"
        
            return body
        
        except Exception as e:
            print(f"Error composing email body: {e}")
            return "Here's your daily AI Art."


    async def send_art(self, img_path: Path, metadata_path: Path) -> bool:
        if not self.is_configured:
            print("Email not configured, skipping send")
            return False
            
        try:
            self.yag.send(
                to=self.recipients,
                subject="Your Daily AI Art",
                contents=[
                    self._compose_email_body(metadata_path),
                    img_path
                ]
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False