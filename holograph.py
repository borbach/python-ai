#!/usr/bin/env python3
"""
3D Holographic AI Companion System
Creates an animated 3D hologram from photos and enables AI conversations
"""

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import numpy as np
import cv2
from PIL import Image, ImageTk
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import speech_recognition as sr
import pyttsx3
import requests
import base64
from datetime import datetime
import math
import random

class HolographicCompanion:
    def __init__(self):
        # Initialize components
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Person data
        self.person_name = ""
        self.photos = []
        self.voice_recordings = []
        self.personality_data = {
            'likes': [],
            'dislikes': [],
            'personality_traits': [],
            'conversation_style': 'friendly',
            'interests': []
        }
        
        # 3D and animation data
        self.face_mesh = None
        self.texture = None
        self.animation_frame = 0
        self.is_speaking = False
        self.current_emotion = 'neutral'
        
        # Voice and AI components
        self.speech_recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # OpenGL/Pygame setup
        self.screen_width = 800
        self.screen_height = 600
#        self.screen_width = 1900
#        self.screen_height = 1000
        self.screen = None
        
        # Conversation history
        self.conversation_history = []
        
        print("🎭 Holographic AI Companion System Initialized")
    
    def setup_person_profile(self):
        """Setup the person's profile and preferences"""
        print("\n=== PERSON PROFILE SETUP ===")
        
        # Get person's name
        self.person_name = simpledialog.askstring("Setup", "Enter the person's name:")
        if not self.person_name:
            print("No name provided. Exiting...")
            return False
        
        print(f"Setting up profile for: {self.person_name}")
        
        # Collect photos
        if not self.collect_photos():
            return False
        
        # Collect personality data
        if not self.collect_personality_data():
            return False
        
        # Collect voice recordings (optional)
        self.collect_voice_recordings()
        
        # Save profile
        self.save_profile()
        
        return True
    
    def collect_photos(self):
        """Collect multiple photos of the person"""
        print("\n📸 Photo Collection")
        print("Please select 3-10 photos of the person from different angles")
        
        while len(self.photos) < 10:
            file_path = filedialog.askopenfilename(
                title=f"Select photo {len(self.photos) + 1} (or cancel to finish)",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
            )
            
            if not file_path:
                break
                
            if self.process_photo(file_path):
                self.photos.append(file_path)
                print(f"✓ Added photo {len(self.photos)}: {os.path.basename(file_path)}")
            else:
                print(f"✗ Could not process photo: {os.path.basename(file_path)}")
        
        if len(self.photos) < 3:
            messagebox.showerror("Error", "Need at least 3 photos to create hologram")
            return False
        
        print(f"Collected {len(self.photos)} photos")
        return True
    
    def process_photo(self, photo_path):
        """Process and validate a photo"""
        try:
            # Load image
            img = cv2.imread(photo_path)
            if img is None:
                return False
            
            # Detect faces to ensure photo contains a person
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return len(faces) > 0
            
        except Exception as e:
            print(f"Error processing photo: {e}")
            return False
    
    def collect_personality_data(self):
        """Collect personality and preference data"""
        print("\n🧠 Personality Data Collection")
        
        # Likes
        likes_input = simpledialog.askstring(
            "Personality", 
            f"What does {self.person_name} like? (comma-separated):\nExample: music, reading, coffee, hiking"
        )
        if likes_input:
            self.personality_data['likes'] = [item.strip() for item in likes_input.split(',')]
        
        # Dislikes
        dislikes_input = simpledialog.askstring(
            "Personality", 
            f"What does {self.person_name} dislike? (comma-separated):\nExample: loud noises, spicy food, crowds"
        )
        if dislikes_input:
            self.personality_data['dislikes'] = [item.strip() for item in dislikes_input.split(',')]
        
        # Personality traits
        traits_input = simpledialog.askstring(
            "Personality", 
            f"Describe {self.person_name}'s personality traits (comma-separated):\nExample: funny, intelligent, caring, creative"
        )
        if traits_input:
            self.personality_data['personality_traits'] = [item.strip() for item in traits_input.split(',')]
        
        # Conversation style
        style_options = ["friendly", "formal", "casual", "witty", "intellectual"]
        style_input = simpledialog.askstring(
            "Personality", 
            f"How does {self.person_name} typically communicate?\nOptions: {', '.join(style_options)}"
        )
        if style_input and style_input.lower() in style_options:
            self.personality_data['conversation_style'] = style_input.lower()
        
        return True
    
    def collect_voice_recordings(self):
        """Collect voice recordings (optional)"""
        print("\n🎤 Voice Recording Collection (Optional)")
        
        record_choice = messagebox.askyesno(
            "Voice Recordings", 
            "Would you like to record some voice samples?\nThis will help make the hologram's voice more authentic."
        )
        
        if not record_choice:
            return
        
        for i in range(3):
            if messagebox.askyesno("Recording", f"Record voice sample {i+1}?\nSpeak for 5-10 seconds."):
                self.record_voice_sample(f"voice_sample_{i+1}")
    
    def record_voice_sample(self, filename):
        """Record a voice sample"""
        try:
            print(f"Recording {filename}... Speak now!")
            with self.microphone as source:
                self.speech_recognizer.adjust_for_ambient_noise(source)
                audio = self.speech_recognizer.listen(source, timeout=1, phrase_time_limit=10)
            
            # Save audio file
            with open(f"{filename}.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            self.voice_recordings.append(f"{filename}.wav")
            print(f"✓ Recorded {filename}")
            
        except Exception as e:
            print(f"Error recording voice: {e}")
    
    def create_3d_model(self):
        """Create 3D model from photos"""
        print("\n🎯 Creating 3D Holographic Model...")
        
        # This is a simplified version - in practice, you'd use photogrammetry
        # or AI-based 3D reconstruction techniques
        
        # For now, we'll create a textured plane that can be animated
        self.create_face_geometry()
        self.create_texture_from_photos()
        
        print("✓ 3D Model created")
    
    def create_face_geometry(self):
        """Create basic face geometry for the hologram"""
        # Create a simple face mesh (in practice, this would be much more complex)
        self.face_mesh = {
            'vertices': [
                [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],  # Face quad
                [-0.3, 0.2, 0.1], [0.3, 0.2, 0.1],  # Eyes
                [0, -0.3, 0.1],  # Mouth
            ],
            'faces': [
                [0, 1, 2], [0, 2, 3],  # Main face
            ],
            'texture_coords': [
                [0, 0], [1, 0], [1, 1], [0, 1]
            ]
        }
    
    def create_texture_from_photos(self):
        """Create texture from the collected photos"""
        if not self.photos:
            return
        
        # Use the first photo as the primary texture
        # In practice, you'd blend multiple photos for better results
        primary_photo = cv2.imread(self.photos[0])
        primary_photo = cv2.cvtColor(primary_photo, cv2.COLOR_BGR2RGB)
        
        # Resize to power of 2 for OpenGL
        self.texture = cv2.resize(primary_photo, (256, 256))
    
    def setup_3d_display(self):
        """Setup the 3D holographic display"""
        pygame.init()
        
        # Setup display
        display = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption(f"Holographic {self.person_name}")
        
        # Setup OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        
        # Setup perspective
        gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        
        # Setup lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        
        # Load texture
        if self.texture is not None:
            self.load_texture()
    
    def load_texture(self):
        """Load texture into OpenGL"""
        texture_data = pygame.image.fromstring(
            self.texture.tobytes(), self.texture.shape[:2][::-1], 'RGB'
        )
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB, 
            self.texture.shape[1], self.texture.shape[0], 
            0, GL_RGB, GL_UNSIGNED_BYTE, 
            pygame.image.tostring(texture_data, 'RGB')
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        return texture_id
    
    def render_hologram(self):
        """Render the 3D hologram"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Apply rotation for holographic effect
        rotation_y = math.sin(time.time()) * 10
        glRotatef(rotation_y, 0, 1, 0)
        
        # Apply speaking animation
        if self.is_speaking:
            mouth_movement = math.sin(time.time() * 10) * 0.1
            glTranslatef(0, mouth_movement, 0)
        
        # Apply emotion-based transformations
        self.apply_emotion_effects()
        
        # Render the face
        glBegin(GL_QUADS)
        for i, vertex in enumerate(self.face_mesh['vertices'][:4]):
            glTexCoord2f(*self.face_mesh['texture_coords'][i])
            glVertex3f(*vertex)
        glEnd()
        
        # Add holographic effects
        self.add_holographic_effects()
        
        pygame.display.flip()
    
    def apply_emotion_effects(self):
        """Apply visual effects based on current emotion"""
        if self.current_emotion == 'happy':
            # Slight upward curve
            glScalef(1.0, 1.05, 1.0)
        elif self.current_emotion == 'sad':
            # Slight downward effect
            glScalef(1.0, 0.95, 1.0)
        elif self.current_emotion == 'excited':
            # Pulsing effect
            scale = 1.0 + math.sin(time.time() * 5) * 0.05
            glScalef(scale, scale, scale)
    
    def add_holographic_effects(self):
        """Add holographic visual effects"""
        # Add scan lines
        glDisable(GL_TEXTURE_2D)
        glColor4f(0.0, 1.0, 1.0, 0.3)
        
        for i in range(0, 20):
            y_pos = -2 + (i * 0.2) + math.sin(time.time() + i) * 0.1
            glBegin(GL_LINES)
            glVertex3f(-2, y_pos, 0.01)
            glVertex3f(2, y_pos, 0.01)
            glEnd()
        
        # Add flickering effect
        flicker = random.random() * 0.1
        glColor4f(1.0 + flicker, 1.0 + flicker, 1.0 + flicker, 1.0)
        glEnable(GL_TEXTURE_2D)
    
    def setup_ai_backend(self):
        """Setup AI conversation backend"""
        print("\n🤖 Setting up AI Backend...")
        
        # Create personality prompt for Claude
        self.create_personality_prompt()
        
        print("✓ AI Backend ready")
    
    def create_personality_prompt(self):
        """Create a personality prompt for the AI based on collected data"""
        likes_str = ", ".join(self.personality_data['likes'])
        dislikes_str = ", ".join(self.personality_data['dislikes'])
        traits_str = ", ".join(self.personality_data['personality_traits'])
        
        self.personality_prompt = f"""You are having a conversation as if you were {self.person_name}. 
        
        Here's what you should know about {self.person_name}:
        
        Likes: {likes_str}
        Dislikes: {dislikes_str}
        Personality traits: {traits_str}
        Communication style: {self.personality_data['conversation_style']}
        
        Respond as {self.person_name} would, incorporating their interests and personality. 
        Be conversational and engaging. Keep responses relatively brief (1-3 sentences) 
        unless asked for more detail.
        
        Remember: You are {self.person_name}, so speak in first person about their likes, 
        experiences, and opinions."""
    
    def get_ai_response(self, user_message):
        """Get AI response from Claude API"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Prepare messages for Claude API
            messages = [
                {"role": "user", "content": self.personality_prompt}
            ] + self.conversation_history
            
            # Call Claude API (using the built-in fetch capability)
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "messages": messages
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["content"][0]["text"]
                
                # Add AI response to conversation history
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                return "I'm having trouble connecting right now. Could you try again?"
                
        except Exception as e:
            print(f"AI Error: {e}")
            return "Sorry, I couldn't process that right now."
    
    def speak_text(self, text):
        """Convert text to speech"""
        try:
            self.is_speaking = True
            
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to select a voice that matches the person's characteristics
                self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.setProperty('rate', 180)  # Speaking rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            self.is_speaking = False
            
        except Exception as e:
            print(f"Speech error: {e}")
            self.is_speaking = False
    
    def listen_for_speech(self):
        """Listen for user speech input"""
        try:
            print("🎤 Listening...")
            with self.microphone as source:
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.speech_recognizer.listen(source, timeout=1, phrase_time_limit=10)
            
            print("Processing speech...")
            text = self.speech_recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def determine_emotion(self, text):
        """Determine emotion from text for animation"""
        text_lower = text.lower()
        
        # Simple emotion detection based on keywords
        if any(word in text_lower for word in ['happy', 'great', 'awesome', 'love', 'excited']):
            return 'happy'
        elif any(word in text_lower for word in ['sad', 'sorry', 'bad', 'terrible', 'awful']):
            return 'sad'
        elif any(word in text_lower for word in ['wow', 'amazing', 'incredible', 'fantastic']):
            return 'excited'
        else:
            return 'neutral'
    
    def conversation_loop(self):
        """Main conversation loop"""
        print(f"\n💬 Starting conversation with {self.person_name}...")
        print("Say 'goodbye' or press Ctrl+C to exit")
        
        # Greet the user
        greeting = f"Hello! I'm {self.person_name}. How are you today?"
        print(f"{self.person_name}: {greeting}")
        self.speak_text(greeting)
        
        try:
            while True:
                # Listen for user input
                user_input = self.listen_for_speech()
                
                if user_input:
                    print(f"You: {user_input}")
                    
                    # Check for exit commands
                    if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit']):
                        farewell = f"Goodbye! It was nice talking with you."
                        print(f"{self.person_name}: {farewell}")
                        self.speak_text(farewell)
                        break
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_input)
                    print(f"{self.person_name}: {ai_response}")
                    
                    # Update emotion based on response
                    self.current_emotion = self.determine_emotion(ai_response)
                    
                    # Speak the response
                    self.speak_text(ai_response)
                
                else:
                    # No speech detected, continue listening
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nConversation ended.")
    
    def run_hologram_display(self):
        """Run the hologram display loop"""
        clock = pygame.time.Clock()
        
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                
                self.render_hologram()
                clock.tick(60)  # 60 FPS
                
        except Exception as e:
            print(f"Display error: {e}")
    
    def save_profile(self):
        """Save the person's profile data"""
        profile_data = {
            'name': self.person_name,
            'photos': self.photos,
            'voice_recordings': self.voice_recordings,
            'personality': self.personality_data,
            'created': datetime.now().isoformat()
        }
        
        filename = f"{self.person_name.lower().replace(' ', '_')}_profile.json"
        with open(filename, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        print(f"✓ Profile saved as {filename}")
    
    def load_profile(self):
        """Load an existing profile"""
        profile_file = filedialog.askopenfilename(
            title="Load Profile",
            filetypes=[("Profile files", "*.json")]
        )
        
        if profile_file:
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                
                self.person_name = profile_data['name']
                self.photos = profile_data['photos']
                self.voice_recordings = profile_data.get('voice_recordings', [])
                self.personality_data = profile_data['personality']
                
                print(f"✓ Loaded profile for {self.person_name}")
                return True
                
            except Exception as e:
                print(f"Error loading profile: {e}")
                return False
        
        return False
    
    def run(self):
        """Main program loop"""
        print("🌟 Welcome to the 3D Holographic AI Companion System")
        print("="*60)
        
        # Ask if user wants to load existing profile or create new
        choice = messagebox.askyesnocancel(
            "Profile Setup", 
            "Do you want to:\n\nYes - Load existing profile\nNo - Create new profile\nCancel - Exit"
        )
        
        if choice is None:  # Cancel
            return
        elif choice:  # Yes - Load existing
            if not self.load_profile():
                return
        else:  # No - Create new
            if not self.setup_person_profile():
                return
        
        # Create 3D model
        self.create_3d_model()
        
        # Setup AI backend
        self.setup_ai_backend()
        
        # Setup 3D display
        self.setup_3d_display()
        
        print(f"\n🎭 {self.person_name} is now ready for conversation!")
        
        # Start conversation thread
        conversation_thread = threading.Thread(target=self.conversation_loop)
        conversation_thread.daemon = True
        conversation_thread.start()
        
        # Run hologram display (this will block until window is closed)
        self.run_hologram_display()
        
        print("\nHolographic companion shutting down...")

def main():
    """Main entry point"""
    try:
        companion = HolographicCompanion()
        companion.run()
        
    except ImportError as e:
        print("Error: Required libraries not found.")
        print("Please install required packages with:")
        print("pip install opencv-python pillow pygame PyOpenGL SpeechRecognition pyttsx3 requests numpy")
        print("\nAdditional system requirements:")
        print("- PyAudio: pip install pyaudio")
        print("- For Linux: sudo apt-get install python3-pyaudio portaudio19-dev")
        print("- For macOS: brew install portaudio")
    except Exception as e:
        print(f"Error starting holographic companion: {e}")

if __name__ == "__main__":
    main()

