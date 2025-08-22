import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import csv
import os
from datetime import datetime
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import threading
import queue

class FinancialAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Financial Advisor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.conversation_history = []
        self.financial_data = {}
        self.advice_log = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_file = "financial_consultation_history.json"
        
        # API configuration
        self.api_key = None
        self.api_url = "https://api.anthropic.com/v1/messages"
        
        # Threading
        self.response_queue = queue.Queue()
        
        # Check API key and load data
        if not self.check_api_key():
            return
            
        self.load_conversation_history()
        self.setup_ui()
        self.start_consultation()
        
    def check_api_key(self):
        """Check for API key in environment variables or prompt user"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            # Create a simple dialog to get API key
            api_dialog = tk.Toplevel(self.root)
            api_dialog.title("API Key Required")
            api_dialog.geometry("400x150")
            api_dialog.transient(self.root)
            api_dialog.grab_set()
            
            tk.Label(api_dialog, text="Please enter your Anthropic API key:", 
                    font=('Arial', 12)).pack(pady=10)
            
            key_entry = tk.Entry(api_dialog, width=50, show="*")
            key_entry.pack(pady=5)
            
            def save_key():
                key = key_entry.get().strip()
                if key:
                    self.api_key = key
                    api_dialog.destroy()
                else:
                    messagebox.showerror("Error", "API key cannot be empty")
            
            tk.Button(api_dialog, text="Save", command=save_key).pack(pady=10)
            
            self.root.wait_window(api_dialog)
            
        if not self.api_key:
            messagebox.showerror("Error", "API key is required to run the application")
            self.root.destroy()
            return False
            
        return True
    
    def load_conversation_history(self):
        """Load previous conversation history from JSON file"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversation_history', [])
                    self.financial_data = data.get('financial_data', {})
                    self.advice_log = data.get('advice_log', [])
                print("Loaded previous conversation history")
            except Exception as e:
                print(f"Error loading conversation history: {e}")
                
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Main conversation
        left_frame = ttk.LabelFrame(main_frame, text="Financial Consultation", padding="5")
        left_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.conversation_text = scrolledtext.ScrolledText(
            left_frame, 
            wrap=tk.WORD, 
            font=('Arial', 11),
            height=25
        )
        self.conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input panel
        input_frame = ttk.LabelFrame(main_frame, text="Your Response", padding="5")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = tk.Text(input_frame, height=3, font=('Arial', 11))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_text.bind('<Return>', self.send_response_enter)
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.send_button = ttk.Button(button_frame, text="Send", command=self.send_response)
        self.send_button.pack(pady=2)
        
        # Right panel - Live advice
        right_frame = ttk.LabelFrame(main_frame, text="Live Analysis & Advice", padding="5")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.advice_text = scrolledtext.ScrolledText(
            right_frame, 
            wrap=tk.WORD, 
            font=('Arial', 10),
            width=40,
            bg='#f0f8ff'
        )
        self.advice_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.end_button = ttk.Button(control_frame, text="End Consultation", command=self.end_consultation)
        self.end_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(control_frame, text="Export Data", command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)
        
    def send_response_enter(self, event):
        """Handle Enter key press"""
        if event.state & 0x4:  # Ctrl+Enter
            self.send_response()
            return "break"
            
    def send_response(self):
        """Send user response and get AI reply"""
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
            
        # Display user input
        self.display_message("You", user_input)
        self.input_text.delete("1.0", tk.END)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()})
        
        # Get AI response in separate thread
        self.status_label.config(text="AI is thinking...")
        self.send_button.config(state='disabled')
        
        threading.Thread(target=self.get_ai_response, daemon=True).start()
        self.root.after(100, self.check_response_queue)
        
    def get_ai_response(self):
        """Get response from AI in separate thread"""
        try:
            # Prepare messages for API
            messages = []
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # API request
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": messages
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['content'][0]['text']
            
            self.response_queue.put(("success", ai_response))
            
        except Exception as e:
            self.response_queue.put(("error", str(e)))
    
    def check_response_queue(self):
        """Check for AI response"""
        try:
            status, response = self.response_queue.get_nowait()
            
            if status == "success":
                self.display_message("Financial Advisor", response)
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": response, 
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate live advice
                self.generate_live_advice(response)
                
            else:
                messagebox.showerror("Error", f"AI Response Error: {response}")
                
            self.status_label.config(text="Ready")
            self.send_button.config(state='normal')
            
        except queue.Empty:
            self.root.after(100, self.check_response_queue)
    
    def display_message(self, sender, message):
        """Display message in conversation panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_text.insert(tk.END, f"\n[{timestamp}] {sender}:\n{message}\n" + "-"*80 + "\n")
        self.conversation_text.see(tk.END)
        
    def generate_live_advice(self, ai_response):
        """Generate and display live advice based on AI response"""
        # Simple keyword-based advice extraction (in real implementation, this could be more sophisticated)
        advice_keywords = ['recommend', 'suggest', 'advice', 'should', 'consider', 'important']
        
        sentences = ai_response.split('.')
        advice_sentences = [s.strip() for s in sentences if any(keyword in s.lower() for keyword in advice_keywords)]
        
        if advice_sentences:
            timestamp = datetime.now().strftime("%H:%M")
            advice_text = f"\n[{timestamp}] KEY ADVICE:\n" + "\n• ".join(advice_sentences) + "\n" + "-"*40 + "\n"
            
            self.advice_text.insert(tk.END, advice_text)
            self.advice_text.see(tk.END)
            
            # Store advice
            self.advice_log.append({
                "timestamp": datetime.now().isoformat(),
                "advice": advice_sentences
            })
    
    def start_consultation(self):
        """Start the financial consultation"""
        if not self.conversation_history:
            # New consultation
            welcome_msg = """Welcome to your AI Financial Advisor consultation!

I'm here to help you with comprehensive financial planning. To provide you with the best advice, I'll need to understand your current financial situation, goals, and preferences.

Let's start with some basic information:

1. What is your current age and employment status?
2. What are your primary financial goals (e.g., retirement planning, buying a home, debt reduction, investment growth)?
3. What is your approximate annual income and monthly expenses?

Please feel free to share as much or as little as you're comfortable with. All information will be kept confidential and used solely for providing you with personalized financial advice."""
            
            self.display_message("Financial Advisor", welcome_msg)
            self.conversation_history.append({
                "role": "assistant", 
                "content": welcome_msg,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Continuing previous consultation
            self.display_message("System", "Continuing previous consultation...")
            
            # Display previous conversation
            for msg in self.conversation_history[-5:]:  # Show last 5 messages
                role = "You" if msg["role"] == "user" else "Financial Advisor"
                self.display_message(role, msg["content"])
    
    def end_consultation(self):
        """End consultation and save data"""
        if messagebox.askyesno("End Consultation", "Are you sure you want to end the consultation?"):
            self.save_data()
            self.export_data()
            messagebox.showinfo("Consultation Ended", "Thank you for using AI Financial Advisor!\n\nYour data has been saved and exported.")
            self.root.destroy()
    
    def save_data(self):
        """Save conversation data to JSON file"""
        data = {
            "session_id": self.session_id,
            "last_updated": datetime.now().isoformat(),
            "conversation_history": self.conversation_history,
            "financial_data": self.financial_data,
            "advice_log": self.advice_log
        }
        
        try:
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data saved to {self.json_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def export_data(self):
        """Export data to CSV and PDF"""
        try:
            # CSV Export
            csv_file = f"financial_consultation_{self.session_id}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Speaker", "Message"])
                
                for msg in self.conversation_history:
                    role = "Client" if msg["role"] == "user" else "Financial Advisor"
                    writer.writerow([msg.get("timestamp", ""), role, msg["content"]])
            
            # PDF Export
            pdf_file = f"financial_advice_report_{self.session_id}.pdf"
            self.create_pdf_report(pdf_file)
            
            messagebox.showinfo("Export Complete", f"Data exported to:\n• {csv_file}\n• {pdf_file}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {e}")
    
    def create_pdf_report(self, filename):
        """Create a formatted PDF report"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Financial Consultation Report", title_style))
        story.append(Spacer(1, 12))
        
        # Date
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Session ID: {self.session_id}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Summary of Advice
        if self.advice_log:
            story.append(Paragraph("Key Recommendations Summary:", styles['Heading2']))
            for i, advice_item in enumerate(self.advice_log, 1):
                for advice in advice_item['advice']:
                    story.append(Paragraph(f"• {advice}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Conversation History
        story.append(Paragraph("Consultation Transcript:", styles['Heading2']))
        
        for msg in self.conversation_history:
            role = "Client" if msg["role"] == "user" else "Financial Advisor"
            timestamp = msg.get("timestamp", "")
            
            # Role and timestamp
            role_style = ParagraphStyle(
                'RoleStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.blue if role == "Financial Advisor" else colors.darkgreen,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"{role} ({timestamp}):", role_style))
            story.append(Paragraph(msg["content"], styles['Normal']))
            story.append(Spacer(1, 6))
        
        doc.build(story)

def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = FinancialAdvisorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



