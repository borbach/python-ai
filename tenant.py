import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import math
import os

class TenantApprovalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Tenant Approval Expert System")
        self.root.geometry("1600x1100")
        self.root.configure(bg='#f0f0f0')
        
        # Create main horizontal paned window
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg='#f0f0f0', 
                                          sashwidth=10, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for input fields (fixed width)
        self.left_frame = tk.Frame(self.paned_window, bg='#f0f0f0', width=650)
        self.left_frame.pack_propagate(False)
        
        # Right frame for results (expandable)
        self.right_frame = tk.Frame(self.paned_window, bg='#f0f0f0')
        
        # Add frames to paned window
        self.paned_window.add(self.left_frame, width=650, minsize=600)
        self.paned_window.add(self.right_frame, minsize=400)
        
        # Title for left frame
        title_label = tk.Label(self.left_frame, text="Tenant Evaluation System", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(10, 20))
        
        # Create scrollable frame for input fields
        self.create_scrollable_input_area()
        
        # Create input fields
        self.create_input_fields()
        
        # Buttons
        self.create_buttons()
        
        # Results area in right frame
        self.create_results_area()
        
    def create_scrollable_input_area(self):
        # Create canvas and scrollbar for left frame
        self.canvas = tk.Canvas(self.left_frame, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar_left = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_left.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 0))
        self.scrollbar_left.pack(side="right", fill="y")
        
    def create_input_fields(self):
        # All input fields go in the scrollable frame now
        input_frame = self.scrollable_frame
        
        # Applicant Information
        info_frame = tk.LabelFrame(input_frame, text="Applicant Information", 
                                  font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        info_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        tk.Label(info_frame, text="Applicant Name:", bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=8, pady=8)
        self.name_entry = tk.Entry(info_frame, width=35, font=('Arial', 9))
        self.name_entry.grid(row=0, column=1, padx=8, pady=8, sticky='w')
        
        # Financial Information
        financial_frame = tk.LabelFrame(input_frame, text="Financial Information", 
                                       font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        financial_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Credit Score
        tk.Label(financial_frame, text="Credit Score (300-850):", bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=8, pady=8)
        self.credit_score = tk.IntVar(value=650)
        credit_scale = tk.Scale(financial_frame, from_=300, to=850, orient=tk.HORIZONTAL, 
                               variable=self.credit_score, length=250, font=('Arial', 8))
        credit_scale.grid(row=0, column=1, padx=8, pady=8, sticky='w')
        
        # Monthly Income
        tk.Label(financial_frame, text="Monthly Income ($):", bg='#f0f0f0', font=('Arial', 9)).grid(row=1, column=0, sticky='w', padx=8, pady=8)
        self.income_entry = tk.Entry(financial_frame, width=25, font=('Arial', 9))
        self.income_entry.grid(row=1, column=1, sticky='w', padx=8, pady=8)
        
        # Monthly Rent
        tk.Label(financial_frame, text="Monthly Rent ($):", bg='#f0f0f0', font=('Arial', 9)).grid(row=2, column=0, sticky='w', padx=8, pady=8)
        self.rent_entry = tk.Entry(financial_frame, width=25, font=('Arial', 9))
        self.rent_entry.grid(row=2, column=1, sticky='w', padx=8, pady=8)
        
        # Credit History
        tk.Label(financial_frame, text="Credit History:", bg='#f0f0f0', font=('Arial', 9)).grid(row=3, column=0, sticky='w', padx=8, pady=8)
        self.credit_history = ttk.Combobox(financial_frame, values=[
            "Excellent - No late payments, long history",
            "Good - Few late payments, good history",
            "Fair - Some late payments or short history",
            "Poor - Many late payments or defaults",
            "No Credit History"
        ], width=40, font=('Arial', 8))
        self.credit_history.grid(row=3, column=1, padx=8, pady=8, sticky='w')
        self.credit_history.set("Good - Few late payments, good history")
        
        # Employment Information
        employment_frame = tk.LabelFrame(input_frame, text="Employment Information", 
                                        font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        employment_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Job Stability
        tk.Label(employment_frame, text="Current Job Duration:", bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=8, pady=8)
        self.job_duration = ttk.Combobox(employment_frame, values=[
            "Less than 6 months",
            "6 months - 1 year",
            "1-2 years",
            "2-5 years",
            "5+ years"
        ], width=30, font=('Arial', 8))
        self.job_duration.grid(row=0, column=1, padx=8, pady=8, sticky='w')
        self.job_duration.set("1-2 years")
        
        # Employment Type
        tk.Label(employment_frame, text="Employment Type:", bg='#f0f0f0', font=('Arial', 9)).grid(row=1, column=0, sticky='w', padx=8, pady=8)
        self.employment_type = ttk.Combobox(employment_frame, values=[
            "Full-time permanent",
            "Full-time contract",
            "Part-time",
            "Self-employed",
            "Retired with pension",
            "Unemployed/Student"
        ], width=30, font=('Arial', 8))
        self.employment_type.grid(row=1, column=1, padx=8, pady=8, sticky='w')
        self.employment_type.set("Full-time permanent")
        
        # Rental History
        rental_frame = tk.LabelFrame(input_frame, text="Rental History & Background", 
                                    font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        rental_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Landlord References
        tk.Label(rental_frame, text="Previous Landlord References:", bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=8, pady=8)
        self.landlord_refs = ttk.Combobox(rental_frame, values=[
            "Excellent - Always paid on time, no issues",
            "Good - Mostly on time, minor issues",
            "Fair - Some late payments, some issues",
            "Poor - Often late, property damage",
            "No Previous Rental History"
        ], width=40, font=('Arial', 8))
        self.landlord_refs.grid(row=0, column=1, padx=8, pady=8, sticky='w')
        self.landlord_refs.set("Good - Mostly on time, minor issues")
        
        # Criminal Background
        tk.Label(rental_frame, text="Criminal Background:", bg='#f0f0f0', font=('Arial', 9)).grid(row=1, column=0, sticky='w', padx=8, pady=8)
        self.criminal_bg = ttk.Combobox(rental_frame, values=[
            "Clean record",
            "Minor infractions (traffic, etc.)",
            "Misdemeanor convictions",
            "Felony convictions",
            "Recent serious convictions"
        ], width=35, font=('Arial', 8))
        self.criminal_bg.grid(row=1, column=1, padx=8, pady=8, sticky='w')
        self.criminal_bg.set("Clean record")
        
        # Additional Criteria
        additional_frame = tk.LabelFrame(input_frame, text="Additional Criteria", 
                                       font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        additional_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Number of Occupants
        tk.Label(additional_frame, text="Number of Occupants:", bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=8, pady=8)
        self.occupants = tk.IntVar(value=2)
        occupants_scale = tk.Scale(additional_frame, from_=1, to=8, orient=tk.HORIZONTAL, 
                                 variable=self.occupants, length=200, font=('Arial', 8))
        occupants_scale.grid(row=0, column=1, padx=8, pady=8, sticky='w')
        
        # Checkboxes
        self.section8_var = tk.BooleanVar()
        section8_check = tk.Checkbutton(additional_frame, text="Section 8 Housing Voucher", 
                                       variable=self.section8_var, bg='#f0f0f0', font=('Arial', 9))
        section8_check.grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=5)
        
        self.pets_var = tk.BooleanVar()
        pets_check = tk.Checkbutton(additional_frame, text="Has Pets", 
                                   variable=self.pets_var, bg='#f0f0f0', font=('Arial', 9))
        pets_check.grid(row=2, column=0, columnspan=2, sticky='w', padx=8, pady=5)
        
        self.emergency_contact_var = tk.BooleanVar(value=True)
        emergency_check = tk.Checkbutton(additional_frame, text="Has Emergency Contact/Co-signer", 
                                       variable=self.emergency_contact_var, bg='#f0f0f0', font=('Arial', 9))
        emergency_check.grid(row=3, column=0, columnspan=2, sticky='w', padx=8, pady=5)
    
    def create_buttons(self):
        button_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        button_frame.pack(pady=20, padx=10)
        
        evaluate_btn = tk.Button(button_frame, text="Evaluate Applicant", 
                               command=self.evaluate_tenant, bg='#3498db', fg='white',
                               font=('Arial', 11, 'bold'), padx=30, pady=12)
        evaluate_btn.pack(pady=5)
        
        clear_btn = tk.Button(button_frame, text="Clear All Fields", 
                            command=self.clear_fields, bg='#95a5a6', fg='white',
                            font=('Arial', 10), padx=30, pady=10)
        clear_btn.pack(pady=5)
        
        save_btn = tk.Button(button_frame, text="Save Report", 
                           command=self.save_report, bg='#27ae60', fg='white',
                           font=('Arial', 10), padx=30, pady=10)
        save_btn.pack(pady=5)
    
    def create_results_area(self):
        # Title for results
        results_title = tk.Label(self.right_frame, text="Evaluation Results", 
                                font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        results_title.pack(pady=(10, 15))
        
        # Results text area with scrollbar
        text_frame = tk.Frame(self.right_frame, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD, bg='white', 
                                   font=('Consolas', 11), relief=tk.SUNKEN, bd=2)
        scrollbar_right = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar_right.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store the current report text for saving
        self.current_report = ""
        
        # Add some initial text
        welcome_text = """Welcome to the Tenant Approval Expert System!

Please fill out the applicant information on the left and click 
"Evaluate Applicant" to generate a comprehensive rental assessment.

The system will analyze:
• Credit score and history
• Income-to-rent ratio
• Employment stability
• Rental history
• Background check results
• And additional risk factors

Results will appear here with detailed scoring and recommendations."""
        
        self.results_text.insert(tk.END, welcome_text)
        self.results_text.configure(state=tk.DISABLED)
    
    def evaluate_tenant(self):
        try:
            self.results_text.configure(state=tk.NORMAL)
            
            # Get all input values
            name = self.name_entry.get() or "Applicant"
            credit_score = self.credit_score.get()
            income = float(self.income_entry.get() or 0)
            rent = float(self.rent_entry.get() or 0)
            
            # Calculate scores for each criteria
            scores = {}
            max_scores = {}
            
            # Credit Score (25 points max)
            max_scores['Credit Score'] = 25
            if credit_score >= 750:
                scores['Credit Score'] = 25
            elif credit_score >= 700:
                scores['Credit Score'] = 22
            elif credit_score >= 650:
                scores['Credit Score'] = 18
            elif credit_score >= 600:
                scores['Credit Score'] = 14
            elif credit_score >= 550:
                scores['Credit Score'] = 10
            else:
                scores['Credit Score'] = 5
            
            # Income to Rent Ratio (20 points max)
            max_scores['Income to Rent Ratio'] = 20
            if income > 0 and rent > 0:
                ratio = income / rent
                if ratio >= 4:
                    scores['Income to Rent Ratio'] = 20
                elif ratio >= 3:
                    scores['Income to Rent Ratio'] = 18
                elif ratio >= 2.5:
                    scores['Income to Rent Ratio'] = 15
                elif ratio >= 2:
                    scores['Income to Rent Ratio'] = 10
                else:
                    scores['Income to Rent Ratio'] = 5
            else:
                scores['Income to Rent Ratio'] = 0
            
            # Credit History (15 points max)
            max_scores['Credit History'] = 15
            credit_hist = self.credit_history.get()
            if "Excellent" in credit_hist:
                scores['Credit History'] = 15
            elif "Good" in credit_hist:
                scores['Credit History'] = 12
            elif "Fair" in credit_hist:
                scores['Credit History'] = 8
            elif "Poor" in credit_hist:
                scores['Credit History'] = 4
            else:
                scores['Credit History'] = 6  # No history
            
            # Job Stability (15 points max)
            max_scores['Job Stability'] = 15
            job_dur = self.job_duration.get()
            emp_type = self.employment_type.get()
            
            duration_score = 0
            if "5+ years" in job_dur:
                duration_score = 10
            elif "2-5 years" in job_dur:
                duration_score = 8
            elif "1-2 years" in job_dur:
                duration_score = 6
            elif "6 months - 1 year" in job_dur:
                duration_score = 4
            else:
                duration_score = 2
            
            type_score = 0
            if "Full-time permanent" in emp_type:
                type_score = 5
            elif "Full-time contract" in emp_type:
                type_score = 4
            elif "Retired with pension" in emp_type:
                type_score = 4
            elif "Part-time" in emp_type:
                type_score = 3
            elif "Self-employed" in emp_type:
                type_score = 2
            else:
                type_score = 1
                
            scores['Job Stability'] = duration_score + type_score
            
            # Landlord References (12 points max)
            max_scores['Landlord References'] = 12
            landlord_ref = self.landlord_refs.get()
            if "Excellent" in landlord_ref:
                scores['Landlord References'] = 12
            elif "Good" in landlord_ref:
                scores['Landlord References'] = 10
            elif "Fair" in landlord_ref:
                scores['Landlord References'] = 6
            elif "Poor" in landlord_ref:
                scores['Landlord References'] = 2
            else:
                scores['Landlord References'] = 7  # No history
            
            # Criminal Background (8 points max)
            max_scores['Criminal Background'] = 8
            criminal = self.criminal_bg.get()
            if "Clean record" in criminal:
                scores['Criminal Background'] = 8
            elif "Minor infractions" in criminal:
                scores['Criminal Background'] = 6
            elif "Misdemeanor" in criminal:
                scores['Criminal Background'] = 4
            elif "Recent serious" in criminal:
                scores['Criminal Background'] = 0
            else:
                scores['Criminal Background'] = 2  # Felony
            
            # Number of Occupants (8 points max)
            max_scores['Occupancy'] = 8
            occupants = self.occupants.get()
            if occupants == 1:
                scores['Occupancy'] = 8
            elif occupants == 2:
                scores['Occupancy'] = 7
            elif occupants == 3:
                scores['Occupancy'] = 5
            elif occupants == 4:
                scores['Occupancy'] = 3
            else:
                scores['Occupancy'] = 1
            
            # Additional factors (7 points max)
            max_scores['Additional Factors'] = 7
            additional_score = 0
            
            if self.section8_var.get():
                additional_score += 2  # Section 8 can be positive (guaranteed payment)
            
            if not self.pets_var.get():
                additional_score += 2  # No pets is generally preferred
            
            if self.emergency_contact_var.get():
                additional_score += 3  # Emergency contact/co-signer is valuable
                
            scores['Additional Factors'] = additional_score
            
            # Calculate total score and percentage
            total_score = sum(scores.values())
            max_total = sum(max_scores.values())
            percentage = (total_score / max_total) * 100
            
            # Determine recommendation
            if percentage >= 85:
                recommendation = "HIGHLY RECOMMENDED"
                color = "green"
                risk_level = "Very Low Risk"
            elif percentage >= 75:
                recommendation = "RECOMMENDED"
                color = "lightgreen"
                risk_level = "Low Risk"
            elif percentage >= 65:
                recommendation = "CONDITIONALLY APPROVED"
                color = "orange"
                risk_level = "Moderate Risk"
            elif percentage >= 50:
                recommendation = "HIGH RISK - CAREFUL CONSIDERATION"
                color = "red"
                risk_level = "High Risk"
            else:
                recommendation = "NOT RECOMMENDED"
                color = "darkred"
                risk_level = "Very High Risk"
            
            # Generate detailed report
            self.generate_report(name, scores, max_scores, total_score, max_total, 
                               percentage, recommendation, risk_level, income, rent)
            
        except ValueError as e:
            messagebox.showerror("Input Error", "Please enter valid numeric values for income and rent.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def save_report(self):
        """Save the current report to a text file"""
        if not self.current_report:
            messagebox.showwarning("No Report", "Please evaluate an applicant first before saving.")
            return
        
        # Get applicant name for filename suggestion
        name = self.name_entry.get() or "Applicant"
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"Tenant_Report_{name.replace(' ', '_')}_{date_str}.txt"
        
        # Open file dialog
#        filename = filedialog.asksaveasfilename(
#            defaultextension=".txt",
#            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
#            initialvalue=default_filename,
#            title="Save Tenant Evaluation Report"
#        )
        filename = f"tenant_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.current_report)
                messagebox.showinfo("Success", f"Report saved successfully to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")
    
    def generate_report(self, name, scores, max_scores, total_score, max_total, 
                       percentage, recommendation, risk_level, income, rent):
        self.results_text.delete(1.0, tk.END)
        
        report = f"""TENANT EVALUATION REPORT
{'='*70}

Applicant: {name}
Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RECOMMENDATION: {recommendation}
Risk Level: {risk_level}
Overall Score: {total_score}/{max_total} ({percentage:.1f}%)

{'='*70}
DETAILED SCORING BREAKDOWN:
{'='*70}

"""
        
        for category, score in scores.items():
            max_score = max_scores[category]
            percentage_cat = (score / max_score) * 100
            report += f"{category:<25}: {score:>2}/{max_score:<2} ({percentage_cat:>5.1f}%)\n"
        
        report += f"\n{'='*70}\n"
        report += f"FINANCIAL ANALYSIS:\n"
        report += f"{'='*70}\n"
        
        if income > 0 and rent > 0:
            ratio = income / rent
            report += f"Monthly Income: ${income:,.2f}\n"
            report += f"Monthly Rent: ${rent:,.2f}\n"
            report += f"Income-to-Rent Ratio: {ratio:.2f}x\n"
            
            if ratio >= 3:
                report += "✓ Excellent income ratio (3x+ rent)\n"
            elif ratio >= 2.5:
                report += "✓ Good income ratio (2.5x+ rent)\n"
            elif ratio >= 2:
                report += "⚠ Marginal income ratio (2x+ rent)\n"
            else:
                report += "✗ Poor income ratio (less than 2x rent)\n"
        
        report += f"\n{'='*70}\n"
        report += f"KEY STRENGTHS & CONCERNS:\n"
        report += f"{'='*70}\n"
        
        strengths = []
        concerns = []
        
        # Analyze strengths and concerns
        if scores['Credit Score'] >= 20:
            strengths.append("Excellent credit score")
        elif scores['Credit Score'] <= 10:
            concerns.append("Poor credit score")
            
        if scores['Income to Rent Ratio'] >= 18:
            strengths.append("Strong income-to-rent ratio")
        elif scores['Income to Rent Ratio'] <= 10:
            concerns.append("Weak income-to-rent ratio")
            
        if scores['Job Stability'] >= 12:
            strengths.append("Stable employment history")
        elif scores['Job Stability'] <= 8:
            concerns.append("Employment stability issues")
            
        if scores['Landlord References'] >= 10:
            strengths.append("Positive rental history")
        elif scores['Landlord References'] <= 6:
            concerns.append("Concerning rental history")
            
        if scores['Criminal Background'] == 8:
            strengths.append("Clean criminal background")
        elif scores['Criminal Background'] <= 4:
            concerns.append("Criminal background issues")
        
        if strengths:
            report += "STRENGTHS:\n"
            for strength in strengths:
                report += f"✓ {strength}\n"
                
        if concerns:
            report += "\nCONCERNS:\n"
            for concern in concerns:
                report += f"✗ {concern}\n"
        
        report += f"\n{'='*70}\n"
        report += f"RECOMMENDATIONS:\n"
        report += f"{'='*70}\n"
        
        if percentage >= 85:
            report += "• Approve application immediately\n"
            report += "• Excellent candidate with minimal risk\n"
        elif percentage >= 75:
            report += "• Approve application\n"
            report += "• Good candidate with acceptable risk\n"
        elif percentage >= 65:
            report += "• Consider approval with conditions:\n"
            report += "  - Require additional security deposit\n"
            report += "  - Request co-signer if available\n"
            report += "  - Verify employment and income\n"
        elif percentage >= 50:
            report += "• High risk - proceed with extreme caution:\n"
            report += "  - Require significant security deposit\n"
            report += "  - Mandate co-signer\n"
            report += "  - Consider month-to-month lease initially\n"
        else:
            report += "• Recommend rejection\n"
            report += "• Risk factors too significant\n"
            report += "• Consider alternative applicants\n"
        
        self.results_text.insert(tk.END, report)
        self.results_text.configure(state=tk.DISABLED)
        
        # Store the report for saving
        self.current_report = report
    
    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.income_entry.delete(0, tk.END)
        self.rent_entry.delete(0, tk.END)
        self.credit_score.set(650)
        self.occupants.set(2)
        self.credit_history.set("Good - Few late payments, good history")
        self.job_duration.set("1-2 years")
        self.employment_type.set("Full-time permanent")
        self.landlord_refs.set("Good - Mostly on time, minor issues")
        self.criminal_bg.set("Clean record")
        self.section8_var.set(False)
        self.pets_var.set(False)
        self.emergency_contact_var.set(True)
        
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        welcome_text = """Welcome to the Tenant Approval Expert System!

Please fill out the applicant information on the left and click 
"Evaluate Applicant" to generate a comprehensive rental assessment."""
        
        self.results_text.insert(tk.END, welcome_text)
        self.results_text.configure(state=tk.DISABLED)
        self.current_report = ""

def main():
    root = tk.Tk()
    app = TenantApprovalSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()


