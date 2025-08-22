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
            # Prepare messages for API - include system prompt for first message
            messages = []
            
            # Add system context if this is the start or continuation
            if not any(msg.get("role") == "assistant" for msg in self.conversation_history[-5:]):
                system_prompt = """You are a professional financial advisor. Provide comprehensive, personalized financial advice based on the client's situation. Ask relevant questions about their income, expenses, goals, risk tolerance, current investments, debts, and financial timeline. Give specific, actionable recommendations while being thorough and professional. Always prioritize the client's best interests and provide educational explanations for your advice."""
                messages.append({
                    "role": "user",
                    "content": f"System instructions: {system_prompt}\n\nClient interaction begins now."
                })
            
            # Add conversation history
            for msg in self.conversation_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # API request with correct headers
            headers = {
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": self.api_key
            }
            
            # Try current model first, fallback to older version if needed
            models_to_try = [
                "claude-3-5-sonnet-20241022",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ]
            
            last_error = None
            for model_name in models_to_try:
                try:
                    data = {
                        "model": model_name,
                        "max_tokens": 1500,
                        "messages": messages
                    }
                    
                    print(f"Trying model: {model_name}")  # Debug
                    print(f"Making API request to: {self.api_url}")  # Debug
                    
                    response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                    
                    print(f"Response status: {response.status_code}")  # Debug
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result['content'][0]['text']
                        self.response_queue.put(("success", ai_response))
                        return
                    elif response.status_code == 404:
                        print(f"Model {model_name} not found, trying next...")
                        continue
                    else:
                        response.raise_for_status()
                        
                except requests.exceptions.RequestException as e:
                    last_error = e
                    if hasattr(e, 'response') and e.response and e.response.status_code == 404:
                        continue  # Try next model
                    else:
                        break  # Other error, don't try more models
            
            # If we get here, all models failed
            error_msg = "All models failed. "
            if last_error:
                error_msg += f"Last error: {str(last_error)}"
                if hasattr(last_error, 'response') and last_error.response is not None:
                    try:
                        error_detail = last_error.response.json()
                        error_msg += f"\nDetails: {error_detail}"
                    except:
                        error_msg += f"\nResponse: {last_error.response.text}"
            
            self.response_queue.put(("error", error_msg))
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request Error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\nDetails: {error_detail}"
                except:
                    error_msg += f"\nResponse: {e.response.text}"
            self.response_queue.put(("error", error_msg))
        except Exception as e:
            self.response_queue.put(("error", f"Unexpected error: {str(e)}"))
    
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
        if not self.conversation_history or len([msg for msg in self.conversation_history if msg.get("role") == "assistant"]) == 0:
            # New consultation - start with AI introduction
            self.status_label.config(text="Starting consultation...")
            self.send_button.config(state='disabled')
            
            # Add initial system context to conversation history
            initial_context = "Please start our financial consultation session. Introduce yourself as a professional financial advisor and begin gathering my financial information with appropriate questions."
            self.conversation_history.append({
                "role": "user", 
                "content": initial_context,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI's opening response
            threading.Thread(target=self.get_ai_response, daemon=True).start()
            self.root.after(100, self.check_response_queue)
            
        else:
            # Continuing previous consultation
            self.display_message("System", "Continuing previous consultation...")
            
            # Display recent conversation history
            recent_messages = self.conversation_history[-10:]  # Show last 10 messages
            for msg in recent_messages:
                role = "You" if msg["role"] == "user" else "Financial Advisor"
                if msg["content"] != "Please start our financial consultation session. Introduce yourself as a professional financial advisor and begin gathering my financial information with appropriate questions.":
                    self.display_message(role, msg["content"])
            
            # Display existing advice
            for advice_item in self.advice_log:
                timestamp = datetime.fromisoformat(advice_item["timestamp"]).strftime("%H:%M")
                advice_text = f"\n[{timestamp}] KEY ADVICE:\n• " + "\n• ".join(advice_item["advice"]) + "\n" + "-"*40 + "\n"
                self.advice_text.insert(tk.END, advice_text)
            
            self.advice_text.see(tk.END)
    
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
        from reportlab.platypus import PageBreak, Image
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics import renderPDF
        from reportlab.lib.pagesizes import letter
        import io
        
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceBefore=25,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.darkblue,
            borderPadding=5,
            backColor=colors.lightblue,
            leftIndent=10,
            rightIndent=10
        )
        
        advice_style = ParagraphStyle(
            'AdviceStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=8,
            leftIndent=20,
            rightIndent=10,
            fontName='Helvetica',
            leading=16
        )
        
        conversation_header_style = ParagraphStyle(
            'ConversationHeader',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=5,
            textColor=colors.darkgreen,
            backColor=colors.lightgrey,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.grey
        )
        
        conversation_text_style = ParagraphStyle(
            'ConversationText',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceBefore=5,
            spaceAfter=10,
            leftIndent=15,
            rightIndent=15,
            alignment=TA_JUSTIFY,
            leading=14
        )
        
        # Header with logo placeholder (you can add actual logo later)
        header_drawing = Drawing(400, 60)
        header_drawing.add(Rect(0, 20, 400, 30, fillColor=colors.darkblue, strokeColor=colors.darkblue))
        header_drawing.add(String(200, 35, 'FINANCIAL ADVISORY SERVICES', 
                                fontSize=16, fillColor=colors.white, textAnchor='middle', fontName='Helvetica-Bold'))
        story.append(header_drawing)
        story.append(Spacer(1, 20))
        
        # Title section
        story.append(Paragraph("Personal Financial Consultation Report", title_style))
        
        # Create a decorative line
        line_drawing = Drawing(500, 10)
        line_drawing.add(Rect(0, 4, 500, 2, fillColor=colors.darkblue, strokeColor=colors.darkblue))
        story.append(line_drawing)
        story.append(Spacer(1, 15))
        
        # Date and session info in a box
        date_table_data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Session ID:', self.session_id],
            ['Consultation Type:', 'Comprehensive Financial Planning']
        ]
        
        date_table = Table(date_table_data, colWidths=[2*inch, 4*inch])
        date_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(date_table)
        story.append(Spacer(1, 30))
        
        # Executive Summary box
        if self.advice_log:
            story.append(Paragraph("Executive Summary of Recommendations", section_header_style))
            story.append(Spacer(1, 10))
            
            # Create a summary box
            summary_data = []
            advice_count = 1
            for advice_item in self.advice_log:
                for advice in advice_item['advice']:
                    if advice.strip():  # Only add non-empty advice
                        summary_data.append([f"{advice_count}.", advice.strip()])
                        advice_count += 1
            
            if summary_data:
                summary_table = Table(summary_data, colWidths=[0.5*inch, 5.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('GRID', (0, 0), (-1, -1), 1, colors.orange),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(summary_table)
            
            story.append(Spacer(1, 30))
        
        # Add a page break before detailed conversation
        story.append(PageBreak())
        
        # Detailed Consultation section
        story.append(Paragraph("Detailed Consultation Transcript", section_header_style))
        story.append(Spacer(1, 15))
        
        # Add consultation explanation
        explanation_text = """This section contains the complete record of our financial consultation session. 
        Each exchange has been documented to provide a comprehensive overview of your financial situation, 
        goals, and the personalized recommendations provided."""
        
        explanation_style = ParagraphStyle(
            'Explanation',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=colors.grey,
            alignment=TA_JUSTIFY,
            spaceBefore=5,
            spaceAfter=15,
            leftIndent=10,
            rightIndent=10
        )
        
        story.append(Paragraph(explanation_text, explanation_style))
        story.append(Spacer(1, 15))
        
        # Process conversation history
        for i, msg in enumerate(self.conversation_history):
            # Skip system messages
            if msg.get("content", "").startswith("System instructions:") or \
               msg.get("content", "").startswith("Please start our financial"):
                continue
                
            role = "CLIENT" if msg["role"] == "user" else "FINANCIAL ADVISOR"
            timestamp = msg.get("timestamp", "")
            
            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%I:%M %p")
                except:
                    formatted_time = ""
            else:
                formatted_time = ""
            
            # Role header with styling
            header_text = f"{role}"
            if formatted_time:
                header_text += f" ({formatted_time})"
            
            # Different colors for client vs advisor
            if role == "CLIENT":
                header_color = colors.darkgreen
                bg_color = colors.lightgreen
            else:
                header_color = colors.darkblue
                bg_color = colors.lightblue
            
            role_style = ParagraphStyle(
                'RoleStyleCustom',
                parent=conversation_header_style,
                textColor=header_color,
                backColor=bg_color
            )
            
            story.append(Paragraph(header_text, role_style))
            
            # Message content with proper formatting
            content = msg["content"].replace('\n', '<br/>')
            story.append(Paragraph(content, conversation_text_style))
            story.append(Spacer(1, 10))
            
            # Add separator line between exchanges
            if i < len(self.conversation_history) - 1:
                separator = Drawing(500, 5)
                separator.add(Rect(0, 2, 500, 1, fillColor=colors.lightgrey, strokeColor=colors.lightgrey))
                story.append(separator)
                story.append(Spacer(1, 5))
        
        # Footer section
        story.append(Spacer(1, 20))
        footer_drawing = Drawing(500, 40)
        footer_drawing.add(Rect(0, 10, 500, 25, fillColor=colors.darkblue, strokeColor=colors.darkblue))
        footer_drawing.add(String(250, 22, 'Thank you for choosing our AI Financial Advisory Services', 
                                fontSize=12, fillColor=colors.white, textAnchor='middle', fontName='Helvetica-Bold'))
        footer_drawing.add(String(250, 8, 'This report is confidential and prepared exclusively for the named client', 
                                fontSize=8, fillColor=colors.white, textAnchor='middle', fontName='Helvetica'))
        story.append(footer_drawing)
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Oblique',
            textColor=colors.grey,
            alignment=TA_JUSTIFY,
            spaceBefore=15,
            leftIndent=10,
            rightIndent=10
        )
        
        disclaimer_text = """<b>Important Disclaimer:</b> This financial advice is generated by an AI system and should be considered as general guidance only. 
        Please consult with a qualified financial advisor or professional before making any significant financial decisions. 
        The AI advisor does not guarantee investment performance or outcomes."""
        
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Build the PDF
        doc.build(story)
        print(f"Professional PDF report created: {filename}")

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



