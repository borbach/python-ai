#!/usr/bin/env python3
"""
Holographic AI Chat System
A system that creates holograms from photos and conducts personality-based conversations
"""

import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import threading
import queue
import time
import random
import math
import requests
from typing import List, Dict

# Speech modules - loaded only if needed
sr = None
pyttsx3 = None

class HologramChat:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Holographic AI Chat System")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Initialize components
        self.hologram_data = None
        self.personality_traits = {}
        self.chat_history = []
        self.conversation_history = []  # For maintaining LLM context
        self.is_listening = False
        self.animation_running = False
        self.voice_enabled = False
        
        # Speech components (loaded only if needed)
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # AI Configuration
        self.ai_config = {
            'provider': 'anthropic',  # 'anthropic', 'openai', or 'local'
            'api_key': '',
            'model': 'claude-3-sonnet-20240229',
            'base_url': '',  # For local models like Ollama
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        # Animation variables
        self.hologram_frame = 0
        self.hologram_layers = []
        
        # GUI setup
        self.setup_gui()
        
        # Load existing holograms and config
        self.load_existing_holograms()
        self.load_ai_config()
        
        # Ask about voice features
        self.ask_voice_preference()

    def ask_voice_preference(self):
        """Ask user if they want to enable voice features"""
        result = messagebox.askyesno(
            "Voice Features", 
            "Do you want to enable voice recognition and text-to-speech?\n\n" +
            "Yes: Full voice interaction (requires microphone and speakers)\n" +
            "No: Text-only mode (type your messages)",
            default='no'
        )
        
        if result:
            self.enable_voice_features()
        else:
            self.voice_enabled = False
            self.voice_status_label.config(text="Voice: Text-only mode", fg='cyan')
            self.setup_text_input()

    def enable_voice_features(self):
        """Enable voice recognition and TTS"""
        try:
            global sr, pyttsx3
            import speech_recognition as sr
            import pyttsx3
            
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            self.voice_enabled = True
            
            self.voice_status_label.config(text="Voice: Enabled", fg='green')
            self.status_label.config(text="Voice features enabled")
            
        except ImportError as e:
            messagebox.showerror(
                "Voice Features Not Available", 
                f"Could not load speech modules: {e}\n\n" +
                "Please install: pip install speechrecognition pyttsx3 pyaudio\n" +
                "Falling back to text-only mode."
            )
            self.voice_enabled = False
            self.voice_status_label.config(text="Voice: Text-only mode", fg='cyan')
            self.setup_text_input()
        except Exception as e:
            messagebox.showerror(
                "Voice Setup Error", 
                f"Error setting up voice features: {e}\n" +
                "Falling back to text-only mode."
            )
            self.voice_enabled = False
            self.voice_status_label.config(text="Voice: Text-only mode", fg='cyan')
            self.setup_text_input()

    def setup_text_input(self):
        """Setup text input interface for non-voice mode"""
        # Add text input area to the chat display
        input_frame = tk.Frame(self.root, bg='black')
        input_frame.pack(side='bottom', fill='x', padx=10, pady=5)
        
        tk.Label(input_frame, text="Type your message:", 
                fg='cyan', bg='black', font=('Arial', 10)).pack(anchor='w')
        
        self.text_input_frame = tk.Frame(input_frame, bg='black')
        self.text_input_frame.pack(fill='x', pady=5)
        
        self.text_entry = tk.Entry(self.text_input_frame, bg='darkblue', fg='white', 
                                  font=('Arial', 12))
        self.text_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.send_button = tk.Button(self.text_input_frame, text="Send", 
                                    command=self.send_text_message, 
                                    bg='darkgreen', fg='white')
        self.send_button.pack(side='right')
        
        # Bind Enter key to send message
        self.text_entry.bind('<Return>', lambda e: self.send_text_message())
        
        # Focus on text entry
        self.text_entry.focus_set()

    def send_text_message(self):
        """Send text message and get AI response"""
        if not self.is_listening:
            messagebox.showwarning("Chat Not Started", "Please start the chat session first.")
            return
            
        message = self.text_entry.get().strip()
        if not message:
            return
            
        # Clear the input
        self.text_entry.delete(0, tk.END)
        
        # Check for exit commands
        if message.lower() in ['goodbye', 'bye', 'exit', 'quit']:
            self.stop_chat()
            return
        
        # Add user message to chat
        self.add_to_chat("You", message)
        
        # Get AI response in separate thread
        response_thread = threading.Thread(target=self.get_ai_response, args=(message,))
        response_thread.daemon = True
        response_thread.start()

    def get_ai_response(self, user_input):
        """Get AI response in background thread"""
        try:
            self.root.after(0, lambda: self.status_label.config(text="AI thinking..."))
            
            response = self.call_llm(user_input)
            
            # Add AI response to chat
            self.root.after(0, lambda: self.add_to_chat("AI", response))
            
            # Speak response if voice is enabled
            if self.voice_enabled:
                self.root.after(0, lambda: self.speak_response(response))
                
            self.root.after(0, lambda: self.status_label.config(text="Ready"))
            
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            self.root.after(0, lambda: self.add_to_chat("System", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="AI Error"))

    def setup_gui(self):
        """Setup the main GUI interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for controls
        control_panel = tk.Frame(main_frame, bg='black', width=300)
        control_panel.pack(side='left', fill='y', padx=(0, 10))
        control_panel.pack_propagate(False)
        
        # Title
        title_label = tk.Label(control_panel, text="Holographic AI Chat", 
                              font=('Arial', 16, 'bold'), fg='cyan', bg='black')
        title_label.pack(pady=10)
        
        # Hologram section
        hologram_frame = tk.LabelFrame(control_panel, text="Hologram", 
                                      fg='cyan', bg='black', font=('Arial', 12))
        hologram_frame.pack(fill='x', pady=5)
        
        tk.Button(hologram_frame, text="Create New Hologram", 
                 command=self.create_hologram, bg='darkblue', fg='white').pack(pady=5)
        
        tk.Button(hologram_frame, text="Load Existing Hologram", 
                 command=self.load_hologram_dialog, bg='darkgreen', fg='white').pack(pady=5)
        
        # AI Configuration section
        ai_frame = tk.LabelFrame(control_panel, text="AI Configuration", 
                               fg='cyan', bg='black', font=('Arial', 12))
        ai_frame.pack(fill='x', pady=5)
        
        tk.Button(ai_frame, text="Configure AI Provider", 
                 command=self.configure_ai, bg='darkorange', fg='white').pack(pady=5)
        
        self.ai_status_label = tk.Label(ai_frame, text="AI: Not configured", 
                                      fg='red', bg='black', font=('Arial', 9))
        self.ai_status_label.pack(pady=2)
        
        # Voice settings section
        voice_frame = tk.LabelFrame(control_panel, text="Voice Settings", 
                                  fg='cyan', bg='black', font=('Arial', 12))
        voice_frame.pack(fill='x', pady=5)
        
        self.voice_status_label = tk.Label(voice_frame, text="Voice: Configuring...", 
                                         fg='yellow', bg='black', font=('Arial', 9))
        self.voice_status_label.pack(pady=2)
        
        tk.Button(voice_frame, text="Toggle Voice Mode", 
                 command=self.toggle_voice_mode, bg='darkviolet', fg='white').pack(pady=5)
        
        # Personality section
        personality_frame = tk.LabelFrame(control_panel, text="Personality", 
                                        fg='cyan', bg='black', font=('Arial', 12))
        personality_frame.pack(fill='x', pady=5)
        
        tk.Button(personality_frame, text="Set Personality Traits", 
                 command=self.set_personality, bg='purple', fg='white').pack(pady=5)
        
        # Current traits display
        self.traits_label = tk.Label(personality_frame, text="No traits set", 
                                   fg='yellow', bg='black', wraplength=250)
        self.traits_label.pack(pady=5)
        
        # Chat controls
        chat_frame = tk.LabelFrame(control_panel, text="Chat Controls", 
                                  fg='cyan', bg='black', font=('Arial', 12))
        chat_frame.pack(fill='x', pady=5)
        
        self.start_button = tk.Button(chat_frame, text="Start Chat", 
                                    command=self.start_chat, bg='darkred', fg='white')
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(chat_frame, text="Stop Chat", 
                                   command=self.stop_chat, bg='maroon', fg='white', state='disabled')
        self.stop_button.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(control_panel, text="Ready", 
                                   fg='green', bg='black', font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        # Right panel for hologram display and chat
        display_panel = tk.Frame(main_frame, bg='black')
        display_panel.pack(side='right', fill='both', expand=True)
        
        # Hologram display area
        self.hologram_canvas = tk.Canvas(display_panel, bg='black', height=400)
        self.hologram_canvas.pack(fill='x', pady=(0, 10))
        
        # Chat display area
        chat_display_frame = tk.Frame(display_panel, bg='black')
        chat_display_frame.pack(fill='both', expand=True)
        
        tk.Label(chat_display_frame, text="Chat Transcript", 
                font=('Arial', 12, 'bold'), fg='cyan', bg='black').pack()
        
        self.chat_text = tk.Text(chat_display_frame, bg='black', fg='green', 
                               font=('Courier', 10), height=15)
        self.chat_text.pack(fill='both', expand=True, pady=5)
        
        # Scrollbar for chat
        scrollbar = tk.Scrollbar(chat_display_frame)
        scrollbar.pack(side='right', fill='y')
        self.chat_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chat_text.yview)

    def toggle_voice_mode(self):
        """Toggle between voice and text mode"""
        if self.voice_enabled:
            # Disable voice
            self.voice_enabled = False
            self.voice_status_label.config(text="Voice: Disabled", fg='red')
            if not hasattr(self, 'text_input_frame'):
                self.setup_text_input()
        else:
            # Try to enable voice
            self.enable_voice_features()

    def create_hologram(self):
        """Create a new hologram from selected photos"""
        file_paths = filedialog.askopenfilenames(
            title="Select photos for hologram",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if not file_paths:
            return
            
        try:
            self.status_label.config(text="Creating hologram...")
            self.root.update()
            
            # Process images to create hologram effect
            hologram_layers = []
            for i, path in enumerate(file_paths[:5]):  # Limit to 5 images
                img = Image.open(path)
                # Resize to standard size
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                
                # Apply holographic effects
                # Create multiple layers with different effects
                layer1 = img.convert('RGBA')
                layer2 = img.filter(ImageFilter.BLUR)
                layer3 = img.filter(ImageFilter.EDGE_ENHANCE)
                
                # Adjust colors for holographic effect
                enhancer = ImageEnhance.Color(layer1)
                layer1 = enhancer.enhance(1.5)
                
                hologram_layers.extend([layer1, layer2, layer3])
            
            # Save hologram data
            hologram_name = simpledialog.askstring("Hologram Name", "Enter a name for this hologram:")
            if hologram_name:
                self.save_hologram(hologram_name, hologram_layers)
                self.hologram_layers = hologram_layers
                self.status_label.config(text=f"Hologram '{hologram_name}' created successfully")
                self.start_hologram_animation()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create hologram: {str(e)}")
            self.status_label.config(text="Ready")

    def save_hologram(self, name, layers):
        """Save hologram data to disk"""
        if not os.path.exists('holograms'):
            os.makedirs('holograms')
        
        hologram_dir = os.path.join('holograms', name)
        if not os.path.exists(hologram_dir):
            os.makedirs(hologram_dir)
        
        # Save each layer
        for i, layer in enumerate(layers):
            layer.save(os.path.join(hologram_dir, f'layer_{i}.png'))
        
        # Save metadata
        metadata = {
            'name': name,
            'layer_count': len(layers),
            'created': time.time()
        }
        
        with open(os.path.join(hologram_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)

    def load_existing_holograms(self):
        """Load list of existing holograms"""
        self.existing_holograms = []
        if os.path.exists('holograms'):
            for item in os.listdir('holograms'):
                hologram_path = os.path.join('holograms', item)
                if os.path.isdir(hologram_path):
                    metadata_path = os.path.join(hologram_path, 'metadata.json')
                    if os.path.exists(metadata_path):
                        self.existing_holograms.append(item)

    def load_hologram_dialog(self):
        """Show dialog to select and load existing hologram"""
        if not self.existing_holograms:
            messagebox.showinfo("No Holograms", "No existing holograms found. Please create one first.")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Hologram")
        dialog.geometry("300x200")
        dialog.configure(bg='black')
        
        tk.Label(dialog, text="Select a hologram:", fg='cyan', bg='black').pack(pady=10)
        
        listbox = tk.Listbox(dialog, bg='darkblue', fg='white')
        for hologram in self.existing_holograms:
            listbox.insert(tk.END, hologram)
        listbox.pack(pady=10, padx=20, fill='both', expand=True)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                hologram_name = self.existing_holograms[selection[0]]
                self.load_hologram(hologram_name)
                dialog.destroy()
        
        tk.Button(dialog, text="Load", command=load_selected, 
                 bg='darkgreen', fg='white').pack(pady=10)

    def load_hologram(self, name):
        """Load hologram from disk"""
        try:
            hologram_dir = os.path.join('holograms', name)
            
            # Load metadata
            with open(os.path.join(hologram_dir, 'metadata.json'), 'r') as f:
                metadata = json.load(f)
            
            # Load layers
            layers = []
            for i in range(metadata['layer_count']):
                layer_path = os.path.join(hologram_dir, f'layer_{i}.png')
                if os.path.exists(layer_path):
                    layer = Image.open(layer_path)
                    layers.append(layer)
            
            self.hologram_layers = layers
            self.status_label.config(text=f"Hologram '{name}' loaded")
            self.start_hologram_animation()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hologram: {str(e)}")

    def start_hologram_animation(self):
        """Start the hologram animation"""
        self.animation_running = True
        self.animate_hologram()

    def animate_hologram(self):
        """Animate the hologram display"""
        if not self.animation_running or not self.hologram_layers:
            return
        
        # Clear canvas
        self.hologram_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.hologram_canvas.winfo_width()
        canvas_height = self.hologram_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not ready yet
            self.root.after(100, self.animate_hologram)
            return
        
        # Calculate animation parameters
        time_factor = time.time() * 2
        layer_index = int(time_factor) % len(self.hologram_layers)
        
        # Get current layer
        current_layer = self.hologram_layers[layer_index]
        
        # Apply animation effects
        # Simulate holographic shimmer
        alpha = int(128 + 64 * math.sin(time_factor * 3))
        
        # Create animated version
        animated_layer = current_layer.copy()
        if animated_layer.mode != 'RGBA':
            animated_layer = animated_layer.convert('RGBA')
        
        # Apply transparency for holographic effect
        pixels = animated_layer.load()
        for y in range(animated_layer.height):
            for x in range(animated_layer.width):
                r, g, b, a = pixels[x, y]
                # Add cyan tint and transparency variation
                r = min(255, int(r * 0.7 + 50))
                g = min(255, int(g * 0.9 + 100))
                b = min(255, int(b * 1.2))
                a = int(alpha + 30 * math.sin(x * 0.1 + time_factor))
                pixels[x, y] = (r, g, b, max(0, min(255, a)))
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(animated_layer)
        
        # Center on canvas
        x = (canvas_width - animated_layer.width) // 2
        y = (canvas_height - animated_layer.height) // 2
        
        self.hologram_canvas.create_image(x, y, anchor='nw', image=photo)
        
        # Keep reference to prevent garbage collection
        self.hologram_canvas.image = photo
        
        # Add holographic border effect
        self.hologram_canvas.create_rectangle(x-2, y-2, x+animated_layer.width+2, 
                                            y+animated_layer.height+2, 
                                            outline='cyan', width=2)
        
        # Schedule next frame
        self.root.after(100, self.animate_hologram)

    def load_ai_config(self):
        """Load AI configuration from file"""
        if os.path.exists('ai_config.json'):
            try:
                with open('ai_config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.ai_config.update(saved_config)
                    
                # Update status label
                if self.ai_config.get('api_key') or self.ai_config.get('base_url'):
                    provider = self.ai_config['provider'].title()
                    self.ai_status_label.config(text=f"AI: {provider} configured", fg='green')
                
            except Exception as e:
                print(f"Error loading AI config: {e}")

    def save_ai_config(self):
        """Save AI configuration to file"""
        try:
            with open('ai_config.json', 'w') as f:
                json.dump(self.ai_config, f, indent=2)
        except Exception as e:
            print(f"Error saving AI config: {e}")

    def configure_ai(self):
        """Configure AI provider settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI Configuration")
        dialog.geometry("500x400")
        dialog.configure(bg='black')
        
        # Provider selection
        tk.Label(dialog, text="AI Provider:", fg='cyan', bg='black').pack(pady=5)
        
        provider_var = tk.StringVar(value=self.ai_config['provider'])
        provider_frame = tk.Frame(dialog, bg='black')
        provider_frame.pack(pady=5)
        
        tk.Radiobutton(provider_frame, text="Anthropic Claude", variable=provider_var, 
                      value="anthropic", bg='black', fg='white', selectcolor='darkblue').pack(side='left')
        tk.Radiobutton(provider_frame, text="OpenAI GPT", variable=provider_var, 
                      value="openai", bg='black', fg='white', selectcolor='darkblue').pack(side='left')
        tk.Radiobutton(provider_frame, text="Local (Ollama)", variable=provider_var, 
                      value="local", bg='black', fg='white', selectcolor='darkblue').pack(side='left')
        
        # API Key field
        tk.Label(dialog, text="API Key (leave empty for local):", fg='cyan', bg='black').pack(pady=(20,5))
        api_key_var = tk.StringVar(value=self.ai_config.get('api_key', ''))
        api_key_entry = tk.Entry(dialog, textvariable=api_key_var, show='*', width=50)
        api_key_entry.pack(pady=5)
        
        # Model field
        tk.Label(dialog, text="Model:", fg='cyan', bg='black').pack(pady=(10,5))
        model_var = tk.StringVar(value=self.ai_config.get('model', ''))
        model_entry = tk.Entry(dialog, textvariable=model_var, width=50)
        model_entry.pack(pady=5)
        
        # Base URL (for local models)
        tk.Label(dialog, text="Base URL (for local models):", fg='cyan', bg='black').pack(pady=(10,5))
        base_url_var = tk.StringVar(value=self.ai_config.get('base_url', 'http://localhost:11434'))
        base_url_entry = tk.Entry(dialog, textvariable=base_url_var, width=50)
        base_url_entry.pack(pady=5)
        
        # Temperature slider
        tk.Label(dialog, text="Temperature (creativity):", fg='cyan', bg='black').pack(pady=(10,5))
        temp_var = tk.DoubleVar(value=self.ai_config.get('temperature', 0.7))
        temp_scale = tk.Scale(dialog, from_=0.0, to=2.0, resolution=0.1,
                             variable=temp_var, orient='horizontal',
                             bg='darkblue', fg='white')
        temp_scale.pack(pady=5)
        
        # Max tokens
        tk.Label(dialog, text="Max tokens:", fg='cyan', bg='black').pack(pady=(10,5))
        tokens_var = tk.IntVar(value=self.ai_config.get('max_tokens', 150))
        tokens_entry = tk.Entry(dialog, textvariable=tokens_var, width=10)
        tokens_entry.pack(pady=5)
        
        def save_config():
            self.ai_config.update({
                'provider': provider_var.get(),
                'api_key': api_key_var.get(),
                'model': model_var.get(),
                'base_url': base_url_var.get(),
                'temperature': temp_var.get(),
                'max_tokens': tokens_var.get()
            })
            
            self.save_ai_config()
            
            # Update status
            if self.ai_config.get('api_key') or self.ai_config.get('base_url'):
                provider = self.ai_config['provider'].title()
                self.ai_status_label.config(text=f"AI: {provider} configured", fg='green')
            
            dialog.destroy()
        
        def test_connection():
            # Save config temporarily and test
            temp_config = {
                'provider': provider_var.get(),
                'api_key': api_key_var.get(),
                'model': model_var.get(),
                'base_url': base_url_var.get(),
                'temperature': temp_var.get(),
                'max_tokens': tokens_var.get()
            }
            
            try:
                test_response = self.call_llm("Hello, this is a test.", temp_config)
                messagebox.showinfo("Success", f"AI connection successful!\n\nResponse: {test_response[:100]}...")
            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect to AI:\n{str(e)}")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='black')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Test Connection", command=test_connection,
                 bg='darkblue', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Save Configuration", command=save_config,
                 bg='darkgreen', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg='darkred', fg='white').pack(side='left', padx=5)

    def set_personality(self):
        """Set personality traits for the AI"""
        traits = ["friendly", "gruff", "talkative", "quiet", "outgoing", 
                 "introverted", "helpful", "sarcastic", "enthusiastic", "calm"]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Personality Traits")
        dialog.geometry("400x500")
        dialog.configure(bg='black')
        
        tk.Label(dialog, text="Select personality traits:", 
                font=('Arial', 12), fg='cyan', bg='black').pack(pady=10)
        
        # Checkboxes for traits
        trait_vars = {}
        for trait in traits:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(dialog, text=trait.capitalize(), variable=var,
                               fg='white', bg='black', selectcolor='darkblue')
            cb.pack(anchor='w', padx=20)
            trait_vars[trait] = var
        
        # Intensity slider
        tk.Label(dialog, text="Personality Intensity:", 
                fg='cyan', bg='black').pack(pady=(20, 5))
        
        intensity_var = tk.DoubleVar(value=0.7)
        intensity_scale = tk.Scale(dialog, from_=0.1, to=1.0, resolution=0.1,
                                 variable=intensity_var, orient='horizontal',
                                 bg='darkblue', fg='white')
        intensity_scale.pack(pady=5)
        
        def save_traits():
            selected_traits = []
            for trait, var in trait_vars.items():
                if var.get():
                    selected_traits.append(trait)
            
            self.personality_traits = {
                'traits': selected_traits,
                'intensity': intensity_var.get()
            }
            
            trait_text = ", ".join(selected_traits) if selected_traits else "None"
            self.traits_label.config(text=f"Traits: {trait_text}")
            
            dialog.destroy()
        
        tk.Button(dialog, text="Save Traits", command=save_traits,
                 bg='darkgreen', fg='white').pack(pady=20)

    def create_personality_prompt(self, user_input: str) -> str:
        """Create a system prompt that incorporates personality traits"""
        traits = self.personality_traits.get('traits', [])
        intensity = self.personality_traits.get('intensity', 0.5)
        
        if not traits:
            personality_desc = "a helpful AI assistant"
        else:
            # Build personality description
            trait_descriptions = {
                'friendly': 'warm and welcoming',
                'gruff': 'blunt and somewhat rough around the edges',
                'talkative': 'very conversational and tends to elaborate',
                'quiet': 'concise and speaks only when necessary',
                'outgoing': 'enthusiastic and energetic',
                'introverted': 'thoughtful and reserved',
                'helpful': 'eager to assist and provide solutions',
                'sarcastic': 'witty with a tendency toward irony',
                'enthusiastic': 'excited and passionate about topics',
                'calm': 'composed and measured in responses'
            }
            
            personality_parts = []
            for trait in traits:
                if trait in trait_descriptions:
                    personality_parts.append(trait_descriptions[trait])
            
            intensity_modifier = ""
            if intensity > 0.8:
                intensity_modifier = "extremely "
            elif intensity > 0.6:
                intensity_modifier = "quite "
            elif intensity < 0.3:
                intensity_modifier = "somewhat "
            
            personality_desc = f"an AI with a {intensity_modifier}{', '.join(personality_parts)} personality"
        
        system_prompt = f"""You are {personality_desc}. You're having a voice conversation with someone through a holographic interface. 

Keep your responses conversational and natural, as if speaking aloud. Avoid overly formal language or lengthy explanations unless specifically asked. Your responses should feel like natural speech that works well when converted to audio.

Remember your personality traits and respond accordingly, but don't overdo it - be natural while maintaining your character.

User said: "{user_input}"

Respond in a way that matches your personality:"""
        
        return system_prompt

    def call_llm(self, user_input: str, config=None) -> str:
        """Make API call to the configured LLM"""
        if config is None:
            config = self.ai_config
        
        provider = config['provider']
        
        try:
            if provider == 'anthropic':
                return self.call_anthropic(user_input, config)
            elif provider == 'openai':
                return self.call_openai(user_input, config)
            elif provider == 'local':
                return self.call_local_llm(user_input, config)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            return f"AI Error: {str(e)}"

    def call_anthropic(self, user_input: str, config: dict) -> str:
        """Call Anthropic Claude API"""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config['api_key'],
            "anthropic-version": "2023-06-01"
        }
        
        # Build conversation history
        messages = []
        for msg in self.conversation_history[-10:]:  # Keep last 10 exchanges
            messages.append(msg)
        
        # Add current message with personality context
        system_prompt = self.create_personality_prompt(user_input)
        messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": config['model'],
            "max_tokens": config['max_tokens'],
            "temperature": config['temperature'],
            "system": system_prompt,
            "messages": messages
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['content'][0]['text']
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    def call_openai(self, user_input: str, config: dict) -> str:
        """Call OpenAI GPT API"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        # Build conversation history
        messages = [{"role": "system", "content": self.create_personality_prompt(user_input)}]
        
        for msg in self.conversation_history[-10:]:  # Keep last 10 exchanges
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": config['model'],
            "messages": messages,
            "max_tokens": config['max_tokens'],
            "temperature": config['temperature']
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    def call_local_llm(self, user_input: str, config: dict) -> str:
        """Call local LLM (like Ollama)"""
        url = f"{config['base_url']}/api/generate"
        
        # Build context from conversation history
        context = self.create_personality_prompt(user_input)
        for msg in self.conversation_history[-6:]:  # Keep last 6 exchanges for context
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"\n\n{role}: {msg['content']}"
        
        context += f"\n\nHuman: {user_input}\n\nAssistant:"
        
        payload = {
            "model": config['model'],
            "prompt": context,
            "stream": False,
            "options": {
                "temperature": config['temperature'],
                "num_predict": config['max_tokens']
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['response'].strip()
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    def start_chat(self):
        """Start the chat session"""
        if not self.hologram_layers:
            messagebox.showwarning("No Hologram", "Please create or load a hologram first.")
            return
        
        if not self.personality_traits:
            messagebox.showwarning("No Personality", "Please set personality traits first.")
            return
            
        if not self.ai_config.get('api_key') and not self.ai_config.get('base_url'):
            messagebox.showwarning("No AI Configuration", "Please configure an AI provider first.")
            return
        
        self.is_listening = True
        self.conversation_history = []  # Reset conversation history
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        if self.voice_enabled:
            self.status_label.config(text="Voice mode - Listening...")
            self.add_to_chat("System", f"Voice chat session started with {self.ai_config['provider'].title()} AI. Speak to begin conversation.")
            
            # Start listening in a separate thread
            listen_thread = threading.Thread(target=self.listen_loop)
            listen_thread.daemon = True
            listen_thread.start()
        else:
            self.status_label.config(text="Text mode - Ready to chat")
            self.add_to_chat("System", f"Text chat session started with {self.ai_config['provider'].title()} AI. Type your message below.")
            
            # Focus on text input if available
            if hasattr(self, 'text_entry'):
                self.text_entry.focus_set()

    def stop_chat(self):
        """Stop the chat session"""
        self.is_listening = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Ready")
        
        self.add_to_chat("System", "Chat session ended.")

    def listen_loop(self):
        """Main listening loop - only runs if voice is enabled"""
        if not self.voice_enabled or not self.recognizer:
            return
            
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        while self.is_listening and self.voice_enabled:
            try:
                # Listen for audio
                with self.microphone as source:
                    self.status_label.config(text="Voice mode - Listening...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                self.status_label.config(text="Processing speech...")
                text = self.recognizer.recognize_google(audio)
                
                if text.lower().strip() in ['goodbye', 'bye', 'exit', 'quit']:
                    self.root.after(0, self.stop_chat)
                    break
                
                # Add user input to chat
                self.root.after(0, lambda: self.add_to_chat("You", text))
                
                # Generate AI response using LLM
                self.root.after(0, lambda: self.status_label.config(text="AI thinking..."))
                
                try:
                    response = self.call_llm(text)
                    
                    # Add AI response to chat and speak it
                    self.root.after(0, lambda: self.add_to_chat("AI", response))
                    if self.voice_enabled:
                        self.root.after(0, lambda: self.speak_response(response))
                    self.root.after(0, lambda: self.status_label.config(text="Voice mode - Listening..."))
                    
                except Exception as e:
                    error_msg = f"AI Error: {str(e)}"
                    self.root.after(0, lambda: self.add_to_chat("System", error_msg))
                    self.root.after(0, lambda: self.status_label.config(text="AI Error - Try again"))
                
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.status_label.config(text="Couldn't understand. Try again."))
            except sr.RequestError as e:
                self.root.after(0, lambda: self.add_to_chat("System", f"Speech recognition error: {e}"))
            except Exception as e:
                self.root.after(0, lambda: self.add_to_chat("System", f"Voice error: {e}"))

    def generate_response(self, user_input):
        """Generate AI response based on personality traits (LEGACY - kept for fallback)"""
        # This method is kept as a fallback if LLM calls fail
        # The main response generation now happens in call_llm()
        
        traits = self.personality_traits.get('traits', [])
        intensity = self.personality_traits.get('intensity', 0.5)
        
        # Base response patterns
        responses = {
            'greeting': ["Hello there!", "Hi!", "Hey!", "Greetings!"],
            'question': ["That's interesting.", "Let me think about that.", "Good question.", "Hmm."],
            'default': ["I see.", "That's nice.", "Okay.", "Interesting."]
        }
        
        # Determine response type
        user_lower = user_input.lower()
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            response_type = 'greeting'
        elif '?' in user_input:
            response_type = 'question'
        else:
            response_type = 'default'
        
        base_response = random.choice(responses[response_type])
        
        # Apply personality modifications
        if 'gruff' in traits:
            base_response = base_response.replace('!', '.').lower()
            if intensity > 0.7:
                base_response = f"Hmph. {base_response}"
        
        if 'friendly' in traits:
            base_response += " Hope you're having a great day!"
            
        if 'talkative' in traits and intensity > 0.6:
            base_response += f" You know, when you said '{user_input}', it reminds me of many things I could discuss."
            
        if 'sarcastic' in traits and intensity > 0.5:
            base_response = f"Oh, {base_response.lower()} How original."
            
        if 'enthusiastic' in traits:
            base_response = base_response.upper() + "!!!"
            
        if 'quiet' in traits:
            base_response = base_response.split('.')[0] + "."
        
        return base_response

    def speak_response(self, text):
        """Convert text to speech - only if voice is enabled"""
        if not self.voice_enabled or not self.tts_engine:
            return
            
        try:
            # Adjust speech rate based on personality
            rate = 200  # Default rate
            
            if 'talkative' in self.personality_traits.get('traits', []):
                rate = 250
            elif 'quiet' in self.personality_traits.get('traits', []):
                rate = 150
                
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def add_to_chat(self, speaker, message):
        """Add message to chat display"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {speaker}: {message}\n"
        
        self.chat_text.insert(tk.END, formatted_message)
        self.chat_text.see(tk.END)
        
        # Color coding
        if speaker == "You":
            # Find the last line and color it blue
            line_start = self.chat_text.index("end-2c linestart")
            line_end = self.chat_text.index("end-2c lineend")
            self.chat_text.tag_add("user", line_start, line_end)
            self.chat_text.tag_config("user", foreground="lightblue")
        elif speaker == "AI":
            # Find the last line and color it green
            line_start = self.chat_text.index("end-2c linestart")
            line_end = self.chat_text.index("end-2c lineend")
            self.chat_text.tag_add("ai", line_start, line_end)
            self.chat_text.tag_config("ai", foreground="lightgreen")
        elif speaker == "System":
            # Find the last line and color it yellow
            line_start = self.chat_text.index("end-2c linestart")
            line_end = self.chat_text.index("end-2c lineend")
            self.chat_text.tag_add("system", line_start, line_end)
            self.chat_text.tag_config("system", foreground="yellow")

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to run the holographic chat system"""
    try:
        app = HologramChat()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        print("Required dependencies:")
        print("pip install Pillow requests")
        print("\nOptional (for voice features):")
        print("pip install speechrecognition pyttsx3 pyaudio")
        print("\nFor AI integration, you'll need:")
        print("- Anthropic API key for Claude")
        print("- OpenAI API key for GPT models")
        print("- Or Ollama installed locally for local models")

if __name__ == "__main__":
    main()


