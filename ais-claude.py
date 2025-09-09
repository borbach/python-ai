import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import re

class LifeInsuranceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Life Insurance Approval System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables to store form data
        self.form_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame with scrollbar
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Life Insurance Application", 
                              font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Personal Information Section
        self.create_section_header(scrollable_frame, "Personal Information")
        
        self.name_var = tk.StringVar()
        self.create_input(scrollable_frame, "Full Name:", self.name_var)
        
        self.age_var = tk.StringVar()
        self.create_input(scrollable_frame, "Age:", self.age_var)
        
        self.gender_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Gender:", self.gender_var, 
                           ["Male", "Female", "Other"])
        
        self.occupation_var = tk.StringVar()
        self.create_input(scrollable_frame, "Occupation:", self.occupation_var)
        
        self.income_var = tk.StringVar()
        self.create_input(scrollable_frame, "Annual Income ($):", self.income_var)
        
        # Policy Information Section
        self.create_section_header(scrollable_frame, "Policy Information")
        
        self.amount_var = tk.StringVar()
        self.create_input(scrollable_frame, "Coverage Amount ($):", self.amount_var)
        
        self.term_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Term (years):", self.term_var,
                           ["10", "15", "20", "25", "30", "Whole Life"])
        
        # Health Information Section
        self.create_section_header(scrollable_frame, "Health Information")
        
        self.height_var = tk.StringVar()
        self.create_input(scrollable_frame, "Height (inches):", self.height_var)
        
        self.weight_var = tk.StringVar()
        self.create_input(scrollable_frame, "Weight (lbs):", self.weight_var)
        
        self.smoker_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Smoking Status:", self.smoker_var,
                           ["Never smoked", "Former smoker (quit >2 years)", 
                            "Former smoker (quit <2 years)", "Current smoker"])
        
        self.alcohol_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Alcohol Consumption:", self.alcohol_var,
                           ["None", "Occasional (1-3 drinks/week)", 
                            "Moderate (4-10 drinks/week)", "Heavy (>10 drinks/week)"])
        
        # Blood Pressure Section
        self.bp_systolic_var = tk.StringVar()
        self.create_input(scrollable_frame, "Blood Pressure - Systolic:", self.bp_systolic_var)
        
        self.bp_diastolic_var = tk.StringVar()
        self.create_input(scrollable_frame, "Blood Pressure - Diastolic:", self.bp_diastolic_var)
        
        # Medical History Section
        self.create_section_header(scrollable_frame, "Medical History")
        
        self.diseases_var = tk.StringVar()
        self.create_input(scrollable_frame, "Current Diseases/Conditions:", self.diseases_var)
        
        self.medications_var = tk.StringVar()
        self.create_input(scrollable_frame, "Current Medications:", self.medications_var)
        
        self.surgeries_var = tk.StringVar()
        self.create_input(scrollable_frame, "Past Surgeries/Hospitalizations:", self.surgeries_var)
        
        self.family_history_var = tk.StringVar()
        self.create_input(scrollable_frame, "Family Medical History:", self.family_history_var)
        
        # Lifestyle Section
        self.create_section_header(scrollable_frame, "Lifestyle")
        
        self.exercise_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Exercise Frequency:", self.exercise_var,
                           ["Sedentary", "Light (1-2 times/week)", 
                            "Moderate (3-4 times/week)", "Active (5+ times/week)"])
        
        self.driving_record_var = tk.StringVar()
        self.create_dropdown(scrollable_frame, "Driving Record:", self.driving_record_var,
                           ["Clean", "Minor violations", "Major violations", "DUI/DWI"])
        
        self.dangerous_activities_var = tk.StringVar()
        self.create_input(scrollable_frame, "Dangerous Hobbies/Activities:", self.dangerous_activities_var)
        
        # Action Buttons Section
        self.create_section_header(scrollable_frame, "Application Processing")
        
        button_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        # Evaluate Button
        evaluate_btn = tk.Button(button_frame, text="EVALUATE APPLICATION", 
                               command=self.process_application,
                               bg='#2ecc71', fg='white', font=('Arial', 16, 'bold'),
                               padx=40, pady=20, width=20, relief='raised', bd=3)
        evaluate_btn.pack(side=tk.LEFT, padx=20)
        
        # Clear Button
        clear_btn = tk.Button(button_frame, text="CLEAR FORM", 
                            command=self.clear_form,
                            bg='#e74c3c', fg='white', font=('Arial', 16, 'bold'),
                            padx=40, pady=20, width=20, relief='raised', bd=3)
        clear_btn.pack(side=tk.LEFT, padx=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_section_header(self, parent, text):
        header_frame = tk.Frame(parent, bg='#34495e', height=40)
        header_frame.pack(fill=tk.X, pady=(25, 10))
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text=text, 
                               font=('Arial', 14, 'bold'), 
                               bg='#34495e', fg='white')
        header_label.pack(pady=8)
    
    def create_input(self, parent, label_text, variable):
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(frame, text=label_text, width=30, anchor='w',
                        bg='#f0f0f0', font=('Arial', 11))
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        entry = tk.Entry(frame, textvariable=variable, width=60, font=('Arial', 11))
        entry.pack(side=tk.LEFT, padx=5)
    
    def create_dropdown(self, parent, label_text, variable, options):
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(frame, text=label_text, width=30, anchor='w',
                        bg='#f0f0f0', font=('Arial', 11))
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        combo = ttk.Combobox(frame, textvariable=variable, values=options, 
                           width=57, font=('Arial', 11), state="readonly")
        combo.pack(side=tk.LEFT, padx=5)
    
    def validate_input(self):
        errors = []
        
        # Required fields validation
        if not self.name_var.get().strip():
            errors.append("Name is required")
        
        # Age validation
        try:
            age = int(self.age_var.get())
            if age < 18 or age > 85:
                errors.append("Age must be between 18 and 85")
        except ValueError:
            errors.append("Age must be a valid number")
        
        # Income validation
        try:
            income = float(self.income_var.get().replace(',', ''))
            if income <= 0:
                errors.append("Income must be greater than 0")
        except ValueError:
            errors.append("Income must be a valid number")
        
        # Coverage amount validation
        try:
            coverage = float(self.amount_var.get().replace(',', ''))
            if coverage <= 0:
                errors.append("Coverage amount must be greater than 0")
        except ValueError:
            errors.append("Coverage amount must be a valid number")
        
        # Height and weight validation
        try:
            height = float(self.height_var.get())
            if height < 48 or height > 84:
                errors.append("Height must be between 48 and 84 inches")
        except ValueError:
            errors.append("Height must be a valid number")
        
        try:
            weight = float(self.weight_var.get())
            if weight < 80 or weight > 500:
                errors.append("Weight must be between 80 and 500 lbs")
        except ValueError:
            errors.append("Weight must be a valid number")
        
        # Blood pressure validation
        try:
            systolic = int(self.bp_systolic_var.get())
            diastolic = int(self.bp_diastolic_var.get())
            if systolic < 80 or systolic > 250:
                errors.append("Systolic BP must be between 80 and 250")
            if diastolic < 40 or diastolic > 150:
                errors.append("Diastolic BP must be between 40 and 150")
        except ValueError:
            errors.append("Blood pressure values must be valid numbers")
        
        return errors
    
    def calculate_bmi(self):
        height = float(self.height_var.get())
        weight = float(self.weight_var.get())
        return (weight / (height * height)) * 703
    
    def assess_risk_factors(self):
        risk_score = 0
        risk_factors = []
        
        # Age risk
        age = int(self.age_var.get())
        if age > 60:
            risk_score += 3
            risk_factors.append(f"Advanced age ({age})")
        elif age > 45:
            risk_score += 1
            risk_factors.append(f"Middle age ({age})")
        
        # BMI risk
        bmi = self.calculate_bmi()
        if bmi > 35:
            risk_score += 4
            risk_factors.append(f"Severe obesity (BMI: {bmi:.1f})")
        elif bmi > 30:
            risk_score += 2
            risk_factors.append(f"Obesity (BMI: {bmi:.1f})")
        elif bmi < 18.5:
            risk_score += 2
            risk_factors.append(f"Underweight (BMI: {bmi:.1f})")
        
        # Smoking risk
        smoking_status = self.smoker_var.get()
        if "Current smoker" in smoking_status:
            risk_score += 5
            risk_factors.append("Current smoker")
        elif "quit <2 years" in smoking_status:
            risk_score += 3
            risk_factors.append("Recent former smoker")
        elif "quit >2 years" in smoking_status:
            risk_score += 1
            risk_factors.append("Former smoker")
        
        # Blood pressure risk
        systolic = int(self.bp_systolic_var.get())
        diastolic = int(self.bp_diastolic_var.get())
        if systolic > 160 or diastolic > 100:
            risk_score += 4
            risk_factors.append(f"High blood pressure ({systolic}/{diastolic})")
        elif systolic > 140 or diastolic > 90:
            risk_score += 2
            risk_factors.append(f"Elevated blood pressure ({systolic}/{diastolic})")
        
        # Alcohol risk
        alcohol = self.alcohol_var.get()
        if "Heavy" in alcohol:
            risk_score += 3
            risk_factors.append("Heavy alcohol consumption")
        elif "Moderate" in alcohol:
            risk_score += 1
            risk_factors.append("Moderate alcohol consumption")
        
        # Medical conditions risk
        diseases = self.diseases_var.get().strip().lower()
        high_risk_conditions = ['heart', 'cancer', 'diabetes', 'stroke', 'kidney', 'liver']
        for condition in high_risk_conditions:
            if condition in diseases:
                risk_score += 4
                risk_factors.append(f"Medical condition: {condition}")
        
        # Family history risk
        family_history = self.family_history_var.get().strip().lower()
        family_risk_conditions = ['heart', 'cancer', 'diabetes', 'stroke']
        for condition in family_risk_conditions:
            if condition in family_history:
                risk_score += 1
                risk_factors.append(f"Family history: {condition}")
        
        # Driving record risk
        driving = self.driving_record_var.get()
        if "DUI" in driving:
            risk_score += 4
            risk_factors.append("DUI/DWI history")
        elif "Major violations" in driving:
            risk_score += 2
            risk_factors.append("Major driving violations")
        
        # Dangerous activities
        activities = self.dangerous_activities_var.get().strip().lower()
        dangerous_keywords = ['skydiving', 'mountaineering', 'racing', 'flying', 'scuba']
        for activity in dangerous_keywords:
            if activity in activities:
                risk_score += 2
                risk_factors.append(f"Dangerous activity: {activity}")
        
        # Coverage to income ratio
        try:
            coverage = float(self.amount_var.get().replace(',', ''))
            income = float(self.income_var.get().replace(',', ''))
            ratio = coverage / income
            if ratio > 20:
                risk_score += 3
                risk_factors.append("High coverage to income ratio")
            elif ratio > 15:
                risk_score += 1
                risk_factors.append("Elevated coverage to income ratio")
        except:
            pass
        
        return risk_score, risk_factors
    
    def make_decision(self, risk_score, risk_factors):
        if risk_score <= 3:
            decision = "APPROVED - Standard Rate"
            explanation = "Application approved at standard premium rates."
        elif risk_score <= 6:
            decision = "APPROVED - Substandard Rate"
            explanation = "Application approved with increased premium (table rating)."
        elif risk_score <= 10:
            decision = "POSTPONED - Additional Information Required"
            explanation = "Application requires medical examination and additional underwriting."
        else:
            decision = "DECLINED"
            explanation = "Application declined due to high risk factors."
        
        return decision, explanation
    
    def process_application(self):
        # Validate input
        errors = self.validate_input()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Calculate risk
        risk_score, risk_factors = self.assess_risk_factors()
        
        # Make decision
        decision, explanation = self.make_decision(risk_score, risk_factors)
        
        # Generate report
        self.generate_report(risk_score, risk_factors, decision, explanation)
    
    def generate_report(self, risk_score, risk_factors, decision, explanation):
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Life Insurance Application Report")
        report_window.geometry("900x800")
        report_window.configure(bg='white')
        
        # Create scrolled text widget for report
        report_text = scrolledtext.ScrolledText(report_window, width=100, height=40,
                                               font=('Courier', 10))
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate report content
        report_content = self.create_report_content(risk_score, risk_factors, decision, explanation)
        
        report_text.insert(tk.END, report_content)
        report_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(report_window, bg='white')
        button_frame.pack(pady=15)
        
        # Print button
        print_btn = tk.Button(button_frame, text="PRINT REPORT", 
                            command=lambda: self.print_report(report_content),
                            bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                            padx=25, pady=10)
        print_btn.pack(side=tk.LEFT, padx=10)
        
        # Save button
        save_btn = tk.Button(button_frame, text="SAVE REPORT", 
                           command=lambda: self.save_report(report_content),
                           bg='#f39c12', fg='white', font=('Arial', 12, 'bold'),
                           padx=25, pady=10)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_btn = tk.Button(button_frame, text="CLOSE", 
                            command=report_window.destroy,
                            bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'),
                            padx=25, pady=10)
        close_btn.pack(side=tk.LEFT, padx=10)
    
    def create_report_content(self, risk_score, risk_factors, decision, explanation):
        bmi = self.calculate_bmi()
        
        report = f"""
{'='*90}
                           LIFE INSURANCE APPLICATION REPORT
{'='*90}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

APPLICANT INFORMATION:
{'─'*50}
Name: {self.name_var.get()}
Age: {self.age_var.get()}
Gender: {self.gender_var.get()}
Occupation: {self.occupation_var.get()}
Annual Income: ${self.income_var.get()}

POLICY DETAILS:
{'─'*50}
Coverage Amount: ${self.amount_var.get()}
Term: {self.term_var.get()}

HEALTH PROFILE:
{'─'*50}
Height: {self.height_var.get()} inches
Weight: {self.weight_var.get()} lbs
BMI: {bmi:.1f}
Smoking Status: {self.smoker_var.get()}
Alcohol Consumption: {self.alcohol_var.get()}
Blood Pressure: {self.bp_systolic_var.get()}/{self.bp_diastolic_var.get()}
Exercise Frequency: {self.exercise_var.get()}
Driving Record: {self.driving_record_var.get()}

MEDICAL HISTORY:
{'─'*50}
Current Diseases/Conditions: {self.diseases_var.get()}
Current Medications: {self.medications_var.get()}
Past Surgeries/Hospitalizations: {self.surgeries_var.get()}
Family Medical History: {self.family_history_var.get()}
Dangerous Activities: {self.dangerous_activities_var.get()}

RISK ASSESSMENT:
{'─'*50}
Total Risk Score: {risk_score}

Risk Factors Identified:
"""
        
        if risk_factors:
            for i, factor in enumerate(risk_factors, 1):
                report += f"{i}. {factor}\n"
        else:
            report += "None identified\n"
        
        report += f"""
UNDERWRITING DECISION:
{'─'*50}
Decision: {decision}

Explanation: {explanation}

PREMIUM ESTIMATION:
{'─'*50}
"""
        
        # Calculate estimated premium
        try:
            coverage = float(self.amount_var.get().replace(',', ''))
            age = int(self.age_var.get())
            base_rate = 0.5  # Base rate per $1000 coverage
            
            # Age factor
            if age < 30:
                age_factor = 0.8
            elif age < 40:
                age_factor = 1.0
            elif age < 50:
                age_factor = 1.5
            elif age < 60:
                age_factor = 2.0
            else:
                age_factor = 3.0
            
            # Risk factor
            if "Standard Rate" in decision:
                risk_factor = 1.0
            elif "Substandard Rate" in decision:
                risk_factor = 1.5
            else:
                risk_factor = 0  # Not applicable
            
            if risk_factor > 0:
                annual_premium = (coverage / 1000) * base_rate * age_factor * risk_factor
                report += f"Estimated Annual Premium: ${annual_premium:,.2f}\n"
            else:
                report += "Premium calculation not applicable\n"
        except:
            report += "Unable to calculate premium\n"
        
        report += f"""
NEXT STEPS:
{'─'*50}
"""
        
        if "APPROVED" in decision:
            report += "• Policy documents will be prepared\n"
            report += "• Medical examination may be required\n"
            report += "• Premium payment schedule will be provided\n"
        elif "POSTPONED" in decision:
            report += "• Medical examination required\n"
            report += "• Additional medical records needed\n"
            report += "• Re-evaluation in 30-60 days\n"
        else:
            report += "• Application cannot be approved at this time\n"
            report += "• Applicant may reapply after addressing risk factors\n"
        
        report += f"""
{'='*90}
This report is generated by an automated underwriting system.
Final decisions may require manual review by licensed underwriters.
{'='*90}
"""
        
        return report
    
    def print_report(self, content):
        # For demonstration, we'll show print dialog simulation
        result = messagebox.askyesno("Print Report", 
                                   "Send report to printer?\n\n(This will actually save the file for demonstration purposes)")
        if result:
            try:
                filename = f"insurance_report_print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Print Successful", f"Report sent to printer and saved as {filename}")
            except Exception as e:
                messagebox.showerror("Print Error", f"Could not print report: {str(e)}")
    
    def save_report(self, content):
        # Save report to file
        try:
            filename = f"insurance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Report Saved", f"Report saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save report: {str(e)}")
    
    def clear_form(self):
        # Clear all form fields
        for var in [self.name_var, self.age_var, self.gender_var, self.occupation_var,
                   self.income_var, self.amount_var, self.term_var, self.height_var,
                   self.weight_var, self.smoker_var, self.alcohol_var, self.bp_systolic_var,
                   self.bp_diastolic_var, self.exercise_var, self.driving_record_var,
                   self.diseases_var, self.medications_var, self.surgeries_var,
                   self.family_history_var, self.dangerous_activities_var]:
            var.set("")
    
    def run(self):
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = LifeInsuranceSystem()
    app.run()


