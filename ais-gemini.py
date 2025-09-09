import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
import tkinter.scrolledtext as st

class LifeInsuranceApp:
    def __init__(self, root):
        """
        Initialize the Life Insurance Approval System application.
        """
        self.root = root
        self.root.title("Life Insurance Approval System")
        self.root.geometry("850x1250")

        # Style configuration
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure("TLabel", font=("Helvetica", 11))
        self.style.configure("TEntry", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), padding=10)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

        # Initialize dictionaries to store widgets
        self.entries = {}
        self.text_areas = {}

        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Input Section ---
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        header_label = ttk.Label(input_frame, text="Applicant Information", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20), sticky="w")

        # Applicant Details
        self.create_entry(input_frame, "Full Name:", 1, 0)
        self.create_entry(input_frame, "Age:", 2, 0)
        self.create_entry(input_frame, "Requested Amount ($):", 3, 0)
        self.create_entry(input_frame, "Policy Term (Years):", 4, 0)
        self.create_entry(input_frame, "Occupation:", 5, 0)

        # Health Details
        self.create_entry(input_frame, "Systolic Blood Pressure:", 1, 2)
        self.create_entry(input_frame, "Diastolic Blood Pressure:", 2, 2)
        
        # --- Height Input (ft/in) ---
        ttk.Label(input_frame, text="Height:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        height_sub_frame = ttk.Frame(input_frame)
        height_sub_frame.grid(row=3, column=3, sticky="ew")
        
        self.entries["Height (ft):"] = ttk.Entry(height_sub_frame, width=10)
        self.entries["Height (ft):"].pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(height_sub_frame, text="ft").pack(side=tk.LEFT, padx=(0, 5))
        
        self.entries["Height (in):"] = ttk.Entry(height_sub_frame, width=10)
        self.entries["Height (in):"].pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(height_sub_frame, text="in").pack(side=tk.LEFT)

        self.create_entry(input_frame, "Weight (lbs):", 4, 2)

        # Checkboxes and Text Areas for more complex info
        self.create_check_and_text(main_frame, "Pre-existing Conditions (e.g., Diabetes, Heart Disease):", 6)
        self.create_check_and_text(main_frame, "Family History of Major Illness:", 7)
        self.create_check_and_text(main_frame, "Current Medications:", 8)
        self.create_check_and_text(main_frame, "Previous Surgeries:", 9)
        
        # --- Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.submit_button = ttk.Button(button_frame, text="Submit for Review", command=self.generate_report)
        self.submit_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.print_button = ttk.Button(button_frame, text="Print Report", command=self.print_report, state=tk.DISABLED)
        self.print_button.grid(row=0, column=1, padx=5, sticky="ew")

        # --- Report Section ---
        report_frame = ttk.Frame(main_frame)
        report_frame.pack(expand=True, fill=tk.BOTH)

        report_header = ttk.Label(report_frame, text="Approval Report", style="Header.TLabel")
        report_header.pack(anchor="w", pady=(0, 10))
        
        self.report_text = st.ScrolledText(report_frame, height=15, wrap=tk.WORD, font=("Courier", 10), state=tk.DISABLED, bg="#ffffff", relief=tk.SOLID, borderwidth=1)
        self.report_text.pack(expand=True, fill=tk.BOTH)

    def create_entry(self, parent, label_text, row, col):
        """Helper to create a label and an entry widget."""
        ttk.Label(parent, text=label_text).grid(row=row, column=col, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=5)
        self.entries[label_text] = entry

    def create_check_and_text(self, parent, label_text, row):
        """Helper to create a checkbox and a text area for detailed input."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        var = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text=label_text, variable=var, command=lambda v=var, l=label_text: self.toggle_text_area(v, l))
        chk.pack(anchor="w")

        text_area = tk.Text(frame, height=2, width=80, state=tk.DISABLED, bg="#e0e0e0")
        text_area.pack(fill=tk.X, pady=(5,0))
        
        self.entries[label_text] = var
        self.text_areas[label_text] = text_area

    def toggle_text_area(self, var, label):
        """Enable or disable text area based on checkbox state."""
        text_area = self.text_areas[label]
        if var.get():
            text_area.config(state=tk.NORMAL, bg="#ffffff")
        else:
            text_area.delete("1.0", tk.END)
            text_area.config(state=tk.DISABLED, bg="#e0e0e0")

    def calculate_risk_score(self):
        """
        Calculates a risk score based on applicant data.
        A lower score is better. Base score is 0.
        """
        score = 0
        reasons = []

        try:
            age = int(self.entries["Age:"].get())
            if age > 50:
                score += (age - 50) * 0.5
                reasons.append(f"Age ({age}) is over 50.")
            
            amount = float(self.entries["Requested Amount ($):"].get())
            if amount > 500000:
                score += 15
                reasons.append("High coverage amount requested.")

            systolic = int(self.entries["Systolic Blood Pressure:"].get())
            diastolic = int(self.entries["Diastolic Blood Pressure:"].get())
            if not (100 <= systolic <= 130 and 70 <= diastolic <= 85):
                score += 20
                reasons.append(f"Blood pressure ({systolic}/{diastolic}) is outside optimal range.")

            height_ft = float(self.entries["Height (ft):"].get())
            height_in = float(self.entries["Height (in):"].get())
            weight_lbs = float(self.entries["Weight (lbs):"].get())
            
            total_height_in = (height_ft * 12) + height_in
            if total_height_in > 0:
                bmi = (weight_lbs / (total_height_in ** 2)) * 703
                if bmi > 25:
                    score += (bmi - 25) * 1.5
                    reasons.append(f"BMI ({bmi:.1f}) is in the overweight or obese range.")

            if self.entries["Pre-existing Conditions (e.g., Diabetes, Heart Disease):"].get():
                score += 40
                reasons.append("Applicant has pre-existing conditions.")
            
            if self.entries["Family History of Major Illness:"].get():
                score += 15
                reasons.append("Family history of major illness noted.")

        except (ValueError, KeyError):
            messagebox.showerror("Input Error", "Please ensure all numerical fields (Age, Amount, BP, Height, Weight) are filled correctly.")
            return None, []

        return score, reasons

    def generate_report(self):
        """
        Gathers data, calculates risk, and displays the final report.
        """
        score, reasons = self.calculate_risk_score()
        if score is None:
            return

        decision = ""
        if score > 60:
            decision = "DECLINED"
        elif 30 <= score <= 60:
            decision = "REQUIRES FURTHER REVIEW"
        else:
            decision = "APPROVED"

        # Build the report string
        report = "========================================\n"
        report += "      LIFE INSURANCE APPROVAL REPORT    \n"
        report += "========================================\n\n"
        
        # Applicant Info
        for label, entry in self.entries.items():
            if isinstance(entry, ttk.Entry):
                report += f"{label:<25} {entry.get()}\n"
        
        report += "\n--- Health & Lifestyle Details ---\n"
        for label, var in self.entries.items():
             if isinstance(var, tk.BooleanVar):
                 has_condition = "Yes" if var.get() else "No"
                 details = self.text_areas[label].get("1.0", tk.END).strip()
                 report += f"{label.split(' (')[0]:<25} {has_condition}\n"
                 if details:
                     report += f"  Details: {details}\n"

        report += "\n" + "="*40 + "\n"
        report += f"RISK SCORE: {score:.1f}\n"
        report += f"DECISION:   {decision}\n"
        report += "-"*40 + "\n"
        
        if reasons:
            report += "Risk Factors Identified:\n"
            for reason in reasons:
                report += f"- {reason}\n"
        else:
            report += "No significant risk factors identified.\n"
        
        report += "\n" + "="*40 + "\n"

        # Display the report
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.config(state=tk.DISABLED)

        self.print_button.config(state=tk.NORMAL)

    def print_report(self):
        """
        Saves the report to a temporary file and opens the print dialog.
        """
        report_content = self.report_text.get("1.0", tk.END)
        if not report_content.strip():
            messagebox.showwarning("Print Error", "Report is empty. Please generate a report first.")
            return

        name = str( self.entries["Full Name:"].get())
        file_name = name + ".txt"        
        with open( file_name, 'w' ) as report_file:    
            report_file.write(report_content)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = LifeInsuranceApp(root)
    root.mainloop()


