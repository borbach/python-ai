import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import base64
import threading
import requests
from PIL import Image, ImageTk, ImageDraw
import io
import math
import random

# Optional voice imports - will gracefully handle if missing
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice libraries not available. Install with: pip install speechrecognition pyttsx3 pyaudio")

class HologramCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hologram Creator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        self.root.minsize(1000, 700)
        
        # Data storage
        self.current_hologram = {
            'name': '',
            'images': [],
            'personality': {
                'friendly': 5,
                'gruff': 3,
                'extrovert': 5,
                'happy': 5,
                'confident': 5,
                'creative': 5
            }
        }
        self.saved_holograms = []
        self.chat_history = []
        self.communication_mode = 'text'
        self.merged_hologram_image = None
        
        # Image cycling variables
        self.current_image_index = 0
        self.cycle_images = []
        self.image_cycle_job = None
        
        # Voice recognition setup (only if available)
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.is_recording = False
        self.voice_setup_failed = False
        self.gender = 0
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Use enhanced voice setup
                self.setup_voice_engine()
                
                # Calibrate microphone for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
            except Exception as e:
                print(f"Voice setup failed: {e}")
                self.voice_setup_failed = True
        
        # Store last response for TTS
        self.last_ai_response = ""
        
        # Load saved holograms
        self.load_saved_holograms()
        
        # Start with main menu
        self.show_main_menu()
   
    def set_male(self):
        self.gender = ""
        return

    def set_female(self):
        random_int = random.randint(1,4)
        if random_int == 1:
            self.gender = "+f1"
        if random_int == 2:
            self.gender = "+f2"
        if random_int == 3:
            self.gender = "+f3"
        if random_int == 4:
            self.gender = "+f4"
        return

    def setup_voice_engine(self):
        """Setup the text-to-speech engine with enhanced settings"""
        if not VOICE_AVAILABLE:
            return
            
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Set voice properties
            if voices:
                # Try to find a female voice first, then any voice
                selected_voice = None
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        selected_voice = voice.id
                        break
                
                if not selected_voice and voices:
                    selected_voice = voices[0].id
                
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
            
        except Exception as e:
            print(f"TTS engine setup failed: {e}")
            self.tts_engine = None
    
    def show_voice_settings(self):
        """Show voice settings dialog"""
        if not VOICE_AVAILABLE or not self.tts_engine:
            messagebox.showinfo("Voice Settings", "Voice features are not available.\n\nPlease install: pip install speechrecognition pyttsx3 pyaudio")
            return
        
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Voice Settings")
        settings_window.geometry("800x600")
        settings_window.configure(bg='#2c3e50')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        title_label = tk.Label(settings_window, text="Voice Settings", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Voice selection
        voice_frame = tk.Frame(settings_window, bg='#2c3e50')
        voice_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(voice_frame, text="Voice:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#2c3e50').pack(anchor='w')
        
        # Get available voices
        voices = self.tts_engine.getProperty('voices')
        current_voice = self.tts_engine.getProperty('voice')
        
        self.voice_var = tk.StringVar()
        voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, 
                                     state="readonly", width=50)
        
        voice_options = []
        voice_ids = []
        for voice in voices:
            voice_name = voice.name if hasattr(voice, 'name') else str(voice.id)
            voice_options.append(voice_name)
            voice_ids.append(voice.id)
            if voice.id == current_voice:
                self.voice_var.set(voice_name)
        
        voice_dropdown['values'] = voice_options
        voice_dropdown.pack(pady=5, fill=tk.X)
        
        # Speech rate
        rate_frame = tk.Frame(settings_window, bg='#2c3e50')
        rate_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(rate_frame, text="Speech Rate:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#2c3e50').pack(anchor='w')
        
        current_rate = self.tts_engine.getProperty('rate')
        self.rate_var = tk.IntVar(value=current_rate)
        
        rate_scale = tk.Scale(rate_frame, from_=100, to=300, orient=tk.HORIZONTAL,
                             variable=self.rate_var, bg='#34495e', fg='white',
                             highlightbackground='#2c3e50', length=300)
        rate_scale.pack(pady=5, fill=tk.X)
        
        tk.Label(rate_frame, text="Slower ← → Faster", font=('Arial', 8), 
                fg='#bdc3c7', bg='#2c3e50').pack()
        
        # Volume
        volume_frame = tk.Frame(settings_window, bg='#2c3e50')
        volume_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(volume_frame, text="Volume:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#2c3e50').pack(anchor='w')
        
        current_volume = self.tts_engine.getProperty('volume')
        self.volume_var = tk.DoubleVar(value=current_volume)
        
        volume_scale = tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1,
                               orient=tk.HORIZONTAL, variable=self.volume_var,
                               bg='#34495e', fg='white', highlightbackground='#2c3e50',
                               length=300)
        volume_scale.pack(pady=5, fill=tk.X)
        
        tk.Label(volume_frame, text="Quieter ← → Louder", font=('Arial', 8), 
                fg='#bdc3c7', bg='#2c3e50').pack()
        
        # Buttons
        gender_frame = tk.Frame(settings_window, bg='#2c3e50')
        gender_frame.pack(pady=20, fill=tk.X)
        
        male_btn = tk.Button(gender_frame, text="Male",
                             command=self.set_male,
                             font=('Arial', 10),
                             bg='#7f8c8d', fg='blue', padx=15, pady=5)
        male_btn.pack(side=tk.LEFT, padx=(300, 5))

        female_btn = tk.Button(gender_frame, text="Female",
                             command=self.set_female,
                             font=('Arial', 10),
                             bg='#7f8c8d', fg='red', padx=15, pady=5)
        female_btn.pack(side=tk.LEFT, padx=(50, 5))

        button_frame = tk.Frame(settings_window, bg='#2c3e50')
        button_frame.pack(pady=20, fill=tk.X)

        test_btn = tk.Button(button_frame, text="Test Voice",
                           command=lambda: self.test_voice_settings(voice_ids, voice_dropdown.current()),
                           font=('Arial', 10),
                           bg='#3498db', fg='white', padx=15, pady=5)
        test_btn.pack(side=tk.LEFT, padx=(20, 5))
        
        save_btn = tk.Button(button_frame, text="Save Settings",
                           command=lambda: self.save_voice_settings(voice_ids, voice_dropdown.current(), settings_window),
                           font=('Arial', 10, 'bold'),
                           bg='#27ae60', fg='white', padx=15, pady=5)
        save_btn.pack(side=tk.RIGHT, padx=(5, 20))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                             command=settings_window.destroy,
                             font=('Arial', 10),
                             bg='#7f8c8d', fg='white', padx=15, pady=5)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def test_voice_settings(self, voice_ids, selected_index):
        """Test the current voice settings"""
        if not self.tts_engine or selected_index < 0:
            return
        
        try:
            # Apply temporary settings
            self.tts_engine.setProperty('voice', voice_ids[selected_index] + self.gender )
            print( voice_ids[selected_index] + self.gender )
            self.tts_engine.setProperty('rate', self.rate_var.get())
            self.tts_engine.setProperty('volume', self.volume_var.get())
            
            # Test message
            test_message = f"Hello! I'm {self.current_hologram['name']}. This is how I will sound when we chat."
            
            # Speak in separate thread
            threading.Thread(target=self._test_speak_thread, args=(test_message,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Test Error", f"Could not test voice: {e}")
    
    def _test_speak_thread(self, text):
        """Test speak in separate thread"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Test TTS Error: {e}")
    
    def save_voice_settings(self, voice_ids, selected_index, window ):
        """Save the voice settings"""
        if not self.tts_engine or selected_index < 0:
            return
        
        try:
            # Apply settings
            self.tts_engine.setProperty('voice', voice_ids[selected_index] + self.gender )
            print( "voice choice is: " + voice_ids[selected_index] + self.gender )
            self.tts_engine.setProperty('rate', self.rate_var.get())
            self.tts_engine.setProperty('volume', self.volume_var.get())
            
            messagebox.showinfo("Settings Saved", "Voice settings have been updated!")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save settings: {e}")
    
    def load_saved_holograms(self):
        """Load saved holograms from file"""
        try:
            if os.path.exists('holograms.json'):
                with open('holograms.json', 'r') as f:
                    self.saved_holograms = json.load(f)
        except Exception as e:
            print(f"Error loading holograms: {e}")
    
    def save_holograms_to_file(self):
        """Save holograms to file"""
        try:
            with open('holograms.json', 'w') as f:
                json.dump(self.saved_holograms, f)
        except Exception as e:
            print(f"Error saving holograms: {e}")
    
    def clear_window(self):
        """Clear all widgets from window"""
        # Cancel any existing image cycling
        if self.image_cycle_job:
            self.root.after_cancel(self.image_cycle_job)
            self.image_cycle_job = None
        
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_individual_hologram_images(self):
        """Create individual hologram images for cycling"""
        if not self.current_hologram['images']:
            return []
        
        hologram_images = []
        
        try:
            for image_info in self.current_hologram['images']:
                # Create a circular hologram for each image
                composite_size = 300
                composite = Image.new('RGBA', (composite_size, composite_size), (0, 0, 0, 0))
                
                # Create circular mask
                mask = Image.new('L', (composite_size, composite_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, composite_size, composite_size), fill=255)
                
                # Load and resize image
                image_data = base64.b64decode(image_info['data'])
                image = Image.open(io.BytesIO(image_data))
                image = image.convert('RGBA')
                image = image.resize((composite_size, composite_size), Image.Resampling.LANCZOS)
                
                # Apply mask
                composite.paste(image, (0, 0))
                composite.putalpha(mask)
                
                # Add holographic effect (subtle glow)
                glow = Image.new('RGBA', (composite_size + 20, composite_size + 20), (0, 0, 0, 0))
                glow_draw = ImageDraw.Draw(glow)
                
                # Create multiple glow layers
                for i in range(5):
                    alpha = 30 - (i * 5)
                    glow_draw.ellipse((i, i, composite_size + 20 - i, composite_size + 20 - i), 
                                    outline=(100, 200, 255, alpha), width=2)
                
                # Combine glow with composite
                final_composite = Image.new('RGBA', (composite_size + 20, composite_size + 20), (0, 0, 0, 0))
                final_composite.paste(glow, (0, 0))
                final_composite.paste(composite, (10, 10), composite)
                
                hologram_images.append(final_composite)
            
            return hologram_images
            
        except Exception as e:
            print(f"Error creating individual hologram images: {e}")
            return []
    
    def create_merged_hologram(self):
        """Create a merged hologram from all uploaded images"""
        if not self.current_hologram['images']:
            return None
        
        # If multiple images, create individual cycling images
        if len(self.current_hologram['images']) > 1:
            self.cycle_images = self.create_individual_hologram_images()
            if self.cycle_images:
                return self.cycle_images[0]  # Return first image as initial display
        
        try:
            # Single image processing
            composite_size = 300
            composite = Image.new('RGBA', (composite_size, composite_size), (0, 0, 0, 0))
            
            # Create circular mask
            mask = Image.new('L', (composite_size, composite_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, composite_size, composite_size), fill=255)
            
            # Single image - make it circular and fill the whole space
            image_data = base64.b64decode(self.current_hologram['images'][0]['data'])
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGBA')
            image = image.resize((composite_size, composite_size), Image.Resampling.LANCZOS)
            composite.paste(image, (0, 0))
            
            # Apply overall circular mask
            composite.putalpha(mask)
            
            # Add holographic effect (subtle glow)
            glow = Image.new('RGBA', (composite_size + 20, composite_size + 20), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            
            # Create multiple glow layers
            for i in range(5):
                alpha = 30 - (i * 5)
                glow_draw.ellipse((i, i, composite_size + 20 - i, composite_size + 20 - i), 
                                outline=(100, 200, 255, alpha), width=2)
            
            # Combine glow with composite
            final_composite = Image.new('RGBA', (composite_size + 20, composite_size + 20), (0, 0, 0, 0))
            final_composite.paste(glow, (0, 0))
            final_composite.paste(composite, (10, 10), composite)
            
            return final_composite
            
        except Exception as e:
            print(f"Error creating merged hologram: {e}")
            return None
    
    def cycle_hologram_image(self):
        """Cycle through hologram images every 3 seconds"""
        if not self.cycle_images or len(self.cycle_images) <= 1:
            return
        
        # Update to next image
        self.current_image_index = (self.current_image_index + 1) % len(self.cycle_images)
        
        # Update the display if hologram_display exists
        if hasattr(self, 'hologram_display') and self.hologram_display.winfo_exists():
            try:
                # Resize for chat interface
                display_image = self.cycle_images[self.current_image_index].copy()
                display_image = display_image.resize((280, 280), Image.Resampling.LANCZOS)
                
                self.hologram_photo = ImageTk.PhotoImage(display_image)
                self.hologram_display.config(image=self.hologram_photo)
                self.hologram_display.image = self.hologram_photo  # Keep reference
            except Exception as e:
                print(f"Error updating hologram display: {e}")
        
        # Schedule next cycle
        self.image_cycle_job = self.root.after(3000, self.cycle_hologram_image)  # 3 seconds
    
    def start_image_cycling(self):
        """Start the image cycling process"""
        if self.cycle_images and len(self.cycle_images) > 1:
            self.current_image_index = 0
            self.image_cycle_job = self.root.after(3000, self.cycle_hologram_image)
    
    def stop_image_cycling(self):
        """Stop the image cycling process"""
        if self.image_cycle_job:
            self.root.after_cancel(self.image_cycle_job)
            self.image_cycle_job = None
    
    def is_voice_available(self):
        """Check if voice functionality is available"""
        return VOICE_AVAILABLE and self.recognizer is not None and self.tts_engine is not None
    
    def record_voice(self):
        """Record voice input from microphone"""
        if not self.is_voice_available():
            self.add_message_to_display("System", "Voice features not available. Install: pip install speechrecognition pyttsx3 pyaudio")
            return
            
        if self.is_recording:
            return
        
        self.is_recording = True
        
        # Update button text
        if hasattr(self, 'record_btn'):
            self.record_btn.config(text="🛑 Recording...", bg='#e74c3c')
        
        self.add_message_to_display("System", "Listening... Speak now!")
        
        # Record in separate thread
        threading.Thread(target=self._record_audio_thread, daemon=True).start()
    
    def _record_audio_thread(self):
        """Record audio in separate thread"""
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                print("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # Reset recording state
            self.is_recording = False
            self.root.after(0, self._update_record_button)
            
            print("Processing speech...")
            self.root.after(0, self.add_message_to_display, "System", "Processing speech...")
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                self.root.after(0, self._handle_voice_input, text)
            except sr.UnknownValueError:
                self.root.after(0, self.add_message_to_display, "System", "Could not understand audio. Please try again.")
            except sr.RequestError as e:
                self.root.after(0, self.add_message_to_display, "System", f"Speech recognition error: {e}")
                
        except sr.WaitTimeoutError:
            self.is_recording = False
            self.root.after(0, self._update_record_button)
            self.root.after(0, self.add_message_to_display, "System", "No speech detected. Timeout.")
        except Exception as e:
            self.is_recording = False
            self.root.after(0, self._update_record_button)
            self.root.after(0, self.add_message_to_display, "System", f"Recording error: {e}")
    
    def _update_record_button(self):
        """Update record button appearance"""
        if hasattr(self, 'record_btn'):
            self.record_btn.config(text="🎤 Record", bg='#27ae60')
    
    def _handle_voice_input(self, text):
        """Handle recognized voice input"""
        self.add_message_to_display("You", f"[Voice] {text}")
        
        # Add to chat history
        self.chat_history.append({"role": "user", "content": text})
        
        # Show loading message and update status
        self.add_message_to_display("System", "Thinking...")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="● Thinking...", fg='#f39c12')
        
        # Send to API in separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def speak_text(self, text):
        """Convert text to speech"""
        if not self.is_voice_available():
            return
            
        try:
            # Remove any system messages or formatting
            clean_text = text.replace("[System]", "").replace("[Voice]", "").strip()
            
            # Remove lines that start and end with asterisks (actions/feelings)
            lines = clean_text.split('\n')
            filtered_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip lines that start and end with asterisks
                if line.startswith('*') and line.endswith('*'):
                    continue
                # Skip empty lines
                if not line:
                    continue
                filtered_lines.append(line)
            
            # Join the remaining lines
            clean_text = ' '.join(filtered_lines).strip()
            
            if clean_text:
                threading.Thread(target=self._speak_thread, args=(clean_text,), daemon=True).start()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def _speak_thread(self, text):
        """Speak text in separate thread"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Thread Error: {e}")
    
    def show_main_menu(self):
        """Display main menu"""
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Hologram Creator", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_label = tk.Label(self.root, text="Create and interact with AI holograms", 
                                 font=('Arial', 12), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(pady=(0, 30))
        
        # Create new hologram button
        create_btn = tk.Button(self.root, text="Create New Hologram",
                              command=self.show_image_selection,
                              font=('Arial', 12, 'bold'),
                              bg='#9b59b6', fg='white',
                              padx=20, pady=10, width=20)
        create_btn.pack(pady=10)
        
        # Show existing holograms if any
        if self.saved_holograms:
            existing_label = tk.Label(self.root, text="Existing Holograms:", 
                                     font=('Arial', 12, 'bold'), 
                                     fg='white', bg='#2c3e50')
            existing_label.pack(pady=(30, 10))
            
            for hologram in self.saved_holograms:
                hologram_btn = tk.Button(self.root, text=f"{hologram['name']} ({hologram.get('created_at', 'Unknown date')})",
                                        command=lambda h=hologram: self.load_hologram(h),
                                        font=('Arial', 10),
                                        bg='#34495e', fg='white',
                                        padx=15, pady=5, width=30)
                hologram_btn.pack(pady=2)
    
    def show_image_selection(self):
        """Display image selection dialog"""
        self.clear_window()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Create Your Hologram", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(10, 20))
        
        # Name input
        name_frame = tk.Frame(main_frame, bg='#2c3e50')
        name_frame.pack(pady=10)
        
        tk.Label(name_frame, text="Hologram Name (Optional):", 
                font=('Arial', 10), fg='white', bg='#2c3e50').pack()
        
        self.name_entry = tk.Entry(name_frame, font=('Arial', 10), width=30)
        self.name_entry.pack(pady=5)
        
        # Image selection
        image_frame = tk.Frame(main_frame, bg='#2c3e50')
        image_frame.pack(pady=10)
        
        tk.Label(image_frame, text="Select up to 5 images (multiple images will cycle automatically):", 
                font=('Arial', 12), fg='white', bg='#2c3e50').pack()
        
        select_btn = tk.Button(image_frame, text="Choose Images",
                              command=self.select_images,
                              font=('Arial', 10, 'bold'),
                              bg='#3498db', fg='white',
                              padx=20, pady=8)
        select_btn.pack(pady=10)
        
        # Selected images display
        self.images_listbox = tk.Listbox(image_frame, height=6, width=50,
                                        font=('Arial', 9))
        self.images_listbox.pack(pady=10)
        
        remove_btn = tk.Button(image_frame, text="Remove Selected Image",
                              command=self.remove_selected_image,
                              font=('Arial', 9),
                              bg='#e74c3c', fg='white',
                              padx=15, pady=5)
        remove_btn.pack(pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              command=self.show_main_menu,
                              font=('Arial', 12, 'bold'),
                              bg='#7f8c8d', fg='white',
                              padx=20, pady=10)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        next_btn = tk.Button(button_frame, text="Next: Set Personality",
                            command=self.validate_and_continue_to_personality,
                            font=('Arial', 12, 'bold'),
                            bg='#27ae60', fg='white',
                            padx=20, pady=10)
        next_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def select_images(self):
        """Open file dialog to select images"""
        if len(self.current_hologram['images']) >= 5:
            messagebox.showwarning("Limit Reached", "You can only select up to 5 images.")
            return
        
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        for file_path in file_paths:
            if len(self.current_hologram['images']) >= 5:
                messagebox.showwarning("Limit Reached", "Maximum 5 images reached.")
                break
            
            try:
                # Convert image to base64 for storage
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                image_info = {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'data': encoded_string
                }
                
                self.current_hologram['images'].append(image_info)
                self.images_listbox.insert(tk.END, image_info['name'])
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image {file_path}: {e}")
    
    def remove_selected_image(self):
        """Remove selected image from list"""
        selection = self.images_listbox.curselection()
        if selection:
            index = selection[0]
            self.images_listbox.delete(index)
            del self.current_hologram['images'][index]
    
    def validate_and_continue_to_personality(self):
        """Validate input and continue to personality selection"""
        if not self.current_hologram['images']:
            messagebox.showerror("Error", "Please select at least one image.")
            return
        
        # Update name
        self.current_hologram['name'] = self.name_entry.get().strip() or f"Hologram_{len(self.saved_holograms) + 1}"
        
        self.show_personality_selection()
    
    def show_personality_selection(self):
        """Display personality trait selection"""
        self.clear_window()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Personality Traits", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(10, 10))
        
        subtitle_label = tk.Label(main_frame, text="Adjust the sliders to define your hologram's personality:", 
                                 font=('Arial', 10), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(pady=(0, 20))
        
        # Personality sliders
        self.personality_vars = {}
        traits = [
            ('friendly', 'Distant', 'Friendly'),
            ('gruff', 'Gentle', 'Gruff'),
            ('extrovert', 'Introverted', 'Extroverted'),
            ('happy', 'Sad', 'Happy'),
            ('confident', 'Uncertain', 'Confident'),
            ('creative', 'Practical', 'Creative')
        ]
        
        sliders_frame = tk.Frame(main_frame, bg='#2c3e50')
        sliders_frame.pack(pady=10, fill=tk.X)
        
        for trait, left_label, right_label in traits:
            trait_frame = tk.Frame(sliders_frame, bg='#2c3e50')
            trait_frame.pack(pady=8, padx=20, fill=tk.X)
            
            # Labels
            label_frame = tk.Frame(trait_frame, bg='#2c3e50')
            label_frame.pack(fill=tk.X)
            
            tk.Label(label_frame, text=left_label, font=('Arial', 10), 
                    fg='white', bg='#2c3e50').pack(side=tk.LEFT)
            tk.Label(label_frame, text=right_label, font=('Arial', 10), 
                    fg='white', bg='#2c3e50').pack(side=tk.RIGHT)
            
            # Slider
            self.personality_vars[trait] = tk.IntVar(value=self.current_hologram['personality'][trait])
            slider = tk.Scale(trait_frame, from_=1, to=8, orient=tk.HORIZONTAL,
                             variable=self.personality_vars[trait],
                             bg='#34495e', fg='white', highlightbackground='#2c3e50',
                             length=300)
            slider.pack(fill=tk.X, pady=3)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        back_btn = tk.Button(button_frame, text="Back",
                           command=self.show_image_selection,
                           font=('Arial', 12, 'bold'),
                           bg='#7f8c8d', fg='white',
                           padx=20, pady=10)
        back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ok_btn = tk.Button(button_frame, text="OK - Create Hologram",
                          command=self.save_hologram,
                          font=('Arial', 12, 'bold'),
                          bg='#27ae60', fg='white',
                          padx=20, pady=10)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def save_hologram(self):
        """Save the current hologram and proceed to hologram display"""
        # Update personality values
        for trait, var in self.personality_vars.items():
            self.current_hologram['personality'][trait] = var.get()
        
        # Add creation date
        from datetime import datetime
        self.current_hologram['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Create merged hologram
        self.merged_hologram_image = self.create_merged_hologram()
        
        # Save to list
        self.saved_holograms.append(self.current_hologram.copy())
        self.save_holograms_to_file()
        
        messagebox.showinfo("Success", f"Hologram '{self.current_hologram['name']}' created successfully!")
        self.show_hologram_display()
    
    def show_hologram_display(self):
        """Display the created hologram with its merged image"""
        self.clear_window()
        
        # Create merged hologram if not already created
        if not self.merged_hologram_image:
            self.merged_hologram_image = self.create_merged_hologram()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text=f"Hologram: {self.current_hologram['name']}", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(10, 20))
        
        # Display merged hologram
        if self.merged_hologram_image:
            hologram_label = tk.Label(main_frame, text="Your Hologram:", 
                                     font=('Arial', 12, 'bold'), 
                                     fg='#bdc3c7', bg='#2c3e50')
            hologram_label.pack(pady=(0, 10))
            
            # Display the merged hologram
            photo = ImageTk.PhotoImage(self.merged_hologram_image)
            hologram_display = tk.Label(main_frame, image=photo, bg='#2c3e50')
            hologram_display.pack(pady=10)
            hologram_display.image = photo  # Keep reference
            
            # Show cycling info if multiple images
            if len(self.current_hologram['images']) > 1:
                cycle_info = tk.Label(main_frame, 
                                     text=f"({len(self.current_hologram['images'])} images will cycle during chat)", 
                                     font=('Arial', 9, 'italic'), 
                                     fg='#95a5a6', bg='#2c3e50')
                cycle_info.pack(pady=5)
        
        # Personality summary
        personality_label = tk.Label(main_frame, text="Personality Profile:", 
                                    font=('Arial', 12, 'bold'), 
                                    fg='#bdc3c7', bg='#2c3e50')
        personality_label.pack(pady=(20, 10))
        
        personality_desc = self.generate_personality_description()
        personality_text = tk.Label(main_frame, text=personality_desc, 
                                   font=('Arial', 10), 
                                   fg='white', bg='#2c3e50', wraplength=600)
        personality_text.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        back_btn = tk.Button(button_frame, text="Back to Menu",
                           command=self.show_main_menu,
                           font=('Arial', 12, 'bold'),
                           bg='#7f8c8d', fg='white',
                           padx=20, pady=10)
        back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        chat_btn = tk.Button(button_frame, text="OK - Start Chatting",
                            command=self.show_communication_mode,
                            font=('Arial', 12, 'bold'),
                            bg='#9b59b6', fg='white',
                            padx=20, pady=10)
        chat_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def load_hologram(self, hologram):
        """Load an existing hologram"""
        self.current_hologram = hologram.copy()
        self.merged_hologram_image = self.create_merged_hologram()
        self.show_hologram_display()
    
    def show_communication_mode(self):
        """Display communication mode selection"""
        self.clear_window()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=50)
        
        # Title
        title_label = tk.Label(main_frame, text="Communication Mode", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(20, 30))
        
        subtitle_label = tk.Label(main_frame, text=f"How would you like to interact with {self.current_hologram['name']}?", 
                                 font=('Arial', 12), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(pady=(0, 30))
        
        # Communication mode selection
        self.comm_mode_var = tk.StringVar(value='text')
        
        # Radio button frame
        radio_frame = tk.Frame(main_frame, bg='#2c3e50')
        radio_frame.pack(pady=20)
        
        text_radio = tk.Radiobutton(radio_frame, text="Text Chat - Type messages to communicate",
                                   variable=self.comm_mode_var, value='text',
                                   font=('Arial', 12), fg='white', bg='#2c3e50',
                                   selectcolor='#9b59b6', activebackground='#2c3e50')
        text_radio.pack(pady=10, anchor='w')
        
        voice_status = "Voice Chat - Speak and listen to responses"
        if not VOICE_AVAILABLE:
            voice_status += " (Not Available - Install voice libraries)"
        
        voice_radio = tk.Radiobutton(radio_frame, text=voice_status,
                                    variable=self.comm_mode_var, value='voice',
                                    font=('Arial', 12), fg='white', bg='#2c3e50',
                                    selectcolor='#9b59b6', activebackground='#2c3e50',
                                    state='disabled' if not VOICE_AVAILABLE else 'normal')
        voice_radio.pack(pady=10, anchor='w')
        
        # Voice requirements info
        if not VOICE_AVAILABLE:
            voice_info = tk.Label(main_frame, 
                                 text="Voice chat requires: speech_recognition, pyttsx3, pyaudio\nInstall with: pip install speechrecognition pyttsx3 pyaudio", 
                                 font=('Arial', 9, 'italic'), 
                                 fg='#e74c3c', bg='#2c3e50')
            voice_info.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        back_btn = tk.Button(button_frame, text="Back to Hologram",
                           command=self.show_hologram_display,
                           font=('Arial', 12, 'bold'),
                           bg='#7f8c8d', fg='white',
                           padx=20, pady=10)
        back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ok_btn = tk.Button(button_frame, text="OK - Start Chat",
                          command=self.start_chat,
                          font=('Arial', 12, 'bold'),
                          bg='#27ae60', fg='white',
                          padx=20, pady=10)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def start_chat(self):
        """Start the chat interface"""
        self.communication_mode = self.comm_mode_var.get()
        self.chat_history = []
        self.show_chat_interface()
    
    def show_chat_interface(self):
        """Display the chat interface with visible hologram"""
        self.clear_window()
        
        # Create main container with two panes
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - Hologram display
        left_pane = tk.Frame(main_container, bg='#2c3e50', width=350)
        main_container.add(left_pane, minsize=300)
        
        # Hologram title
        hologram_title = tk.Label(left_pane, text=self.current_hologram['name'], 
                                 font=('Arial', 16, 'bold'), 
                                 fg='white', bg='#2c3e50')
        hologram_title.pack(pady=(10, 5))
        
        # Hologram display
        if self.merged_hologram_image or self.cycle_images:
            # Choose initial image
            display_image = None
            if self.cycle_images:
                display_image = self.cycle_images[0].copy()
                self.current_image_index = 0
            elif self.merged_hologram_image:
                display_image = self.merged_hologram_image.copy()
            
            if display_image:
                # Resize for chat interface
                display_image = display_image.resize((280, 280), Image.Resampling.LANCZOS)
                
                self.hologram_photo = ImageTk.PhotoImage(display_image)
                self.hologram_display = tk.Label(left_pane, image=self.hologram_photo, bg='#2c3e50')
                self.hologram_display.pack(pady=10)
                
                # Start image cycling if multiple images
                self.start_image_cycling()
        
        # Personality info
        personality_desc = self.generate_personality_description()
        personality_label = tk.Label(left_pane, text=f"Personality:\n{personality_desc}", 
                                    font=('Arial', 9), 
                                    fg='#bdc3c7', bg='#2c3e50', 
                                    wraplength=280, justify=tk.CENTER)
        personality_label.pack(pady=10)
        
        # Status indicator
        self.status_label = tk.Label(left_pane, text="● Online", 
                                    font=('Arial', 10, 'bold'), 
                                    fg='#2ecc71', bg='#2c3e50')
        self.status_label.pack(pady=5)
        
        # Image cycling info
        if self.cycle_images and len(self.cycle_images) > 1:
            cycle_info = tk.Label(left_pane, 
                                 text=f"Cycling through {len(self.cycle_images)} images", 
                                 font=('Arial', 8, 'italic'), 
                                 fg='#95a5a6', bg='#2c3e50')
            cycle_info.pack(pady=2)
        
        # Right pane - Chat interface
        right_pane = tk.Frame(main_container, bg='#34495e')
        main_container.add(right_pane, minsize=500)
        
        # Chat header
        chat_header = tk.Frame(right_pane, bg='#34495e', height=50)
        chat_header.pack(fill=tk.X, pady=(5, 0))
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(chat_header, text=f"Chat with {self.current_hologram['name']}", 
                             font=('Arial', 14, 'bold'), 
                             fg='white', bg='#34495e')
        chat_title.pack(side=tk.LEFT, padx=15, pady=15)
        
        end_btn = tk.Button(chat_header, text="End Chat",
                           command=self.end_chat,
                           font=('Arial', 9),
                           bg='#e74c3c', fg='white',
                           padx=15, pady=5)
        end_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(right_pane, height=20, width=60,
                                                     font=('Arial', 10),
                                                     bg='#2c3e50', fg='white',
                                                     insertbackground='white')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(right_pane, bg='#34495e')
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.message_entry = tk.Entry(input_frame, font=('Arial', 10),
                                     bg='#2c3e50', fg='white', insertbackground='white')
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        send_btn = tk.Button(input_frame, text="Send",
                           command=self.send_message,
                           font=('Arial', 10),
                           bg='#9b59b6', fg='white',
                           padx=15, pady=5)
        send_btn.pack(side=tk.RIGHT)
        
        # Voice controls (if voice mode and available)
        if self.communication_mode == 'voice' and VOICE_AVAILABLE:
            voice_frame = tk.Frame(right_pane, bg='#34495e')
            voice_frame.pack(fill=tk.X, padx=10, pady=5)
            
            self.record_btn = tk.Button(voice_frame, text="🎤 Record",
                                       command=self.record_voice,
                                       font=('Arial', 9),
                                       bg='#27ae60', fg='white',
                                       padx=10, pady=2)
            self.record_btn.pack(side=tk.LEFT, padx=5)
            
            play_btn = tk.Button(voice_frame, text="🔊 Play Last Response",
                                command=self.play_last_response,
                                font=('Arial', 9),
                                bg='#3498db', fg='white',
                                padx=10, pady=2)
            play_btn.pack(side=tk.LEFT, padx=5)
            
            voice_settings_btn = tk.Button(voice_frame, text="⚙️ Voice Settings",
                                          command=self.show_voice_settings,
                                          font=('Arial', 9),
                                          bg='#9b59b6', fg='white',
                                          padx=10, pady=2)
            voice_settings_btn.pack(side=tk.LEFT, padx=5)

        # Initial message
        self.add_message_to_display("System", "Chat started! Type a message to begin talking with your hologram.")
        if self.communication_mode == 'voice' and VOICE_AVAILABLE:
            self.add_message_to_display("System", "Click the Record button to speak, or type messages normally.")
        elif self.communication_mode == 'voice' and not VOICE_AVAILABLE:
            self.add_message_to_display("System", "Voice mode requested but libraries not available. Using text mode.")
            self.communication_mode = 'text'
        
        self.message_entry.focus()
    
    def end_chat(self):
        """End chat and return to main menu"""
        self.stop_image_cycling()
        self.show_main_menu()
    
    def play_last_response(self):
        """Play the last AI response using text-to-speech"""
        if self.last_ai_response:
            self.speak_text(self.last_ai_response)
        else:
            self.add_message_to_display("System", "No previous response to play.")
    
    def generate_personality_description(self):
        """Generate a description of the hologram's personality"""
        personality = self.current_hologram['personality']
        traits = []
        
        trait_mappings = {
            'friendly': ('distant', 'friendly'),
            'gruff': ('gentle', 'gruff'),
            'extrovert': ('introverted', 'extroverted'),
            'happy': ('sad', 'happy'),
            'confident': ('uncertain', 'confident'),
            'creative': ('practical', 'creative')
        }
        
        for trait, (low_desc, high_desc) in trait_mappings.items():
            value = personality[trait]
            if value >= 7:
                traits.append(f"very {high_desc}")
            elif value >= 5:
                traits.append(high_desc)
            elif value <= 2:
                traits.append(f"quite {low_desc}")
            elif value <= 4:
                traits.append(f"somewhat {low_desc}")
        
        return ', '.join(traits[:3])  # Show only first 3 traits to keep it concise
    
    def add_message_to_display(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "System":
            self.chat_display.insert(tk.END, f"[{sender}] {message}\n\n", 'system')
        elif sender == "You":
            self.chat_display.insert(tk.END, f"{sender}: {message}\n\n", 'user')
        else:
            self.chat_display.insert(tk.END, f"{sender}: {message}\n\n", 'assistant')
        
        # Configure text tags for styling
        self.chat_display.tag_configure('system', foreground='#f39c12')
        self.chat_display.tag_configure('user', foreground='#3498db')
        self.chat_display.tag_configure('assistant', foreground='#2ecc71')
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send message to the hologram"""
        message = self.message_entry.get().strip()
        if not message:
            return
        
        self.message_entry.delete(0, tk.END)
        self.add_message_to_display("You", message)
        
        # Add to chat history
        self.chat_history.append({"role": "user", "content": message})
        
        # Show loading message and update status
        self.add_message_to_display("System", "Thinking...")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="● Thinking...", fg='#f39c12')
        
        # Send to API in separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def get_ai_response(self):
        """Get response from AI (Claude API)"""
        try:
            # NOTE: You need to set your API key as an environment variable
            # export ANTHROPIC_API_KEY="your-api-key-here"
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                error_msg = "Please set your ANTHROPIC_API_KEY environment variable with your Claude API key.\n\nTo get an API key:\n1. Go to https://console.anthropic.com/\n2. Sign up/login\n3. Generate an API key\n4. Set it as environment variable: export ANTHROPIC_API_KEY=\"your-key-here\""
                self.root.after(0, self.handle_ai_response, error_msg)
                return
            
            # Generate personality prompt
            personality_desc = self.generate_personality_description()
            system_prompt = f"""You are {self.current_hologram['name']}, a digital hologram created from uploaded images. 
Your personality traits include: {personality_desc}. 

You should embody these traits in your responses - speak and react according to your personality. 
Keep responses conversational and in character. Remember that you are a hologram created by the user, 
so you can reference this unique nature while staying true to your assigned personality.
You appear as a merged composite of multiple images, creating a unique holographic presence."""

            # Prepare messages for API
            messages = [{"role": "user", "content": system_prompt}]
            messages.extend(self.chat_history[-10:])  # Last 10 messages for context
            
            # Make API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "messages": messages
                },
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_message = response_data["content"][0]["text"]
                
                # Update UI in main thread
                self.root.after(0, self.handle_ai_response, ai_message)
            else:
                error_msg = f"API Error {response.status_code}: {response.text}\n\nMake sure your ANTHROPIC_API_KEY is valid."
                self.root.after(0, self.handle_ai_response, error_msg)
                
        except Exception as e:
            error_msg = f"Connection Error: {str(e)}\n\nCheck your internet connection and API key."
            self.root.after(0, self.handle_ai_response, error_msg)
    
    def handle_ai_response(self, response):
        """Handle the AI response in the main thread"""
        # Update status back to online
        if hasattr(self, 'status_label'):
            self.status_label.config(text="● Online", fg='#2ecc71')
        
        # Remove the "Thinking..." message by clearing and rebuilding
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get(1.0, tk.END)
        
        # Remove last "Thinking..." line
        lines = content.strip().split('\n')
        if lines and "Thinking..." in lines[-1]:
            lines = lines[:-2]  # Remove "Thinking..." and empty line
            self.chat_display.delete(1.0, tk.END)
            if lines:
                self.chat_display.insert(1.0, '\n'.join(lines) + '\n\n')
        
        self.chat_display.config(state=tk.DISABLED)
        
        # Add AI response
        self.add_message_to_display(self.current_hologram['name'], response)
        
        # Store for TTS and add to chat history
        self.last_ai_response = response
        self.chat_history.append({"role": "assistant", "content": response})
        
        # Auto-speak if voice mode
        if self.communication_mode == 'voice' and VOICE_AVAILABLE:
            self.speak_text(response)
    
    def run(self):
        """Start the application"""
        # Check for required voice libraries
        if VOICE_AVAILABLE:
            print("Voice libraries available")
        else:
            print("Voice libraries missing. Install with: pip install speechrecognition pyttsx3 pyaudio")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        self.stop_image_cycling()
        self.root.destroy()

if __name__ == "__main__":
    # Installation instructions:
    # pip install requests pillow speechrecognition pyttsx3 pyaudio
    #
    # API Key setup:
    # 1. Get your Anthropic API key from https://console.anthropic.com/
    # 2. Set environment variable: export ANTHROPIC_API_KEY="your-api-key-here"
    #    On Windows: set ANTHROPIC_API_KEY=your-api-key-here
    #
    # Voice chat requirements:
    # - speechrecognition: For speech-to-text
    # - pyttsx3: For text-to-speech  
    # - pyaudio: For microphone access
    #
    # On macOS you may need: brew install portaudio
    # On Ubuntu: sudo apt-get install python3-pyaudio
    #
    # Run the application:

    app = HologramCreator()
    app.run()



