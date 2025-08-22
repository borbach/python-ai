#!/usr/bin/env python3
"""
Minimal Holographic Persona Generator (Standard Library Only)
A system to create interactive AI personas using only Python standard library.
"""

import json
import sqlite3
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonalityProfile:
    """Data class to store personality characteristics"""
    name: str
    likes: List[str]
    dislikes: List[str]
    writing_style: Dict[str, Any]
    personality_traits: Dict[str, float]
    created_date: str

class MinimalHologramGenerator:
    """Minimal hologram generator with no external dependencies"""
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process image and create hologram data (basic file info only)"""
        try:
            # Get basic file information
            file_size = os.path.getsize(image_path)
            file_name = os.path.basename(image_path)
            
            # Create hologram data with basic info
            hologram_data = {
                'original_path': image_path,
                'file_name': file_name,
                'file_size': file_size,
                'has_face': True,  # Assume all images have faces
                'processed_date': datetime.now().isoformat()
            }
            
            return hologram_data
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

class PersonalityAnalyzer:
    """Analyzes and builds personality profiles"""
    
    def __init__(self):
        self.questions = [
            "What are your favorite hobbies or activities?",
            "What type of music do you enjoy?",
            "What foods do you love/hate?",
            "How do you prefer to spend your free time?",
            "What are your biggest pet peeves?",
            "What makes you feel most happy?",
            "What are your core values?",
            "How would friends describe your personality?",
            "What topics do you find most interesting?",
            "What are your biggest fears or concerns?"
        ]
    
    def analyze_writing_style(self, text_samples: List[str]) -> Dict[str, Any]:
        """Analyze writing style from text samples"""
        if not text_samples:
            return {}
        
        combined_text = " ".join(text_samples)
        words = combined_text.split()
        sentences = combined_text.split('.')
        
        if not words:
            return {}
        
        style_analysis = {
            'avg_word_length': sum(len(word) for word in words) / len(words),
            'avg_sentence_length': sum(len(sent.split()) for sent in sentences if sent.strip()) / max(len([s for s in sentences if s.strip()]), 1),
            'vocabulary_richness': len(set(words)) / len(words),
            'common_words': self._get_common_words(words),
            'punctuation_usage': self._analyze_punctuation(combined_text),
            'formality_level': self._assess_formality(combined_text),
            'total_words': len(words),
            'total_characters': len(combined_text)
        }
        
        return style_analysis
    
    def _get_common_words(self, words: List[str], top_n: int = 10) -> List[tuple]:
        """Get most common words"""
        word_freq = {}
        for word in words:
            word_lower = word.lower().strip('.,!?;:"')
            if word_lower and len(word_lower) > 2:  # Skip empty strings and very short words
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def _analyze_punctuation(self, text: str) -> Dict[str, int]:
        """Analyze punctuation usage patterns"""
        return {
            'exclamation': text.count('!'),
            'question': text.count('?'),
            'period': text.count('.'),
            'comma': text.count(','),
            'semicolon': text.count(';'),
            'ellipsis': text.count('...'),
            'quotation': text.count('"') + text.count("'")
        }
    
    def _assess_formality(self, text: str) -> str:
        """Assess formality level of writing"""
        formal_indicators = ['therefore', 'however', 'furthermore', 'consequently', 'moreover', 'nevertheless', 'accordingly']
        informal_indicators = ['yeah', 'gonna', 'wanna', 'kinda', 'sorta', 'lol', 'omg', 'btw', 'tbh']
        
        text_lower = text.lower()
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        informal_count = sum(1 for word in informal_indicators if word in text_lower)
        
        if formal_count > informal_count:
            return 'formal'
        elif informal_count > formal_count:
            return 'informal'
        else:
            return 'neutral'

class HolographicPersona:
    """Main class representing the interactive holographic persona"""
    
    def __init__(self, profile: PersonalityProfile, hologram_data: Dict[str, Any]):
        self.profile = profile
        self.hologram_data = hologram_data
        self.conversation_history = []
        self.response_patterns = self._build_response_patterns()
        
    def _build_response_patterns(self) -> Dict[str, List[str]]:
        """Build response patterns based on personality"""
        formality = self.profile.writing_style.get('formality_level', 'neutral')
        
        patterns = {
            'greetings': {
                'formal': ["Good day! How may I assist you today?", "Hello, it's a pleasure to speak with you.", "Greetings! What would you like to discuss?"],
                'informal': ["Hey there! What's up?", "Hi! Good to chat with you!", "Hello! How's it going?"],
                'neutral': ["Hello! How can I help you?", "Hi there! What's on your mind?", "Hello! What would you like to talk about?"]
            },
            'positive_responses': {
                'formal': ["That is quite fascinating.", "I find that rather intriguing.", "That's an excellent observation."],
                'informal': ["That's awesome!", "Cool stuff!", "I love that!"],
                'neutral': ["That's interesting.", "I like that.", "That sounds good."]
            },
            'questions': {
                'formal': ["Could you elaborate on that?", "What are your thoughts on this matter?", "How do you perceive this?"],
                'informal': ["Tell me more!", "What do you think?", "How do you feel about it?"],
                'neutral': ["Can you tell me more?", "What's your opinion?", "How do you see it?"]
            }
        }
        
        return patterns
    
    def generate_response(self, user_input: str) -> str:
        """Generate persona response based on personality and input"""
        user_input_lower = user_input.lower()
        formality = self.profile.writing_style.get('formality_level', 'neutral')
        
        # Check for greetings
        if any(greeting in user_input_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            import random
            return random.choice(self.response_patterns['greetings'][formality])
        
        # Check if input relates to likes
        for like in self.profile.likes:
            if like.lower() in user_input_lower:
                enthusiasm_responses = {
                    'formal': f"I must say, {like} is one of my greatest interests. I find it particularly engaging.",
                    'informal': f"Oh wow, I absolutely love {like}! It's one of my favorite things ever!",
                    'neutral': f"I really enjoy {like}. It's definitely one of my interests."
                }
                follow_up = {
                    'formal': " What aspects of it do you find most compelling?",
                    'informal': " What do you love most about it?",
                    'neutral': " What do you think about it?"
                }
                return enthusiasm_responses[formality] + follow_up[formality]
        
        # Check if input relates to dislikes
        for dislike in self.profile.dislikes:
            if dislike.lower() in user_input_lower:
                negative_responses = {
                    'formal': f"I must admit, {dislike} is not particularly to my liking. I tend to avoid it when possible.",
                    'informal': f"Ugh, {dislike} really isn't my thing. I try to stay away from it.",
                    'neutral': f"I'm not really into {dislike}. It's not for me."
                }
                return negative_responses[formality]
        
        # Check for questions
        if '?' in user_input:
            response_starters = {
                'formal': "That is an excellent question. ",
                'informal': "Great question! ",
                'neutral': "Good question. "
            }
            follow_ups = {
                'formal': "I believe this matter requires careful consideration. What is your perspective on it?",
                'informal': "I'd love to hear what you think about this! What's your take?",
                'neutral': "I'd like to hear your thoughts on this. What do you think?"
            }
            return response_starters[formality] + follow_ups[formality]
        
        # Default responses based on writing style
        avg_sentence_length = self.profile.writing_style.get('avg_sentence_length', 10)
        
        if avg_sentence_length > 20:  # Long sentences - detailed response
            responses = {
                'formal': "Your observation raises several interesting points that merit further discussion. I would be delighted to explore this topic with you in greater depth, as I believe there are multiple perspectives worth considering.",
                'informal': "That's really interesting stuff! I love talking about things like this, and I think there's so much we could dive into here. What got you thinking about this?",
                'neutral': "That's an interesting point. I think there's a lot we could discuss about this topic. I'd like to hear more about your thoughts on it."
            }
        else:  # Shorter sentences - concise response
            responses = {
                'formal': "I see. Please continue.",
                'informal': "Cool! Tell me more!",
                'neutral': "Interesting. What else?"
            }
        
        # Add to conversation history
        response = responses[formality]
        self.conversation_history.append({
            'user': user_input,
            'persona': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response

class PersonaDatabase:
    """Database manager for storing and retrieving personas"""
    
    def __init__(self, db_path: str = "personas.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                profile_data TEXT NOT NULL,
                hologram_data TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_persona(self, persona: HolographicPersona) -> None:
        """Save persona to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO personas (name, profile_data, hologram_data, created_date)
                VALUES (?, ?, ?, ?)
            ''', (
                persona.profile.name,
                json.dumps(asdict(persona.profile)),
                json.dumps(persona.hologram_data),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Persona '{persona.profile.name}' saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving persona: {e}")
            raise
        finally:
            conn.close()
    
    def load_persona(self, name: str) -> HolographicPersona:
        """Load persona from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT profile_data, hologram_data FROM personas WHERE name = ?', (name,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"Persona '{name}' not found")
            
            profile_data, hologram_data = result
            profile_dict = json.loads(profile_data)
            
            # Reconstruct PersonalityProfile
            profile = PersonalityProfile(**profile_dict)
            hologram_data = json.loads(hologram_data)
            
            return HolographicPersona(profile, hologram_data)
            
        except Exception as e:
            logger.error(f"Error loading persona: {e}")
            raise
        finally:
            conn.close()
    
    def list_personas(self) -> List[str]:
        """List all saved personas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM personas ORDER BY created_date DESC')
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error listing personas: {e}")
            return []
        finally:
            conn.close()

class MinimalPersonaApp:
    """Main application class with GUI (no external dependencies)"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minimal Holographic Persona Generator")
        self.root.geometry("900x700")
        
        self.hologram_gen = MinimalHologramGenerator()
        self.personality_analyzer = PersonalityAnalyzer()
        self.database = PersonaDatabase()
        
        self.current_persona = None
        self.selected_photo = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Create Persona
        create_frame = ttk.Frame(notebook)
        notebook.add(create_frame, text="Create Persona")
        self.setup_create_tab(create_frame)
        
        # Tab 2: Interact with Persona
        interact_frame = ttk.Frame(notebook)
        notebook.add(interact_frame, text="Chat")
        self.setup_interact_tab(interact_frame)
        
        # Tab 3: Manage Personas
        manage_frame = ttk.Frame(notebook)
        notebook.add(manage_frame, text="Manage")
        self.setup_manage_tab(manage_frame)
        
        # Tab 4: About
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="About")
        self.setup_about_tab(about_frame)
    
    def setup_create_tab(self, parent):
        """Setup the persona creation tab"""
        # Main scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Image upload section
        img_frame = ttk.LabelFrame(scrollable_frame, text="1. Select Photo", padding=10)
        img_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(img_frame, text="Choose Image File", 
                  command=self.select_photo).pack(side=tk.LEFT)
        self.photo_label = ttk.Label(img_frame, text="No photo selected")
        self.photo_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Personality section
        personality_frame = ttk.LabelFrame(scrollable_frame, text="2. Personality Profile", padding=10)
        personality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Name
        name_frame = ttk.Frame(personality_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="Name:", width=12).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, width=50)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Likes
        likes_frame = ttk.Frame(personality_frame)
        likes_frame.pack(fill=tk.X, pady=2)
        ttk.Label(likes_frame, text="Likes:", width=12).pack(side=tk.LEFT)
        self.likes_entry = tk.Entry(likes_frame, width=50)
        self.likes_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(personality_frame, text="(comma-separated: music, books, travel, etc.)", 
                 font=('Arial', 8)).pack(anchor=tk.W, padx=(90, 0))
        
        # Dislikes
        dislikes_frame = ttk.Frame(personality_frame)
        dislikes_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dislikes_frame, text="Dislikes:", width=12).pack(side=tk.LEFT)
        self.dislikes_entry = tk.Entry(dislikes_frame, width=50)
        self.dislikes_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Writing samples
        writing_frame = ttk.LabelFrame(scrollable_frame, text="3. Writing Sample", padding=10)
        writing_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(writing_frame, text="Paste a sample of text written by this person:").pack(anchor=tk.W)
        self.writing_text = tk.Text(writing_frame, height=8, wrap=tk.WORD)
        self.writing_text.pack(fill=tk.X, pady=5)
        
        # Personality traits
        traits_frame = ttk.LabelFrame(scrollable_frame, text="4. Personality Traits (Optional)", padding=10)
        traits_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create sliders for Big Five traits
        self.trait_vars = {}
        traits = [
            ("Extroversion", "How outgoing and social"),
            ("Openness", "How open to new experiences"),
            ("Conscientiousness", "How organized and disciplined"),
            ("Agreeableness", "How cooperative and trusting"),
            ("Neuroticism", "How anxious or emotional")
        ]
        
        for trait, description in traits:
            trait_row = ttk.Frame(traits_frame)
            trait_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(trait_row, text=f"{trait}:", width=15).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=0.5)
            self.trait_vars[trait.lower()] = var
            scale = tk.Scale(trait_row, from_=0.0, to=1.0, resolution=0.1, 
                           orient=tk.HORIZONTAL, variable=var, length=200)
            scale.pack(side=tk.LEFT)
            ttk.Label(trait_row, text=description, font=('Arial', 8)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Create persona button
        create_button = ttk.Button(scrollable_frame, text="Create Persona", 
                                 command=self.create_persona)
        create_button.pack(pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_interact_tab(self, parent):
        """Setup the interaction tab"""
        # Persona info
        info_frame = ttk.LabelFrame(parent, text="Current Persona", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.persona_info = ttk.Label(info_frame, text="No persona loaded", font=('Arial', 10, 'bold'))
        self.persona_info.pack()
        
        self.persona_details = ttk.Label(info_frame, text="", font=('Arial', 9))
        self.persona_details.pack()
        
        # Chat interface
        chat_frame = ttk.LabelFrame(parent, text="Conversation", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chat display with scrollbar
        chat_scroll_frame = ttk.Frame(chat_frame)
        chat_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        chat_scrollbar = ttk.Scrollbar(chat_scroll_frame)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Text(chat_scroll_frame, height=15, state=tk.DISABLED, 
                                   yscrollcommand=chat_scrollbar.set, wrap=tk.WORD,
                                   font=('Arial', 10))
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.config(command=self.chat_display.yview)
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(input_frame, text="You:").pack(side=tk.LEFT)
        self.chat_input = tk.Entry(input_frame, font=('Arial', 10))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.chat_input.bind('<Return>', self.send_message)
        
        ttk.Button(input_frame, text="Send", 
                  command=self.send_message).pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.Frame(chat_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(control_frame, text="Clear Chat", 
                  command=self.clear_chat).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Save Conversation", 
                  command=self.save_conversation).pack(side=tk.LEFT, padx=(5, 0))
    
    def setup_manage_tab(self, parent):
        """Setup the persona management tab"""
        # Persona list
        list_frame = ttk.LabelFrame(parent, text="Saved Personas", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox with scrollbar
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_scroll_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.persona_listbox = tk.Listbox(list_scroll_frame, yscrollcommand=list_scrollbar.set,
                                        font=('Arial', 10))
        self.persona_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.config(command=self.persona_listbox.yview)
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Load Persona", 
                  command=self.load_selected_persona).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="View Details", 
                  command=self.view_persona_details).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Delete Persona", 
                  command=self.delete_selected_persona).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.refresh_persona_list).pack(side=tk.RIGHT)
        
        self.refresh_persona_list()
    
    def setup_about_tab(self, parent):
        """Setup the about tab"""
        about_text = """
Minimal Holographic Persona Generator v1.0

This application creates interactive AI personas based on:
• Photo selection
• Personality traits (likes, dislikes)
• Writing style analysis
• Conversation patterns

Features:
• Create multiple personas
• Chat with personas
• Save/load persona profiles
• Personality-based responses
• No external dependencies (pure Python)

How to use:
1. Go to 'Create Persona' tab
2. Select a photo and fill in personality details
3. Click 'Create Persona'
4. Go to 'Chat' tab to interact with your persona
5. Use 'Manage' tab to switch between personas

The personas will respond based on their personality traits,
likes/dislikes, and writing style patterns.

Created with Python standard library only.
        """
        
        about_frame = ttk.Frame(parent)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        about_label = tk.Label(about_frame, text=about_text, justify=tk.LEFT, 
                              font=('Arial', 10), wraplength=600)
        about_label.pack()
    
    def select_photo(self):
        """Handle photo selection"""
        file_path = filedialog.askopenfilename(
            title="Select a photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            self.selected_photo = file_path
            filename = os.path.basename(file_path)
            self.photo_label.config(text=f"Selected: {filename}")
    
    def create_persona(self):
        """Create new persona from collected data"""
        try:
            # Validate inputs
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a name for the persona")
                return
                
            if not self.selected_photo:
                messagebox.showerror("Error", "Please select a photo")
                return
            
            likes_text = self.likes_entry.get().strip()
            dislikes_text = self.dislikes_entry.get().strip()
            writing_sample = self.writing_text.get(1.0, tk.END).strip()
            
            if not likes_text and not dislikes_text:
                messagebox.showerror("Error", "Please enter at least some likes or dislikes")
                return
            
            # Process image
            hologram_data = self.hologram_gen.process_image(self.selected_photo)
            
            # Parse likes and dislikes
            likes = [item.strip() for item in likes_text.split(',') if item.strip()]
            dislikes = [item.strip() for item in dislikes_text.split(',') if item.strip()]
            
            # Analyze writing style
            writing_samples = [writing_sample] if writing_sample else []
            writing_style = self.personality_analyzer.analyze_writing_style(writing_samples)
            
            # Get personality traits from sliders
            personality_traits = {trait: var.get() for trait, var in self.trait_vars.items()}
            
            # Create personality profile
            profile = PersonalityProfile(
                name=name,
                likes=likes,
                dislikes=dislikes,
                writing_style=writing_style,
                personality_traits=personality_traits,
                created_date=datetime.now().isoformat()
            )
            
            # Create persona
            persona = HolographicPersona(profile, hologram_data)
            
            # Save to database
            self.database.save_persona(persona)
            
            # Set as current persona
            self.current_persona = persona
            self._update_persona_display()
            
            messagebox.showinfo("Success", f"Persona '{name}' created successfully!")
            self.refresh_persona_list()
            
            # Clear form
            self.name_entry.delete(0, tk.END)
            self.likes_entry.delete(0, tk.END)
            self.dislikes_entry.delete(0, tk.END)
            self.writing_text.delete(1.0, tk.END)
            self.selected_photo = None
            self.photo_label.config(text="No photo selected")
            
            # Reset trait sliders to default
            for var in self.trait_vars.values():
                var.set(0.5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create persona: {e}")
    
    def load_selected_persona(self):
        """Load selected persona from list"""
        selection = self.persona_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a persona to load")
            return
        
        persona_name = self.persona_listbox.get(selection[0])
        
        try:
            self.current_persona = self.database.load_persona(persona_name)
            self._update_persona_display()
            messagebox.showinfo("Success", f"Loaded persona '{persona_name}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load persona: {e}")
    
    def view_persona_details(self):
        """View details of selected persona"""
        selection = self.persona_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a persona to view")
            return
        
        persona_name = self.persona_listbox.get(selection[0])
        
        try:
            persona = self.database.load_persona(persona_name)
            
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Persona Details: {persona_name}")
            details_window.geometry("500x600")
            
            # Create scrollable text widget
            text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
            scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Build details text
            details = f"Persona: {persona.profile.name}\n"
            details += f"Created: {persona.profile.created_date}\n\n"
            
            details += f"Likes ({len(persona.profile.likes)}):\n"
            for like in persona.profile.likes:
                details += f"  • {like}\n"
            
            details += f"\nDislikes ({len(persona.profile.dislikes)}):\n"
            for dislike in persona.profile.dislikes:
                details += f"  • {dislike}\n"
            
            details += f"\nPersonality Traits:\n"
            for trait, value in persona.profile.personality_traits.items():
                details += f"  • {trait.title()}: {value:.1f}\n"
            
            details += f"\nWriting Style Analysis:\n"
            style = persona.profile.writing_style
            if style:
                details += f"  • Average word length: {style.get('avg_word_length', 0):.1f}\n"
                details += f"  • Average sentence length: {style.get('avg_sentence_length', 0):.1f}\n"
                details += f"  • Vocabulary richness: {style.get('vocabulary_richness', 0):.2f}\n"
                details += f"  • Formality level: {style.get('formality_level', 'unknown')}\n"
                details += f"  • Total words analyzed: {style.get('total_words', 0)}\n"
                
                common_words = style.get('common_words', [])
                if common_words:
                    details += f"  • Common words: {', '.join([word for word, count in common_words[:5]])}\n"
            else:
                details += "  • No writing style data available\n"
            
            details += f"\nImage Information:\n"
            details += f"  • File: {persona.hologram_data.get('file_name', 'Unknown')}\n"
            details += f"  • Size: {persona.hologram_data.get('file_size', 0)} bytes\n"
            
            # Insert text and make read-only
            text_widget.insert(tk.END, details)
            text_widget.config(state=tk.DISABLED)
            
            # Pack widgets
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load persona details: {e}")
    
    def delete_selected_persona(self):
        """Delete selected persona"""
        selection = self.persona_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a persona to delete")
            return
        
        persona_name = self.persona_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{persona_name}'?\n\nThis action cannot be undone."):
            try:
                conn = sqlite3.connect(self.database.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM personas WHERE name = ?', (persona_name,))
                conn.commit()
                conn.close()
                
                self.refresh_persona_list()
                messagebox.showinfo("Success", f"Deleted persona '{persona_name}'")
                
                # Clear current persona if it was deleted
                if self.current_persona and self.current_persona.profile.name == persona_name:
                    self.current_persona = None
                    self._update_persona_display()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete persona: {e}")
    
    def _update_persona_display(self):
        """Update the persona display in the chat tab"""
        if self.current_persona:
            name = self.current_persona.profile.name
            self.persona_info.config(text=f"Chatting with: {name}")
            
            # Build details string
            details = f"Likes: {len(self.current_persona.profile.likes)} items • "
            details += f"Dislikes: {len(self.current_persona.profile.dislikes)} items • "
            
            formality = self.current_persona.profile.writing_style.get('formality_level', 'neutral')
            details += f"Style: {formality}"
            
            self.persona_details.config(text=details)
        else:
            self.persona_info.config(text="No persona loaded")
            self.persona_details.config(text="Load a persona from the Manage tab to start chatting")
    
    def refresh_persona_list(self):
        """Refresh the persona list"""
        self.persona_listbox.delete(0, tk.END)
        personas = self.database.list_personas()
        for persona in personas:
            self.persona_listbox.insert(tk.END, persona)
    
    def send_message(self, event=None):
        """Send message to current persona"""
        if not self.current_persona:
            messagebox.showwarning("Warning", "Please load a persona first from the Manage tab")
            return
        
        user_input = self.chat_input.get().strip()
        if not user_input:
            return
        
        # Add user message to chat
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {user_input}\n\n")
        
        # Generate persona response
        response = self.current_persona.generate_response(user_input)
        self.chat_display.insert(tk.END, f"{self.current_persona.profile.name}: {response}\n\n")
        
        # Add separator
        self.chat_display.insert(tk.END, "-" * 50 + "\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Clear input
        self.chat_input.delete(0, tk.END)
    
    def clear_chat(self):
        """Clear the chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the conversation history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            if self.current_persona:
                self.current_persona.conversation_history = []
    
    def save_conversation(self):
        """Save current conversation to file"""
        if not self.current_persona or not self.current_persona.conversation_history:
            messagebox.showwarning("Warning", "No conversation to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Conversation",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Conversation with {self.current_persona.profile.name}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in self.current_persona.conversation_history:
                        f.write(f"You: {entry['user']}\n\n")
                        f.write(f"{self.current_persona.profile.name}: {entry['persona']}\n\n")
                        f.write("-" * 30 + "\n\n")
                
                messagebox.showinfo("Success", f"Conversation saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save conversation: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    print("Minimal Holographic Persona Generator v1.0")
    print("=" * 50)
    print("Starting application...")
    
    # Create necessary directories
    os.makedirs("processed_faces", exist_ok=True)
    
    try:
        app = MinimalPersonaApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()


