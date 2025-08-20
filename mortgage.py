import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import math
import csv
import requests
import threading
from datetime import datetime
import os
import webbrowser

class MortgageAI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Mortgage Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Conversation history
        self.messages = []
        self.mortgage_data = None
        self.amortization_schedule = []
        self.manual_mode = False
        
        # Initialize with welcome message
        self.add_message("assistant", 
            "Hello! I'm your mortgage calculator assistant. I can help you calculate your monthly mortgage payment and generate a detailed amortization schedule.\n\n"
            "To get started, I'll need some information from you. What's the home purchase price you're considering?")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title and buttons
        title_label = ttk.Label(header_frame, text="🏠 AI Mortgage Calculator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.export_btn = ttk.Button(button_frame, text="📊 Export to Sheets", 
                                   command=self.export_to_sheets, state='disabled')
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_csv_btn = ttk.Button(button_frame, text="💾 Save CSV", 
                                     command=self.save_csv, state='disabled')
        self.save_csv_btn.pack(side=tk.LEFT)
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20, width=80, 
                                                     wrap=tk.WORD, state='disabled',
                                                     font=('Arial', 10))
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for styling
        self.chat_display.tag_config("user", foreground="blue", font=('Arial', 10, 'bold'))
        self.chat_display.tag_config("assistant", foreground="green", font=('Arial', 10))
        self.chat_display.tag_config("system", foreground="red", font=('Arial', 10, 'italic'))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.user_input = tk.Text(input_frame, height=3, width=70, wrap=tk.WORD)
        self.user_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind Enter key
        self.user_input.bind('<Return>', self.on_enter)
        self.user_input.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for newlines
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Ask me about mortgage calculations!")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief='sunken', anchor='w')
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Summary frame (initially hidden)
        self.summary_frame = ttk.LabelFrame(main_frame, text="Mortgage Summary", padding="5")
        
        self.summary_text = tk.Text(self.summary_frame, height=6, state='disabled', 
                                   bg='#f8f8f8', font=('Arial', 9))
        self.summary_text.pack(fill='both', expand=True)
        
        # Load initial conversation
        self.update_chat_display()
        
    def add_message(self, role, content):
        """Add a message to the conversation history"""
        self.messages.append({"role": role, "content": content})
        
    def update_chat_display(self):
        """Update the chat display with all messages"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        
        for message in self.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                self.chat_display.insert(tk.END, "You: ", "user")
            elif role == "assistant":
                self.chat_display.insert(tk.END, "AI Assistant: ", "assistant")
            else:
                self.chat_display.insert(tk.END, "System: ", "system")
                
            self.chat_display.insert(tk.END, content + "\n\n")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
    def on_enter(self, event):
        """Handle Enter key press"""
        if not event.state & 1:  # If Shift is not pressed
            self.send_message()
            return 'break'  # Prevent default behavior
            
    def send_message(self):
        """Send user message and get AI response"""
        user_message = self.user_input.get(1.0, tk.END).strip()
        if not user_message:
            return
            
        # Check if in manual mode
        if self.manual_mode:
            self.add_message("system", "Manual mode active. Use the form above to calculate mortgage, or restart the application for AI mode.")
            self.user_input.delete(1.0, tk.END)
            self.update_chat_display()
            return
            
        # Add user message
        self.add_message("user", user_message)
        self.user_input.delete(1.0, tk.END)
        self.update_chat_display()
        
        # Set status
        self.status_var.set("Thinking...")
        
        # Get AI response in a separate thread
        thread = threading.Thread(target=self.get_ai_response, args=(user_message,))
        thread.daemon = True
        thread.start()
        
    def get_ai_response(self, user_message):
        """Get response from Claude API"""
        try:
            # Get API key from environment variable or show setup dialog
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                self.root.after(0, self.show_api_key_dialog)
                return
            
            # Prepare the conversation for the API
            api_messages = []
            for msg in self.messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add system context to the last message
            if api_messages:
                api_messages[-1]["content"] += """

IMPORTANT CONTEXT: You are a mortgage calculator assistant. Your goal is to collect the following information from the user:
1. Home purchase price (or loan amount)
2. Down payment amount or percentage
3. Annual interest rate (APR)
4. Loan term in years (typically 15 or 30)

Once you have ALL this information, respond with a JSON object in this EXACT format:
{
  "action": "calculate",
  "purchasePrice": [number],
  "downPayment": [number], 
  "annualRate": [number],
  "loanTermYears": [number]
}

If you don't have all the information yet, continue the conversation naturally to collect the missing details. Be helpful and conversational, but focused on getting these mortgage parameters.

DO NOT OUTPUT ANYTHING OTHER THAN VALID JSON when you have all the required information. The JSON should be the entire response with no additional text or markdown formatting."""
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": "claude-4-sonnet-20250514",  # Use a stable model
                    "max_tokens": 1000,
                    "messages": api_messages
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_response = data['content'][0]['text']
                
                # Check if response is JSON (calculation ready)
                try:
                    parsed = json.loads(assistant_response)
                    if parsed.get("action") == "calculate":
                        self.root.after(0, lambda: self.process_calculation(parsed))
                        return
                except json.JSONDecodeError:
                    pass
                
                # Regular conversation response
                self.root.after(0, lambda: self.handle_ai_response(assistant_response))
                
            else:
                error_data = response.json() if response.content else {}
                error_msg = f"API Error {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}"
                self.root.after(0, lambda: self.handle_ai_response(error_msg))
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. Please try again."
            self.root.after(0, lambda: self.handle_ai_response(error_msg))
        except requests.exceptions.RequestException as e:
            error_msg = f"Network Error: {str(e)}"
            self.root.after(0, lambda: self.handle_ai_response(error_msg))
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.handle_ai_response(error_msg))
            
    def handle_ai_response(self, response):
        """Handle AI response in the main thread"""
        self.add_message("assistant", response)
        self.update_chat_display()
        self.status_var.set("Ready")
        
    def show_api_key_dialog(self):
        """Show dialog to enter API key or use manual mode"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API Configuration")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Anthropic API Key Required", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        info_text = """To use the AI assistant, you need an Anthropic API key.

1. Get your API key from: https://console.anthropic.com/
2. Set it as environment variable: ANTHROPIC_API_KEY=your_key_here
3. Or enter it below (not recommended for production)

Alternatively, you can use Manual Mode to calculate mortgages without AI."""
        
        ttk.Label(frame, text=info_text, wraplength=450).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(frame, text="Enter API Key (optional):").pack(anchor='w')
        api_key_var = tk.StringVar()
        api_entry = ttk.Entry(frame, textvariable=api_key_var, width=60, show="*")
        api_entry.pack(fill='x', pady=(5, 10))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def use_api_key():
            key = api_key_var.get().strip()
            if key:
                os.environ['ANTHROPIC_API_KEY'] = key
                dialog.destroy()
                self.status_var.set("API key set - AI mode enabled")
            else:
                messagebox.showwarning("Warning", "Please enter an API key")
        
        def use_manual_mode():
            dialog.destroy()
            self.enable_manual_mode()
            
        def open_console():
            webbrowser.open("https://console.anthropic.com/")
            
        ttk.Button(button_frame, text="Set API Key", command=use_api_key).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Use Manual Mode", command=use_manual_mode).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Get API Key", command=open_console).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='right')
        
        self.status_var.set("API key required for AI mode")
        
    def enable_manual_mode(self):
        """Enable manual mortgage calculation mode"""
        self.manual_mode = True
        self.add_message("system", "Manual Mode Enabled - AI features disabled. You can still calculate mortgages using the manual input form.")
        
        # Show manual input form
        self.show_manual_input_form()
        self.update_chat_display()
        self.status_var.set("Manual mode - Enter mortgage details below")
        
    def show_manual_input_form(self):
        """Show manual mortgage input form"""
        # Manual input frame
        self.manual_frame = ttk.LabelFrame(self.root, text="Manual Mortgage Calculator", padding="10")
        self.manual_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Input fields
        fields_frame = ttk.Frame(self.manual_frame)
        fields_frame.pack(fill='x')
        
        # Purchase Price
        ttk.Label(fields_frame, text="Purchase Price ($):").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.purchase_price_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.purchase_price_var, width=15).grid(row=0, column=1, padx=5)
        
        # Down Payment
        ttk.Label(fields_frame, text="Down Payment ($):").grid(row=0, column=2, sticky='w', padx=(10, 5))
        self.down_payment_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.down_payment_var, width=15).grid(row=0, column=3, padx=5)
        
        # Interest Rate
        ttk.Label(fields_frame, text="Interest Rate (%):").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.interest_rate_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.interest_rate_var, width=15).grid(row=1, column=1, padx=5, pady=(5, 0))
        
        # Loan Term
        ttk.Label(fields_frame, text="Loan Term (years):").grid(row=1, column=2, sticky='w', padx=(10, 5), pady=(5, 0))
        self.loan_term_var = tk.StringVar(value="30")
        ttk.Entry(fields_frame, textvariable=self.loan_term_var, width=15).grid(row=1, column=3, padx=5, pady=(5, 0))
        
        # Calculate button
        calc_btn = ttk.Button(self.manual_frame, text="Calculate Mortgage", 
                             command=self.manual_calculate)
        calc_btn.pack(pady=10)
        
    def manual_calculate(self):
        """Calculate mortgage manually"""
        try:
            purchase_price = float(self.purchase_price_var.get().replace(',', ''))
            down_payment = float(self.down_payment_var.get().replace(',', ''))
            annual_rate = float(self.interest_rate_var.get())
            loan_term_years = int(self.loan_term_var.get())
            
            if purchase_price <= 0 or down_payment < 0 or annual_rate < 0 or loan_term_years <= 0:
                raise ValueError("Invalid input values")
                
            if down_payment >= purchase_price:
                raise ValueError("Down payment cannot be greater than purchase price")
            
            # Calculate mortgage
            calc_data = {
                "purchasePrice": purchase_price,
                "downPayment": down_payment,
                "annualRate": annual_rate,
                "loanTermYears": loan_term_years
            }
            
            self.process_calculation(calc_data)
            
        except ValueError as e:
            if "could not convert" in str(e):
                messagebox.showerror("Error", "Please enter valid numeric values")
            else:
                messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
            
    def process_calculation(self, calc_data):
        """Process mortgage calculation"""
        try:
            results = self.calculate_mortgage(
                calc_data["purchasePrice"],
                calc_data["annualRate"], 
                calc_data["loanTermYears"],
                calc_data["downPayment"]
            )
            
            self.mortgage_data = {
                "purchasePrice": calc_data["purchasePrice"],
                "downPayment": calc_data["downPayment"],
                "loanAmount": results["loanAmount"],
                "annualRate": calc_data["annualRate"],
                "loanTermYears": calc_data["loanTermYears"],
                "monthlyPayment": results["monthlyPayment"],
                "totalInterest": results["totalInterest"],
                "totalPayments": results["totalPayments"]
            }
            
            self.amortization_schedule = results["schedule"]
            
            # Create summary message
            summary_msg = f"""Perfect! I've calculated your mortgage details:

**Mortgage Summary:**
- Purchase Price: ${calc_data["purchasePrice"]:,.2f}
- Down Payment: ${calc_data["downPayment"]:,.2f}
- Loan Amount: ${results["loanAmount"]:,.2f}
- Interest Rate: {calc_data["annualRate"]}% APR
- Loan Term: {calc_data["loanTermYears"]} years
- **Monthly Payment: ${results["monthlyPayment"]:,.2f}**
- Total Interest: ${results["totalInterest"]:,.2f}
- Total Amount Paid: ${results["totalPayments"]:,.2f}

I've also generated a complete {calc_data["loanTermYears"] * 12}-month amortization schedule showing the principal and interest breakdown for each payment. You can now export this data to Google Sheets or save as CSV!"""
            
            self.add_message("assistant", summary_msg)
            self.update_chat_display()
            
            # Enable export buttons
            self.export_btn.config(state='normal')
            self.save_csv_btn.config(state='normal')
            
            # Show summary panel
            self.show_summary()
            
            self.status_var.set("Calculation complete - Ready to export!")
            
        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            self.add_message("assistant", error_msg)
            self.update_chat_display()
            self.status_var.set("Error in calculation")
            
    def calculate_mortgage(self, principal, annual_rate, years, down_payment):
        """Calculate mortgage payments and amortization schedule"""
        loan_amount = principal - down_payment
        monthly_rate = annual_rate / 100 / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            monthly_payment = loan_amount / num_payments
            total_interest = 0
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            total_interest = (monthly_payment * num_payments) - loan_amount
        
        # Generate amortization schedule
        remaining_balance = loan_amount
        schedule = []
        total_interest_paid = 0
        
        for month in range(1, num_payments + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance = max(0, remaining_balance - principal_payment)
            total_interest_paid += interest_payment
            
            schedule.append({
                "month": month,
                "monthlyPayment": monthly_payment,
                "principalPayment": principal_payment,
                "interestPayment": interest_payment,
                "remainingBalance": remaining_balance
            })
        
        return {
            "monthlyPayment": monthly_payment,
            "loanAmount": loan_amount,
            "totalInterest": total_interest_paid,
            "totalPayments": monthly_payment * num_payments,
            "schedule": schedule
        }
        
    def show_summary(self):
        """Show mortgage summary panel"""
        if not self.mortgage_data:
            return
            
        self.summary_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        summary_text = f"""Purchase Price: ${self.mortgage_data["purchasePrice"]:,.2f}    Down Payment: ${self.mortgage_data["downPayment"]:,.2f}    Loan Amount: ${self.mortgage_data["loanAmount"]:,.2f}
Interest Rate: {self.mortgage_data["annualRate"]}% APR    Loan Term: {self.mortgage_data["loanTermYears"]} years    Payments: {len(self.amortization_schedule)}

MONTHLY PAYMENT: ${self.mortgage_data["monthlyPayment"]:,.2f}
Total Interest: ${self.mortgage_data["totalInterest"]:,.2f}    Total Paid: ${self.mortgage_data["totalPayments"]:,.2f}"""
        
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary_text)
        self.summary_text.config(state='disabled')
        
    def save_csv(self):
        """Save mortgage data as CSV"""
        if not self.mortgage_data or not self.amortization_schedule:
            messagebox.showwarning("Warning", "No mortgage data to save")
            return
            
#        filename = filedialog.asksaveasfilename(
#            defaultextension=".csv",
#            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
#            title="Save Mortgage Calculation",
#            initialname=f"mortgage_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#        )
 
        filename = "test.csv"
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write summary
                    writer.writerow(["Mortgage Summary"])
                    writer.writerow(["Purchase Price", self.mortgage_data["purchasePrice"]])
                    writer.writerow(["Down Payment", self.mortgage_data["downPayment"]])
                    writer.writerow(["Loan Amount", self.mortgage_data["loanAmount"]])
                    writer.writerow(["Interest Rate (%)", self.mortgage_data["annualRate"]])
                    writer.writerow(["Loan Term (years)", self.mortgage_data["loanTermYears"]])
                    writer.writerow(["Monthly Payment", f"{self.mortgage_data['monthlyPayment']:.2f}"])
                    writer.writerow(["Total Interest", f"{self.mortgage_data['totalInterest']:.2f}"])
                    writer.writerow(["Total Payments", f"{self.mortgage_data['totalPayments']:.2f}"])
                    writer.writerow([])
                    
                    # Write amortization schedule header
                    writer.writerow(["Amortization Schedule"])
                    writer.writerow(["Month", "Monthly Payment", "Principal", "Interest", "Remaining Balance"])
                    
                    # Write schedule data
                    for payment in self.amortization_schedule:
                        writer.writerow([
                            payment["month"],
                            f"{payment['monthlyPayment']:.2f}",
                            f"{payment['principalPayment']:.2f}",
                            f"{payment['interestPayment']:.2f}",
                            f"{payment['remainingBalance']:.2f}"
                        ])
                
                messagebox.showinfo("Success", f"Mortgage calculation saved to:\n{filename}")
                self.status_var.set("CSV file saved successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                
    def export_to_sheets(self):
        """Export to Google Sheets (or show instructions)"""
        if not self.mortgage_data or not self.amortization_schedule:
            messagebox.showwarning("Warning", "No mortgage data to export")
            return
            
        # For this demo, we'll show instructions for Google Sheets integration
        instructions = """To export to Google Sheets, you have several options:

1. MANUAL UPLOAD (Recommended):
   • Save as CSV first using the 'Save CSV' button
   • Go to sheets.google.com
   • Create a new spreadsheet
   • File → Import → Upload → Select your CSV file

2. GOOGLE APPS SCRIPT:
   • Use Google Apps Script to create a web app
   • Connect to this application via HTTP requests
   • Automatically create and populate spreadsheets

3. GOOGLE SHEETS API:
   • Set up Google Cloud Project with Sheets API
   • Configure OAuth2 credentials
   • Use gspread or google-api-python-client libraries

Would you like me to save the CSV file for manual upload?"""
        
        result = messagebox.askyesnocancel("Google Sheets Export", 
                                          instructions + "\n\nClick 'Yes' to save CSV for manual upload, 'No' to see API setup info, or 'Cancel' to close.")
        
        if result is True:
            self.save_csv()
        elif result is False:
            self.show_api_setup_info()
            
    def show_api_setup_info(self):
        """Show Google Sheets API setup information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Google Sheets API Setup")
        info_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        
        setup_info = """Google Sheets API Setup Instructions:

1. GOOGLE CLOUD SETUP:
   • Go to console.cloud.google.com
   • Create a new project or select existing one
   • Enable Google Sheets API
   • Create credentials (OAuth 2.0 or Service Account)

2. INSTALL REQUIRED PACKAGES:
   pip install gspread google-auth google-auth-oauthlib

3. AUTHENTICATION:
   • Download credentials JSON file
   • Place in your project directory
   • Update code with credentials path

4. SAMPLE CODE TO ADD:
   
import gspread
from google.oauth2.service_account import Credentials

def export_to_google_sheets(self):
    # Setup credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # Create new spreadsheet
    title = f"Mortgage Calculation - {datetime.now().strftime('%Y-%m-%d')}"
    sheet = client.create(title)
    worksheet = sheet.sheet1
    
    # Prepare data
    data = [
        ["Mortgage Summary", ""],
        ["Purchase Price", self.mortgage_data["purchasePrice"]],
        ["Down Payment", self.mortgage_data["downPayment"]],
        # ... add all summary data
        ["", ""],
        ["Amortization Schedule", ""],
        ["Month", "Monthly Payment", "Principal", "Interest", "Remaining Balance"]
    ]
    
    # Add amortization schedule
    for payment in self.amortization_schedule:
        data.append([
            payment["month"],
            payment["monthlyPayment"],
            payment["principalPayment"],
            payment["interestPayment"],
            payment["remainingBalance"]
        ])
    
    # Write to sheet
    worksheet.update("A1", data)
    
    # Open in browser
    webbrowser.open(sheet.url)

5. SECURITY NOTES:
   • Keep credentials file secure
   • Don't commit credentials to version control
   • Consider using environment variables for production

For a complete implementation, you would replace the export_to_sheets method
with the code above after setting up your Google Cloud credentials."""
        
        text_widget.insert(1.0, setup_info)
        text_widget.config(state='disabled')
        
        close_btn = ttk.Button(info_window, text="Close", command=info_window.destroy)
        close_btn.pack(pady=10)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MortgageAI()
    app.run()


