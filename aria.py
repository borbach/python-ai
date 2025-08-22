#!/usr/bin/env python3
"""
Advanced Python Chatbot
Features: Chat, Creative Writing, Calculations, File Reading, Weather, Time
"""

OPENAI_API_KEY="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"
GOOGLE_API_KEY="AIzaSyB1oM5l4kKIiqsGy-k2jUnC-FiF0VQ7F6s"
GEMINI_API_KEY="AIzaSyB1oM5l4kKIiqsGy-k2jUnC-FiF0VQ7F6s"
OPENWEATHER_API_KEY="5e8089fba040eee46d43da8676c5750a"
ANTHROPIC_API_KEY="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"
STABILITY_API_KEY="sk-XEvNJLDdswcfu8KZh6Lz17BLd1EwGiSAMqEsTEzQGB7ZpJ2q"

import subprocess
import os
import json
import re
import math
import requests
import docx
import PyPDF2
from datetime import datetime
import pytz
from typing import Dict, List, Any
import subprocess
import tempfile
import sqlite3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class AdvancedChatbot:
    def __init__(self):
        self.name = "Assistant"
        self.conversation_history = []
        self.user_name = "User"
        self.setup_database()
        self.weather_api_key = None
        self.claude_api_key = None
        self.openai_api_key = None
        self.stability_api_key = None
        
        # Initialize APIs
        self.setup_apis()
        
    def setup_apis(self):
        """Setup API keys"""
        print("🔧 API Setup")
        print("="*50)
        
        # Weather API (OpenWeatherMap - free)
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.weather_api_key:
            self.weather_api_key = OPENWEATHER_API_KEY
        if not self.weather_api_key:
            print("⚠️  For weather features, get a free API key from:")
            print("   https://openweathermap.org/api")
            weather_key = input("Enter OpenWeatherMap API key (or press Enter to skip): ").strip()
            if weather_key:
                self.weather_api_key = weather_key
        
        # Claude API for advanced responses
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.claude_api_key:
            self.claude_api_key = ANTHROPIC_API_KEY
        if not self.claude_api_key:
            claude_key = input("Enter Anthropic API key (or press Enter for basic mode): ").strip()
            if claude_key:
                self.claude_api_key = claude_key
        
        # OpenAI API for DALL-E image generation
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            self.openai_api_key = OPENAI_API_KEY
        if not self.openai_api_key:
            print("⚠️  For AI image generation, get an API key from:")
            print("   https://platform.openai.com/api-keys")
            openai_key = input("Enter OpenAI API key (or press Enter to skip): ").strip()
            if openai_key:
                self.openai_api_key = openai_key
        self.openai_api_key = "" 
        
        # Stability AI for Stable Diffusion (alternative image generation)
        self.stability_api_key = os.getenv('STABILITY_API_KEY')
        if not self.stability_api_key:
            stability_key = input("Enter Stability AI API key (or press Enter to skip): ").strip()
            if stability_key:
                self.stability_api_key = stability_key
    
    def setup_database(self):
        """Setup SQLite database for conversation history"""
        self.db_path = "chatbot_history.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                bot_response TEXT,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                filepath TEXT,
                summary TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT,
                filepath TEXT,
                method TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_input: str, bot_response: str):
        """Save conversation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = datetime.now().strftime("%Y%m%d")
        cursor.execute('''
            INSERT INTO conversations (timestamp, user_input, bot_response, session_id)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_input, bot_response, session_id))
        
        conn.commit()
        conn.close()
    
    def call_claude_api(self, message: str, mode: str = "chat") -> str:
        """Call Claude API for advanced responses"""
        if not self.claude_api_key:
            return self.generate_basic_response(message, mode)
        
        system_prompts = {
            "chat": "You are a helpful, friendly AI assistant. Provide clear, informative responses.",
            "creative": "You are a creative writing assistant. Write engaging, imaginative content with rich descriptions and compelling narratives.",
            "academic": "You are an academic writing assistant. Provide well-structured, formal, and informative essays with proper analysis."
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.claude_api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user", 
                            "content": f"{system_prompts.get(mode, system_prompts['chat'])}\n\nUser: {message}"
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['content'][0]['text']
            else:
                return f"API Error: {response.status_code}"
                
        except Exception as e:
            return f"Connection Error: {str(e)}"
    
    def generate_basic_response(self, message: str, mode: str = "chat") -> str:
        """Generate basic responses without API"""
        message_lower = message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return f"Hello {self.user_name}! How can I help you today?"
        
        # Creative writing triggers
        if mode == "creative" or any(word in message_lower for word in ['story', 'write', 'creative', 'essay', 'poem']):
            return "I'd love to help with creative writing! However, for the best creative content, please set up the Claude API key. In basic mode, I can provide writing tips and structure guidance."
        
        # Question responses
        if message_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            return "That's an interesting question! For detailed answers, I recommend setting up the Claude API key for more comprehensive responses."
        
        # Default response
        return "I understand you're asking about that topic. For more detailed and helpful responses, please consider setting up the Claude API key."
    
    def perform_calculation(self, expression: str) -> str:
        """Perform mathematical calculations"""
        try:
            # Replace common math expressions
            expression = expression.replace('^', '**')  # Power operator
            expression = expression.replace('sqrt', 'math.sqrt')
            expression = expression.replace('sin', 'math.sin')
            expression = expression.replace('cos', 'math.cos')
            expression = expression.replace('tan', 'math.tan')
            expression = expression.replace('log', 'math.log')
            expression = expression.replace('pi', 'math.pi')
            expression = expression.replace('e', 'math.e')
            
            # Safe evaluation
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"📊 Calculation Result: {result}"
            
        except Exception as e:
            return f"❌ Calculation Error: {str(e)}"
    
    def read_text_file(self, filepath: str) -> str:
        """Read text files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def read_pdf_file(self, filepath: str) -> str:
        """Read PDF files"""
        try:
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def read_docx_file(self, filepath: str) -> str:
        """Read Word documents"""
        try:
            doc = docx.Document(filepath)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def read_and_summarize_file(self, filepath: str) -> str:
        """Read and summarize files"""
        if not os.path.exists(filepath):
            return f"❌ File not found: {filepath}"
        
        file_ext = Path(filepath).suffix.lower()
        
        # Read file based on extension
        if file_ext == '.pdf':
            content = self.read_pdf_file(filepath)
        elif file_ext == '.docx':
            content = self.read_docx_file(filepath)
        elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            content = self.read_text_file(filepath)
        else:
            return f"❌ Unsupported file type: {file_ext}"
        
        if "Error" in content:
            return content
        
        # Truncate if too long
        if len(content) > 5000:
            content = content[:5000] + "...(truncated)"
        
        # Generate summary
        filename = Path(filepath).name
        summary_prompt = f"Please summarize this document '{filename}':\n\n{content}"
        summary = self.call_claude_api(summary_prompt, "academic")
        
        # Save to database
        self.save_file_summary(filename, filepath, summary)
        
        return f"📄 File Summary for '{filename}':\n\n{summary}"
    
    def generate_image_dalle(self, prompt: str) -> str:
        """Generate image using OpenAI DALL-E"""
        if not self.openai_api_key:
            return "❌ OpenAI API key not configured for DALL-E image generation"
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "size": "1024x1024",
                    "quality": "standard",
                    "n": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data['data'][0]['url']
                
                # Download and save image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    # Create images directory if it doesn't exist
                    os.makedirs("generated_images", exist_ok=True)
                    
                    # Save image with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"dalle_{timestamp}.png"
                    filepath = os.path.join("generated_images", filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Save to database
                    self.save_generated_image(prompt, filepath, "DALL-E")
                    
                    return f"🎨 Image generated successfully!\n📁 Saved to: {filepath}\n✨ Method: DALL-E 3"
                else:
                    return "❌ Failed to download generated image"
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                return f"❌ DALL-E Error: {error_msg}"
                
        except Exception as e:
            return f"❌ DALL-E Generation Error: {str(e)}"
    
    def generate_image_stability(self, prompt: str) -> str:
        """Generate image using Stability AI"""
        if not self.stability_api_key:
            return "❌ Stability AI API key not configured"
        
        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.stability_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Create images directory
                os.makedirs("generated_images", exist_ok=True)
                
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stability_{timestamp}.png"
                filepath = os.path.join("generated_images", filename)
                
                # Decode and save image
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Save to database
                self.save_generated_image(prompt, filepath, "Stability AI")
                
                return f"🎨 Image generated successfully!\n📁 Saved to: {filepath}\n✨ Method: Stability AI"
            else:
                return f"❌ Stability AI Error: {response.status_code}"
                
        except Exception as e:
            return f"❌ Stability AI Generation Error: {str(e)}"
    
    def generate_simple_image(self, prompt: str) -> str:
        """Generate simple image using matplotlib (offline method)"""
        try:
            # Create images directory
            os.makedirs("generated_images", exist_ok=True)
            
            # Parse prompt for simple drawings
            prompt_lower = prompt.lower()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 8)
            ax.set_aspect('equal')
            
            # Simple shape detection and drawing
            if 'circle' in prompt_lower:
                circle = patches.Circle((5, 4), 2, linewidth=2, edgecolor='blue', facecolor='lightblue')
                ax.add_patch(circle)
                ax.text(5, 1, 'Circle', ha='center', fontsize=14)
                
            elif 'square' in prompt_lower or 'rectangle' in prompt_lower:
                rectangle = patches.Rectangle((3, 2), 4, 3, linewidth=2, edgecolor='red', facecolor='lightcoral')
                ax.add_patch(rectangle)
                ax.text(5, 1, 'Rectangle', ha='center', fontsize=14)
                
            elif 'triangle' in prompt_lower:
                triangle = patches.Polygon([(5, 6), (3, 2), (7, 2)], closed=True, 
                                         linewidth=2, edgecolor='green', facecolor='lightgreen')
                ax.add_patch(triangle)
                ax.text(5, 1, 'Triangle', ha='center', fontsize=14)
                
            elif 'house' in prompt_lower:
                # Draw a simple house
                house_base = patches.Rectangle((3, 2), 4, 3, linewidth=2, edgecolor='brown', facecolor='wheat')
                roof = patches.Polygon([(3, 5), (5, 7), (7, 5)], closed=True, 
                                     linewidth=2, edgecolor='red', facecolor='red')
                door = patches.Rectangle((4.5, 2), 1, 2, linewidth=2, edgecolor='black', facecolor='brown')
                
                ax.add_patch(house_base)
                ax.add_patch(roof)
                ax.add_patch(door)
                ax.text(5, 0.5, 'House', ha='center', fontsize=14)
                
            elif 'flower' in prompt_lower:
                # Draw a simple flower
                center = patches.Circle((5, 4), 0.3, linewidth=2, edgecolor='yellow', facecolor='yellow')
                petals = []
                for angle in range(0, 360, 45):
                    x = 5 + 1.2 * np.cos(np.radians(angle))
                    y = 4 + 1.2 * np.sin(np.radians(angle))
                    petal = patches.Circle((x, y), 0.5, linewidth=1, edgecolor='pink', facecolor='pink')
                    petals.append(petal)
                
                for petal in petals:
                    ax.add_patch(petal)
                ax.add_patch(center)
                
                # Stem
                ax.plot([5, 5], [2.5, 4], 'g-', linewidth=4)
                ax.text(5, 1, 'Flower', ha='center', fontsize=14)
                
            else:
                # Default: colorful abstract art
                colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
                for i in range(6):
                    x = 2 + (i % 3) * 2
                    y = 3 + (i // 3) * 2
                    circle = patches.Circle((x, y), 0.8, linewidth=1, 
                                          edgecolor=colors[i], facecolor=colors[i], alpha=0.7)
                    ax.add_patch(circle)
                ax.text(5, 1, 'Abstract Art', ha='center', fontsize=14)
            
            ax.set_title(f'Generated Image: {prompt}', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_{timestamp}.png"
            filepath = os.path.join("generated_images", filename)
            
            plt.savefig(filepath, bbox_inches='tight', dpi=150, facecolor='white')
            plt.close()
            
            # Save to database
            self.save_generated_image(prompt, filepath, "Simple Drawing")
            
            return f"🎨 Simple image generated!\n📁 Saved to: {filepath}\n✨ Method: Simple Drawing (Offline)"
            
        except Exception as e:
            return f"❌ Simple image generation error: {str(e)}"
    
    def generate_text_art(self, text: str) -> str:
        """Generate text-based art image"""
        try:
            # Create images directory
            os.makedirs("generated_images", exist_ok=True)
            
            # Create image with PIL
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 60)
                small_font = ImageFont.truetype("arial.ttf", 30)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)  # macOS
                    small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
            
            # Draw colorful background
            colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200)]
            for i in range(4):
                x1 = (i % 2) * width // 2
                y1 = (i // 2) * height // 2
                x2 = x1 + width // 2
                y2 = y1 + height // 2
                draw.rectangle([x1, y1, x2, y2], fill=colors[i])
            
            # Draw text in center
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text with shadow
            draw.text((x+3, y+3), text, fill='gray', font=font)
            draw.text((x, y), text, fill='black', font=font)
            
            # Add decorative border
            draw.rectangle([10, 10, width-10, height-10], outline='black', width=5)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"textart_{timestamp}.png"
            filepath = os.path.join("generated_images", filename)
            
            img.save(filepath)
            
            # Save to database
            self.save_generated_image(f"Text Art: {text}", filepath, "Text Art")
            
            return f"🎨 Text art generated!\n📁 Saved to: {filepath}\n✨ Method: Text Art"
            
        except Exception as e:
            return f"❌ Text art generation error: {str(e)}"
    
    def save_generated_image(self, prompt: str, filepath: str, method: str):
        """Save generated image info to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_images (prompt, filepath, method, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (prompt, filepath, method, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def save_file_summary(self, filename: str, filepath: str, summary: str):
        """Save  file summary to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO files_summary (filename, filepath, summary, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (filename, filepath, summary, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

    def generate_image(self, prompt: str) -> str:
        """Main image generation function with multiple methods"""
        print(f"🎨 Generating image: '{prompt}'...")
        
        # Try different methods in order of preference
        if self.openai_api_key:
            print("🤖 Using DALL-E 3...")
            return self.generate_image_dalle(prompt)
        elif self.stability_api_key:
            print("🎨 Using Stability AI...")
            return self.generate_image_stability(prompt)
        else:
            # Check if it's a simple drawing request
            simple_keywords = ['circle', 'square', 'triangle', 'rectangle', 'house', 'flower']
            if any(keyword in prompt.lower() for keyword in simple_keywords):
                print("✏️ Using simple drawing method...")
                return self.generate_simple_image(prompt)
            else:
                print("📝 Using text art method...")
                # Extract main text from prompt
                text = prompt.replace('draw', '').replace('create', '').replace('make', '').strip()
                if len(text) > 20:
                    text = text[:20] + "..."
                return self.generate_text_art(text)
    
    def show_generated_images(self):
        """Show history of generated images"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt, filepath, method, timestamp 
            FROM generated_images 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        images = cursor.fetchall()
        conn.close()
        
        if images:
            print("\n🖼️ RECENT GENERATED IMAGES")
            print("="*60)
            for prompt, filepath, method, timestamp in images:
                time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                exists = "✅" if os.path.exists(filepath) else "❌"
                print(f"{exists} [{time_str}] {method}")
                print(f"    Prompt: {prompt}")
                print(f"    File: {filepath}")
                print("-" * 40)
        else:
            print("🖼️ No generated images found.")
        """Save file summary to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO files_summary (filename, filepath, summary, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (filename, filepath, summary, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_weather(self, city: str) -> str:
        """Get weather information"""
        if not self.weather_api_key:
            return "❌ Weather API key not configured. Get one free from https://openweathermap.org/api"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_info = f"🌤️ Weather in {data['name']}, {data['sys']['country']}:\n"
                weather_info += f"   🌡️  Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)\n"
                weather_info += f"   📊 Condition: {data['weather'][0]['description'].title()}\n"
                weather_info += f"   💧 Humidity: {data['main']['humidity']}%\n"
                weather_info += f"   💨 Wind: {data['wind']['speed']} m/s\n"
                weather_info += f"   👁️  Visibility: {data.get('visibility', 'N/A')} meters\n"
                
                return weather_info
            else:
                return f"❌ Weather Error: {response.json().get('message', 'City not found')}"
                
        except Exception as e:
            return f"❌ Weather Error: {str(e)}"
    
    def get_time_in_city(self, city: str) -> str:
        """Get current time in a city"""
        try:
            # Common timezone mappings
            timezone_mapping = {
                'new york': 'America/New_York',
                'london': 'Europe/London',
                'paris': 'Europe/Paris',
                'tokyo': 'Asia/Tokyo',
                'sydney': 'Australia/Sydney',
                'los angeles': 'America/Los_Angeles',
                'chicago': 'America/Chicago',
                'moscow': 'Europe/Moscow',
                'mumbai': 'Asia/Kolkata',
                'dubai': 'Asia/Dubai',
                'singapore': 'Asia/Singapore',
                'hong kong': 'Asia/Hong_Kong',
                'berlin': 'Europe/Berlin',
                'madrid': 'Europe/Madrid',
                'rome': 'Europe/Rome'
            }
            
            city_lower = city.lower()
            timezone = timezone_mapping.get(city_lower)
            
            if timezone:
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz)
                
                time_info = f"🕒 Current time in {city.title()}:\n"
                time_info += f"   📅 Date: {current_time.strftime('%A, %B %d, %Y')}\n"
                time_info += f"   ⏰ Time: {current_time.strftime('%I:%M:%S %p')}\n"
                time_info += f"   🌍 Timezone: {timezone}\n"
                
                return time_info
            else:
                available_cities = ", ".join(timezone_mapping.keys())
                return f"❌ Timezone not found for '{city}'. Available cities: {available_cities}"
                
        except Exception as e:
            return f"❌ Time Error: {str(e)}"
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent"""
        message_lower = message.lower()
        
        # File operations
        if any(word in message_lower for word in ['read file', 'summarize', 'open file', 'analyze file','list file']):
            print( "Here is a list of files in the current directory" )
            os.system( "ls" )
            return 'file_operation'
        
        # Calculations
        if any(char in message for char in ['+', '-', '*', '/', '=', '^']) or \
           any(word in message_lower for word in ['calculate', 'math', 'solve', 'compute']):
            return 'calculation'
        
        # Weather
        if any(word in message_lower for word in ['weather', 'temperature', 'forecast', 'climate']):
            return 'weather'
        
        # Time
        if any(word in message_lower for word in ['time', 'clock', 'current time', 'what time']):
            return 'time'
        
        # Creative writing
        if any(word in message_lower for word in ['write', 'story', 'essay', 'creative', 'poem', 'article']):
            return 'creative'
        
        # Image generation
        if any(word in message_lower for word in ['draw', 'create image', 'generate image', 'make picture', 'paint']):
            return 'image_generation'
        
        # Default chat
        return 'chat'
    
    def process_message(self, message: str) -> str:
        """Process user message and generate response"""
        intent = self.detect_intent(message)
        
        if intent == 'file_operation':
            # Extract file path
            words = message.split()
            filepath = None
            for word in words:
                if '.' in word and ('/' in word or '\\' in word or os.path.exists(word)):
                    filepath = word
                    break
            
            if not filepath:
                return "📁 Please specify a file path. Example: 'read file /path/to/document.pdf'"
            
            return self.read_and_summarize_file(filepath)
        
        elif intent == 'calculation':
            # Extract mathematical expression
            expression = message
            for word in ['calculate', 'compute', 'solve', 'math', 'what is', 'whats']:
                expression = expression.replace(word, '', 1).strip()
            
            return self.perform_calculation(expression)
        
        elif intent == 'weather':
            # Extract city name - improved to handle multi-word cities
            message_lower = message.lower()
            city = None
            
            # Look for "in [city]" pattern
            if ' in ' in message_lower:
                city_part = message_lower.split(' in ')[-1].strip()
                # Remove punctuation and get full city name
                city = city_part.rstrip('?.,!').strip()
            else:
                # Look for city names after weather-related words
                words = message_lower.split()
                weather_words = ['weather', 'temperature', 'forecast', 'climate']
                for i, word in enumerate(words):
                    if word in weather_words and i + 1 < len(words):
                        # Get remaining words as city name
                        city = ' '.join(words[i+1:]).rstrip('?.,!').strip()
                        break
            
            if not city:
                return "🌤️ Please specify a city. Example: 'weather in London' or 'what's the weather in Tokyo?'"
            
            return self.get_weather(city)
        
        elif intent == 'time':
            # Extract city name - improved to handle multi-word cities
            message_lower = message.lower()
            city = None
            
            if ' in ' in message_lower:
                city_part = message_lower.split(' in ')[-1].strip()
                # Remove any trailing punctuation
                city = city_part.rstrip('?.,!').strip()
            else:
                # Look for city names after time-related words
                words = message_lower.split()
                time_words = ['time', 'clock', 'current']
                for i, word in enumerate(words):
                    if word in time_words and i + 1 < len(words):
                        # Get remaining words as city name
                        city = ' '.join(words[i+1:]).rstrip('?.,!').strip()
                        break
            
            if not city:
                return "🕒 Please specify a city. Example: 'time in New York' or 'what time is it in Tokyo?'"
            
            return self.get_time_in_city(city)
        
        elif intent == 'image_generation':
            # Extract image description
            prompt = message
            # Remove trigger words to get clean description
            trigger_words = ['draw', 'create image', 'generate image', 'make picture', 'paint', 'create', 'make']
            for word in trigger_words:
                prompt = prompt.replace(word, '', 1).strip()
            
            if not prompt:
                return "🎨 Please describe what you want me to draw. Example: 'draw a sunset over mountains'"
            
            return self.generate_image(prompt)
        
        elif intent == 'creative':
            return self.call_claude_api(message, "creative")
        
        else:
            return self.call_claude_api(message, "chat")
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🤖 ADVANCED CHATBOT ASSISTANT")
        print("="*60)
        print("🎯 Features:")
        print("   💬 Natural conversation")
        print("   ✍️  Creative writing & essays")
        print("   🧮 Mathematical calculations")
        print("   📄 File reading & summarization")
        print("   🌤️ Weather information")
        print("   🕒 World time zones")
        print("   🎨 Image generation & drawing")
        print("="*60)
        print("📝 Examples:")
        print("   'Write a story about space exploration'")
        print("   'Calculate 15 * 67 + sqrt(144)'")
        print("   'Read file /path/to/document.pdf'")
        print("   'Weather in London'")
        print("   'What time is it in Tokyo?'")
        print("   'Draw a beautiful sunset over mountains'")
        print("="*60)
        print("💡 Commands: 'help', 'history', 'images', 'clear', 'quit'")
        print("="*60)
    
    def display_help(self):
        """Display help information"""
        print("\n🆘 HELP GUIDE")
        print("="*50)
        print("🔧 SETUP:")
        print("   pip install requests PyPDF2 python-docx pytz")
        print("   Get free weather API: https://openweathermap.org/api")
        print("   Get Claude API: https://console.anthropic.com/")
        print("\n💬 CHAT EXAMPLES:")
        print("   'Hello, how are you?'")
        print("   'Tell me about artificial intelligence'")
        print("\n✍️  CREATIVE WRITING:")
        print("   'Write a short story about robots'")
        print("   'Create an essay about climate change'")
        print("   'Write a poem about friendship'")
        print("\n🧮 CALCULATIONS:")
        print("   'Calculate 25 * 4 + 15'")
        print("   'What is sqrt(144) + pi'")
        print("   'Solve 2^8'")
        print("\n📄 FILE OPERATIONS:")
        print("   'Read file C:\\\\Users\\\\document.pdf'")
        print("   'Summarize /home/user/report.docx'")
        print("   'Analyze file data.txt'")
        print("\n🌤️ WEATHER:")
        print("   'Weather in New York'")
        print("   'What's the temperature in London?'")
        print("\n🕒 TIME:")
        print("   'Time in Tokyo'")
        print("   'What time is it in Paris?'")
        print("\n🎨 IMAGE GENERATION:")
        print("   'Draw a cat sitting on a chair'")
        print("   'Create image of a futuristic city'")
        print("   'Paint a beautiful landscape'")
        print("   'Generate a simple circle' (offline)")
        print("   'Make text art saying Hello' (offline)")
        print("="*50)
    
    def show_history(self):
        """Show conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_input, bot_response 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        history = cursor.fetchall()
        conn.close()
        
        if history:
            print("\n📚 RECENT CONVERSATION HISTORY")
            print("="*50)
            for timestamp, user_input, bot_response in reversed(history):
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                print(f"[{time_str}] You: {user_input}")
                print(f"[{time_str}] Bot: {bot_response[:100]}...")
                print("-" * 30)
        else:
            print("📚 No conversation history found.")
    
    def run(self):
        """Main chatbot loop"""
        self.display_welcome()
        
        # Get user name
        name = input("\nWhat's your name? ").strip()
        if name:
            self.user_name = name
        
        print(f"\nHello {self.user_name}! I'm ready to help. Type 'help' for guidance or 'quit' to exit.")
        
        while True:
            try:
                user_input = input(f"\n{self.user_name}: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'quit':
                    print(f"👋 Goodbye {self.user_name}! Thanks for chatting!")
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                elif user_input.lower() == 'images':
                    self.show_generated_images()
                    continue
                elif user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                # Process message
                print(f"\n{self.name}: ", end="", flush=True)
                response = self.process_message(user_input)
                print(response)
                
                # Save conversation
                self.save_conversation(user_input, response)
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye {self.user_name}!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")

def main():
    """Main function"""
    try:
        chatbot = AdvancedChatbot()
        chatbot.run()
    except Exception as e:
        print(f"❌ Failed to start chatbot: {e}")
        print("Make sure you have installed required packages:")
        print("pip install requests PyPDF2 python-docx pytz pillow matplotlib numpy")

if __name__ == "__main__":
    main()

