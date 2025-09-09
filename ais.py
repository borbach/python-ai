import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import math

class LifeInsuranceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Life Insurance Underwriting System")
        self.root.geometry("900x950")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Life Insurance Application Assessment System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for organized sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Personal Information Tab
        self.personal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.personal_frame, text="Personal Info")
        self.create_personal_info_section()
        
        # Health Information Tab
        self.health_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.health_frame, text="Health Info")
        self.create_health_info_section()
        
        # Lifestyle & Risk Tab
        self.lifestyle_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lifestyle_frame, text="Lifestyle & Risk")
        self.create_lifestyle_section()
        
        # Policy Details Tab
        self.policy_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.policy_frame, text="Policy Details")
        self.create_policy_details_section()
        
        # Results Tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Underwriting Results")
        self.create_results_section()
        
        # Bottom buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Evaluate Application", 
                  command=self.evaluate_application).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export Report", 
                  command=self.export_report).pack(side=tk.LEFT)
        
    def create_personal_info_section(self):
        # Personal Information
        personal_info_frame = ttk.LabelFrame(self.personal_frame, text="Applicant Information", 
                                           padding="10")
        personal_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Age
        ttk.Label(personal_info_frame, text="Age:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.age_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.age_var, width=20).grid(row=0, column=1, pady=2)
        
        # Gender
        ttk.Label(personal_info_frame, text="Gender:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(personal_info_frame, textvariable=self.gender_var, 
                                   values=["Male", "Female", "Other"])
        gender_combo.grid(row=1, column=1, pady=2)
        gender_combo.state(['readonly'])
        
        # Height (in inches)
        ttk.Label(personal_info_frame, text="Height (inches):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.height_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.height_var, width=20).grid(row=2, column=1, pady=2)
        
        # Weight (in pounds)
        ttk.Label(personal_info_frame, text="Weight (pounds):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.weight_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.weight_var, width=20).grid(row=3, column=1, pady=2)
        
        # Marital Status
        ttk.Label(personal_info_frame, text="Marital Status:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.marital_var = tk.StringVar()
        marital_combo = ttk.Combobox(personal_info_frame, textvariable=self.marital_var, 
                                    values=["Single", "Married", "Divorced", "Widowed"])
        marital_combo.grid(row=4, column=1, pady=2)
        marital_combo.state(['readonly'])
        
        # Occupation
        ttk.Label(personal_info_frame, text="Occupation:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.occupation_var = tk.StringVar()
        occupation_combo = ttk.Combobox(personal_info_frame, textvariable=self.occupation_var, 
                                       values=["Office Worker", "Teacher", "Doctor/Nurse", "Construction Worker", 
                                              "Police Officer", "Pilot", "Military", "Driver/Trucker", 
                                              "Mining/Oil Worker", "Professional Athlete", "Retired", "Other"])
        occupation_combo.grid(row=5, column=1, pady=2)
        occupation_combo.state(['readonly'])
        
        # Annual Income
        ttk.Label(personal_info_frame, text="Annual Income ($):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.income_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.income_var, width=20).grid(row=6, column=1, pady=2)
        
    def create_health_info_section(self):
        # Create scrollable frame for health information
        canvas = tk.Canvas(self.health_frame)
        scrollbar = ttk.Scrollbar(self.health_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # General Health
        general_health_frame = ttk.LabelFrame(scrollable_frame, text="General Health", padding="10")
        general_health_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(general_health_frame, text="Overall Health Status:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.health_status_var = tk.StringVar()
        health_combo = ttk.Combobox(general_health_frame, textvariable=self.health_status_var, 
                                   values=["Excellent", "Very Good", "Good", "Fair", "Poor"])
        health_combo.grid(row=0, column=1, pady=2)
        health_combo.state(['readonly'])
        
        # Blood Pressure
        ttk.Label(general_health_frame, text="Blood Pressure (systolic/diastolic):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.blood_pressure_var = tk.StringVar()
        ttk.Entry(general_health_frame, textvariable=self.blood_pressure_var, width=20).grid(row=1, column=1, pady=2)
        
        # Cholesterol Level
        ttk.Label(general_health_frame, text="Cholesterol Level (mg/dL):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cholesterol_var = tk.StringVar()
        ttk.Entry(general_health_frame, textvariable=self.cholesterol_var, width=20).grid(row=2, column=1, pady=2)
        
        # Medical Conditions
        conditions_frame = ttk.LabelFrame(scrollable_frame, text="Medical Conditions", padding="10")
        conditions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Diabetes
        self.diabetes_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Diabetes", variable=self.diabetes_var).grid(row=0, column=0, sticky=tk.W)
        
        # Heart Disease
        self.heart_disease_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Heart Disease", variable=self.heart_disease_var).grid(row=0, column=1, sticky=tk.W)
        
        # Cancer
        self.cancer_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Cancer (current or history)", variable=self.cancer_var).grid(row=1, column=0, sticky=tk.W)
        
        # Stroke
        self.stroke_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Stroke", variable=self.stroke_var).grid(row=1, column=1, sticky=tk.W)
        
        # Mental Health Conditions
        self.mental_health_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Mental Health Conditions", variable=self.mental_health_var).grid(row=2, column=0, sticky=tk.W)
        
        # Respiratory Issues
        self.respiratory_var = tk.BooleanVar()
        ttk.Checkbutton(conditions_frame, text="Asthma/COPD/Respiratory", variable=self.respiratory_var).grid(row=2, column=1, sticky=tk.W)
        
        # Surgeries
        surgery_frame = ttk.LabelFrame(scrollable_frame, text="Medical History", padding="10")
        surgery_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(surgery_frame, text="Major Surgeries in Last 5 Years:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.surgeries_var = tk.StringVar()
        surgeries_combo = ttk.Combobox(surgery_frame, textvariable=self.surgeries_var, 
                                      values=["None", "1 minor surgery", "1 major surgery", 
                                             "Multiple surgeries", "Heart surgery", "Cancer surgery"])
        surgeries_combo.grid(row=0, column=1, pady=2)
        surgeries_combo.state(['readonly'])
        
        # Hospitalizations
        ttk.Label(surgery_frame, text="Hospitalizations in Last 2 Years:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.hospitalizations_var = tk.StringVar()
        hosp_combo = ttk.Combobox(surgery_frame, textvariable=self.hospitalizations_var, 
                                 values=["None", "1 time", "2-3 times", "4+ times"])
        hosp_combo.grid(row=1, column=1, pady=2)
        hosp_combo.state(['readonly'])
        
        # Current Medications
        ttk.Label(surgery_frame, text="Current Medications:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.medications_var = tk.StringVar()
        med_combo = ttk.Combobox(surgery_frame, textvariable=self.medications_var, 
                                values=["None", "Vitamins only", "1-2 prescriptions", 
                                       "3-5 prescriptions", "5+ prescriptions"])
        med_combo.grid(row=2, column=1, pady=2)
        med_combo.state(['readonly'])
        
        # Family History
        family_frame = ttk.LabelFrame(scrollable_frame, text="Family Medical History", padding="10")
        family_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Family Heart Disease
        self.family_heart_var = tk.BooleanVar()
        ttk.Checkbutton(family_frame, text="Heart Disease (parents/siblings)", variable=self.family_heart_var).grid(row=0, column=0, sticky=tk.W)
        
        # Family Cancer
        self.family_cancer_var = tk.BooleanVar()
        ttk.Checkbutton(family_frame, text="Cancer (parents/siblings)", variable=self.family_cancer_var).grid(row=0, column=1, sticky=tk.W)
        
        # Family Diabetes
        self.family_diabetes_var = tk.BooleanVar()
        ttk.Checkbutton(family_frame, text="Diabetes (parents/siblings)", variable=self.family_diabetes_var).grid(row=1, column=0, sticky=tk.W)
        
        # Family Early Death
        self.family_early_death_var = tk.BooleanVar()
        ttk.Checkbutton(family_frame, text="Early Death <60 (parents/siblings)", variable=self.family_early_death_var).grid(row=1, column=1, sticky=tk.W)
        
    def create_lifestyle_section(self):
        # Lifestyle Risk Factors
        lifestyle_frame = ttk.LabelFrame(self.lifestyle_frame, text="Lifestyle & Risk Factors", padding="10")
        lifestyle_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Smoking
        ttk.Label(lifestyle_frame, text="Smoking Status:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.smoking_var = tk.StringVar()
        smoking_combo = ttk.Combobox(lifestyle_frame, textvariable=self.smoking_var, 
                                    values=["Never smoked", "Former smoker (>2 years)", 
                                           "Former smoker (<2 years)", "Current light smoker (<10/day)",
                                           "Current heavy smoker (10+/day)"])
        smoking_combo.grid(row=0, column=1, pady=2)
        smoking_combo.state(['readonly'])
        
        # Alcohol Consumption
        ttk.Label(lifestyle_frame, text="Alcohol Consumption:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.alcohol_var = tk.StringVar()
        alcohol_combo = ttk.Combobox(lifestyle_frame, textvariable=self.alcohol_var, 
                                    values=["None", "Occasional (1-2 drinks/week)", 
                                           "Moderate (3-7 drinks/week)", "Heavy (8-14 drinks/week)",
                                           "Excessive (15+ drinks/week)": -100
            }
            
            alcohol_score = alcohol_scores.get(alcohol_status, -20)
            lifestyle_score += alcohol_score
            if "Heavy" in alcohol_status or "Excessive" in alcohol_status:
                risk_factors.append("Excessive alcohol consumption")
                
            # Exercise
            exercise_status = self.exercise_var.get()
            exercise_scores = {
                "Daily": 20,
                "4-6 times/week": 15,
                "2-3 times/week": 10,
                "1 time/week": 0,
                "Rarely": -20,
                "Never": -40
            }
            
            exercise_score = exercise_scores.get(exercise_status, -10)
            lifestyle_score += exercise_score
            
            # Drug Use
            drug_status = self.drugs_var.get()
            drug_scores = {
                "Never": 0,
                "Past use (>5 years ago)": -10,
                "Past use (<5 years ago)": -30,
                "Occasional current use": -100,
                "Regular current use": -300
            }
            
            drug_score = drug_scores.get(drug_status, -50)
            lifestyle_score += drug_score
            if "current use" in drug_status:
                risk_factors.append("Current drug use")
                
            total_score += lifestyle_score
            evaluation_details.append(f"Lifestyle Factors (Smoking: {smoking_score}, Alcohol: {alcohol_score}, Exercise: {exercise_score}, Drugs: {drug_score}): {lifestyle_score} points")
            
            # 8. Occupation Risk Evaluation
            occupation = self.occupation_var.get()
            occupation_scores = {
                "Office Worker": 0,
                "Teacher": 0,
                "Doctor/Nurse": -10,
                "Construction Worker": -50,
                "Police Officer": -75,
                "Pilot": -100,
                "Military": -150,
                "Driver/Trucker": -40,
                "Mining/Oil Worker": -200,
                "Professional Athlete": -60,
                "Retired": 0,
                "Other": -25
            }
            
            occupation_score = occupation_scores.get(occupation, -25)
            if occupation_score <= -100:
                risk_factors.append(f"High-risk occupation: {occupation}")
                
            total_score += occupation_score
            evaluation_details.append(f"Occupation Risk ({occupation}): {occupation_score} points")
            
            # 9. High-Risk Activities
            risk_activities_score = 0
            
            if self.extreme_sports_var.get():
                risk_activities_score -= 100
                risk_factors.append("Extreme sports participation")
                
            if self.dangerous_hobbies_var.get():
                risk_activities_score -= 75
                risk_factors.append("Dangerous hobbies")
                
            travel_risk = self.travel_risk_var.get()
            travel_scores = {
                "Never": 0,
                "Rarely": -5,
                "Occasionally": -15,
                "Frequently": -40
            }
            
            travel_score = travel_scores.get(travel_risk, -10)
            risk_activities_score += travel_score
            
            total_score += risk_activities_score
            evaluation_details.append(f"High-Risk Activities: {risk_activities_score} points")
            
            # 10. Medical History
            medical_history_score = 0
            
            surgeries = self.surgeries_var.get()
            surgery_scores = {
                "None": 0,
                "1 minor surgery": -10,
                "1 major surgery": -30,
                "Multiple surgeries": -60,
                "Heart surgery": -150,
                "Cancer surgery": -200
            }
            
            surgery_score = surgery_scores.get(surgeries, -20)
            medical_history_score += surgery_score
            
            hospitalizations = self.hospitalizations_var.get()
            hosp_scores = {
                "None": 0,
                "1 time": -20,
                "2-3 times": -50,
                "4+ times": -100
            }
            
            hosp_score = hosp_scores.get(hospitalizations, -25)
            medical_history_score += hosp_score
            
            medications = self.medications_var.get()
            med_scores = {
                "None": 0,
                "Vitamins only": 5,
                "1-2 prescriptions": -10,
                "3-5 prescriptions": -40,
                "5+ prescriptions": -80
            }
            
            med_score = med_scores.get(medications, -20)
            medical_history_score += med_score
            
            if surgery_score <= -100 or hosp_score <= -50 or med_score <= -40:
                risk_factors.append("Significant medical history")
                
            total_score += medical_history_score
            evaluation_details.append(f"Medical History (Surgeries: {surgery_score}, Hospitalizations: {hosp_score}, Medications: {med_score}): {medical_history_score} points")
            
            # 11. Financial Underwriting
            financial_score = 0
            
            # Coverage to income ratio
            if income > 0:
                coverage_ratio = coverage_amount / income
                if coverage_ratio <= 10:
                    financial_score = 0
                elif coverage_ratio <= 15:
                    financial_score = -25
                elif coverage_ratio <= 20:
                    financial_score = -50
                else:
                    financial_score = -100
                    risk_factors.append("Excessive coverage relative to income")
            else:
                financial_score = -50
                risk_factors.append("No income reported")
                
            # Total coverage check
            total_coverage = coverage_amount + existing_coverage
            if total_coverage > income * 20:
                financial_score -= 75
                risk_factors.append("Total coverage exceeds financial justification")
                
            total_score += financial_score
            evaluation_details.append(f"Financial Underwriting (Coverage ratio: {coverage_ratio:.1f}x income): {financial_score} points")
            
            # Ensure score doesn't go below 0
            total_score = max(total_score, 0)
            
            # Calculate final percentage and recommendation
            percentage_score = (total_score / 1000) * 100
            
            # Determine recommendation and premium rating
            if percentage_score >= 90:
                recommendation = "APPROVED - SUPER PREFERRED"
                risk_class = "Super Preferred"
                premium_rating = "Standard rates - 10% discount"
            elif percentage_score >= 80:
                recommendation = "APPROVED - PREFERRED"
                risk_class = "Preferred"
                premium_rating = "Standard rates"
            elif percentage_score >= 70:
                recommendation = "APPROVED - STANDARD PLUS"
                risk_class = "Standard Plus"
                premium_rating = "Standard rates + 25%"
            elif percentage_score >= 60:
                recommendation = "APPROVED - STANDARD"
                risk_class = "Standard"
                premium_rating = "Standard rates + 50%"
            elif percentage_score >= 50:
                recommendation = "APPROVED - SUBSTANDARD"
                risk_class = "Table 2-4"
                premium_rating = "Standard rates + 75-150%"
            elif percentage_score >= 40:
                recommendation = "APPROVED - HIGH SUBSTANDARD"
                risk_class = "Table 6-8"
                premium_rating = "Standard rates + 200-300%"
            elif percentage_score >= 30:
                recommendation = "CONDITIONAL APPROVAL"
                risk_class = "Requires Medical Exam"
                premium_rating = "Pending further underwriting"
            else:
                recommendation = "DECLINED"
                risk_class = "Uninsurable"
                premium_rating = "N/A"
            
            # Calculate estimated annual premium
            base_premium = 0
            if recommendation != "DECLINED":
                # Simplified premium calculation based on age, coverage, and risk
                base_rate_per_1000 = 1.5 + (age - 30) * 0.1  # Base rate increases with age
                base_premium = (coverage_amount / 1000) * base_rate_per_1000
                
                # Apply risk multiplier
                if "SUPER PREFERRED" in recommendation:
                    base_premium *= 0.9
                elif "PREFERRED" in recommendation:
                    base_premium *= 1.0
                elif "STANDARD PLUS" in recommendation:
                    base_premium *= 1.25
                elif "STANDARD" in recommendation:
                    base_premium *= 1.5
                elif "SUBSTANDARD" in recommendation:
                    base_premium *= 2.0
                elif "HIGH SUBSTANDARD" in recommendation:
                    base_premium *= 3.0
                    
            # Prepare detailed report
            report = f"""
LIFE INSURANCE UNDERWRITING ASSESSMENT REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

APPLICANT SUMMARY:
Age: {age} years
Gender: {self.gender_var.get()}
Height: {height}" Weight: {weight} lbs (BMI: {bmi:.1f})
Occupation: {occupation}
Annual Income: ${income:,.0f}
Health Status: {health_status}
Blood Pressure: {self.blood_pressure_var.get()}

POLICY REQUEST:
Requested Coverage: ${coverage_amount:,.0f}
Policy Type: {self.policy_type_var.get()}
Term Length: {self.term_length_var.get()} years
Existing Coverage: ${existing_coverage:,.0f}
Purpose: {self.purpose_var.get()}

RISK FACTORS IDENTIFIED:
"""
            
            if risk_factors:
                for risk in risk_factors:
                    report += f"• {risk}\n"
            else:
                report += "• No significant risk factors identified\n"
                
            report += f"""
UNDERWRITING EVALUATION BREAKDOWN:
"""
            
            for detail in evaluation_details:
                report += f"• {detail}\n"
                
            report += f"""
TOTAL SCORE: {total_score:.0f}/1000 ({percentage_score:.1f}%)

FINAL RECOMMENDATION: {recommendation}
RISK CLASSIFICATION: {risk_class}
PREMIUM RATING: {premium_rating}
ESTIMATED ANNUAL PREMIUM: ${base_premium:,.0f}

UNDERWRITING NOTES:
"""
            
            # Add specific underwriting notes
            if percentage_score >= 80:
                report += "• Excellent risk profile - minimal health and lifestyle concerns\n"
                report += "• Standard underwriting process recommended\n"
            elif percentage_score >= 60:
                report += "• Acceptable risk with some concerns noted\n"
                report += "• May require medical records review\n"
            elif percentage_score >= 40:
                report += "• Significant risk factors present\n"
                report += "• Medical exam and detailed medical records required\n"
                report += "• Consider reduced coverage amount\n"
            else:
                report += "• Multiple high-risk factors identified\n"
                report += "• Application does not meet current underwriting standards\n"
                report += "• Consider reapplication after risk improvement\n"
                
            # Additional recommendations
            report += "\nRECOMMENDATIONS:\n"
            
            if age > 60:
                report += "• Consider medical exam due to age\n"
            if bmi > 30:
                report += "• Weight management counseling recommended\n"
            if "Current smoker" in [r for r in risk_factors]:
                report += "• Smoking cessation program strongly recommended\n"
            if any("family history" in r.lower() for r in risk_factors):
                report += "• Regular health screenings recommended\n"
            if coverage_amount > income * 15:
                report += "• Financial justification documentation required\n"
                
            # Coverage alternatives if declined
            if recommendation == "DECLINED":
                report += "\nALTERNATIVE OPTIONS:\n"
                report += "• Consider guaranteed issue life insurance (lower coverage limits)\n"
                report += "• Group life insurance through employer\n"
                report += "• Accidental death coverage\n"
                report += "• Reapply after addressing major risk factors\n"
                
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, report)
            
            # Switch to results tab
            self.notebook.select(self.results_frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during evaluation: {str(e)}")
            
    def clear_all_fields(self):
        """Clear all input fields"""
        # String variables
        string_vars = [
            self.age_var, self.gender_var, self.height_var, self.weight_var, self.marital_var,
            self.occupation_var, self.income_var, self.health_status_var, self.blood_pressure_var,
            self.cholesterol_var, self.surgeries_var, self.hospitalizations_var, self.medications_var,
            self.smoking_var, self.alcohol_var, self.exercise_var, self.drugs_var, self.travel_risk_var,
            self.coverage_amount_var, self.policy_type_var, self.term_length_var, 
            self.existing_coverage_var, self.purpose_var
        ]
        
        for var in string_vars:
            var.set("")
            
        # Boolean variables
        boolean_vars = [
            self.diabetes_var, self.heart_disease_var, self.cancer_var, self.stroke_var,
            self.mental_health_var, self.respiratory_var, self.family_heart_var, 
            self.family_cancer_var, self.family_diabetes_var, self.family_early_death_var,
            self.extreme_sports_var, self.dangerous_hobbies_var
        ]
        
        for var in boolean_vars:
            var.set(False)
            
        self.results_text.delete(1.0, tk.END)
        messagebox.showinfo("Cleared", "All fields have been cleared.")
        
    def export_report(self):
        """Export the assessment report to a text file"""
        try:
            report_content = self.results_text.get(1.0, tk.END)
            if not report_content.strip():
                messagebox.showwarning("Warning", "No assessment report to export. Please evaluate an application first.")
                return
                
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Life Insurance Assessment Report"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported successfully to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LifeInsuranceSystem(root)
    root.mainloop()/week)"])
        alcohol_combo.grid(row=1, column=1, pady=2)
        alcohol_combo.state(['readonly'])
        
        # Exercise
        ttk.Label(lifestyle_frame, text="Exercise Frequency:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.exercise_var = tk.StringVar()
        exercise_combo = ttk.Combobox(lifestyle_frame, textvariable=self.exercise_var, 
                                     values=["Daily", "4-6 times/week", "2-3 times/week", 
                                            "1 time/week", "Rarely", "Never"])
        exercise_combo.grid(row=2, column=1, pady=2)
        exercise_combo.state(['readonly'])
        
        # Drug Use
        ttk.Label(lifestyle_frame, text="Recreational Drug Use:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.drugs_var = tk.StringVar()
        drugs_combo = ttk.Combobox(lifestyle_frame, textvariable=self.drugs_var, 
                                  values=["Never", "Past use (>5 years ago)", "Past use (<5 years ago)",
                                         "Occasional current use", "Regular current use"])
        drugs_combo.grid(row=3, column=1, pady=2)
        drugs_combo.state(['readonly'])
        
        # High-Risk Activities
        risk_frame = ttk.LabelFrame(self.lifestyle_frame, text="High-Risk Activities", padding="10")
        risk_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Extreme Sports
        self.extreme_sports_var = tk.BooleanVar()
        ttk.Checkbutton(risk_frame, text="Extreme Sports (skydiving, rock climbing, etc.)", 
                       variable=self.extreme_sports_var).grid(row=0, column=0, sticky=tk.W)
        
        # Dangerous Hobbies
        self.dangerous_hobbies_var = tk.BooleanVar()
        ttk.Checkbutton(risk_frame, text="Dangerous Hobbies (racing, mountaineering, etc.)", 
                       variable=self.dangerous_hobbies_var).grid(row=1, column=0, sticky=tk.W)
        
        # Travel to High-Risk Areas
        ttk.Label(risk_frame, text="Travel to High-Risk Areas:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.travel_risk_var = tk.StringVar()
        travel_combo = ttk.Combobox(risk_frame, textvariable=self.travel_risk_var, 
                                   values=["Never", "Rarely", "Occasionally", "Frequently"])
        travel_combo.grid(row=2, column=1, pady=2)
        travel_combo.state(['readonly'])
        
    def create_policy_details_section(self):
        # Policy Information
        policy_info_frame = ttk.LabelFrame(self.policy_frame, text="Policy Details", padding="10")
        policy_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Coverage Amount
        ttk.Label(policy_info_frame, text="Requested Coverage Amount ($):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.coverage_amount_var = tk.StringVar()
        ttk.Entry(policy_info_frame, textvariable=self.coverage_amount_var, width=20).grid(row=0, column=1, pady=2)
        
        # Policy Type
        ttk.Label(policy_info_frame, text="Policy Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.policy_type_var = tk.StringVar()
        policy_combo = ttk.Combobox(policy_info_frame, textvariable=self.policy_type_var, 
                                   values=["Term Life", "Whole Life", "Universal Life", "Variable Life"])
        policy_combo.grid(row=1, column=1, pady=2)
        policy_combo.state(['readonly'])
        
        # Term Length (if applicable)
        ttk.Label(policy_info_frame, text="Term Length (years, if Term Life):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.term_length_var = tk.StringVar()
        ttk.Entry(policy_info_frame, textvariable=self.term_length_var, width=20).grid(row=2, column=1, pady=2)
        
        # Existing Life Insurance
        ttk.Label(policy_info_frame, text="Existing Life Insurance ($):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.existing_coverage_var = tk.StringVar()
        ttk.Entry(policy_info_frame, textvariable=self.existing_coverage_var, width=20).grid(row=3, column=1, pady=2)
        
        # Purpose of Insurance
        ttk.Label(policy_info_frame, text="Purpose of Insurance:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.purpose_var = tk.StringVar()
        purpose_combo = ttk.Combobox(policy_info_frame, textvariable=self.purpose_var, 
                                    values=["Income replacement", "Mortgage protection", "Estate planning",
                                           "Business protection", "Debt coverage", "Other"])
        purpose_combo.grid(row=4, column=1, pady=2)
        purpose_combo.state(['readonly'])
        
    def create_results_section(self):
        # Results display
        results_label = ttk.Label(self.results_frame, text="Underwriting Assessment Results", 
                                 font=('Arial', 12, 'bold'))
        results_label.pack(pady=(10, 10))
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, height=30, width=90)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def get_numeric_value(self, var, default=0):
        """Safely convert string to numeric value"""
        try:
            value = var.get().replace(',', '').replace('$', '')
            return float(value) if value else default
        except:
            return default
            
    def calculate_bmi(self, height, weight):
        """Calculate BMI"""
        if height <= 0 or weight <= 0:
            return 0
        height_meters = height * 0.0254  # Convert inches to meters
        weight_kg = weight * 0.453592    # Convert pounds to kg
        return weight_kg / (height_meters ** 2)
        
    def parse_blood_pressure(self, bp_string):
        """Parse blood pressure string like '120/80'"""
        try:
            if '/' in bp_string:
                systolic, diastolic = bp_string.split('/')
                return int(systolic.strip()), int(diastolic.strip())
            return 0, 0
        except:
            return 0, 0
            
    def evaluate_application(self):
        """Main evaluation logic for life insurance application"""
        try:
            # Get all input values
            age = self.get_numeric_value(self.age_var, 0)
            height = self.get_numeric_value(self.height_var, 0)
            weight = self.get_numeric_value(self.weight_var, 0)
            income = self.get_numeric_value(self.income_var, 0)
            coverage_amount = self.get_numeric_value(self.coverage_amount_var, 0)
            existing_coverage = self.get_numeric_value(self.existing_coverage_var, 0)
            cholesterol = self.get_numeric_value(self.cholesterol_var, 0)
            
            # Initialize scoring system (out of 1000 points)
            total_score = 1000  # Start with perfect score and deduct points for risks
            evaluation_details = []
            risk_factors = []
            
            # 1. Age Evaluation
            age_score = 0
            if age < 18:
                age_score = -500
                risk_factors.append("Age below minimum (18)")
            elif age <= 30:
                age_score = 0
            elif age <= 40:
                age_score = -20
            elif age <= 50:
                age_score = -50
            elif age <= 60:
                age_score = -100
            elif age <= 70:
                age_score = -200
            elif age <= 75:
                age_score = -350
            else:
                age_score = -500
                risk_factors.append("Age above maximum insurability (75)")
                
            total_score += age_score
            evaluation_details.append(f"Age Assessment ({age} years): {age_score} points")
            
            # 2. BMI Evaluation
            bmi = self.calculate_bmi(height, weight)
            bmi_score = 0
            bmi_category = ""
            
            if bmi == 0:
                bmi_score = -50
                bmi_category = "Invalid height/weight"
            elif bmi < 18.5:
                bmi_score = -100
                bmi_category = "Underweight"
                risk_factors.append("Underweight (BMI < 18.5)")
            elif bmi <= 24.9:
                bmi_score = 0
                bmi_category = "Normal"
            elif bmi <= 29.9:
                bmi_score = -30
                bmi_category = "Overweight"
            elif bmi <= 34.9:
                bmi_score = -80
                bmi_category = "Obese Class I"
                risk_factors.append("Obesity Class I")
            elif bmi <= 39.9:
                bmi_score = -150
                bmi_category = "Obese Class II"
                risk_factors.append("Obesity Class II")
            else:
                bmi_score = -250
                bmi_category = "Obese Class III"
                risk_factors.append("Severe Obesity")
                
            total_score += bmi_score
            evaluation_details.append(f"BMI Assessment ({bmi:.1f} - {bmi_category}): {bmi_score} points")
            
            # 3. Health Status Evaluation
            health_status = self.health_status_var.get()
            health_score = 0
            
            health_scores = {
                "Excellent": 0,
                "Very Good": -10,
                "Good": -25,
                "Fair": -75,
                "Poor": -200
            }
            
            health_score = health_scores.get(health_status, -50)
            if health_status in ["Fair", "Poor"]:
                risk_factors.append(f"Poor health status: {health_status}")
                
            total_score += health_score
            evaluation_details.append(f"Health Status ({health_status}): {health_score} points")
            
            # 4. Blood Pressure Evaluation
            systolic, diastolic = self.parse_blood_pressure(self.blood_pressure_var.get())
            bp_score = 0
            bp_category = ""
            
            if systolic == 0 and diastolic == 0:
                bp_score = -25
                bp_category = "Not provided"
            elif systolic < 120 and diastolic < 80:
                bp_score = 0
                bp_category = "Normal"
            elif systolic < 130 and diastolic < 80:
                bp_score = -10
                bp_category = "Elevated"
            elif systolic < 140 or diastolic < 90:
                bp_score = -40
                bp_category = "Stage 1 Hypertension"
                risk_factors.append("Hypertension Stage 1")
            elif systolic < 180 or diastolic < 120:
                bp_score = -100
                bp_category = "Stage 2 Hypertension"
                risk_factors.append("Hypertension Stage 2")
            else:
                bp_score = -200
                bp_category = "Hypertensive Crisis"
                risk_factors.append("Severe Hypertension")
                
            total_score += bp_score
            evaluation_details.append(f"Blood Pressure ({systolic}/{diastolic} - {bp_category}): {bp_score} points")
            
            # 5. Medical Conditions Evaluation
            conditions_score = 0
            
            if self.diabetes_var.get():
                conditions_score -= 150
                risk_factors.append("Diabetes")
                
            if self.heart_disease_var.get():
                conditions_score -= 200
                risk_factors.append("Heart Disease")
                
            if self.cancer_var.get():
                conditions_score -= 250
                risk_factors.append("Cancer History")
                
            if self.stroke_var.get():
                conditions_score -= 200
                risk_factors.append("Stroke History")
                
            if self.mental_health_var.get():
                conditions_score -= 50
                risk_factors.append("Mental Health Conditions")
                
            if self.respiratory_var.get():
                conditions_score -= 75
                risk_factors.append("Respiratory Conditions")
                
            total_score += conditions_score
            evaluation_details.append(f"Medical Conditions: {conditions_score} points")
            
            # 6. Family History Evaluation
            family_score = 0
            
            if self.family_heart_var.get():
                family_score -= 30
                risk_factors.append("Family history of heart disease")
                
            if self.family_cancer_var.get():
                family_score -= 40
                risk_factors.append("Family history of cancer")
                
            if self.family_diabetes_var.get():
                family_score -= 25
                risk_factors.append("Family history of diabetes")
                
            if self.family_early_death_var.get():
                family_score -= 60
                risk_factors.append("Family history of early death")
                
            total_score += family_score
            evaluation_details.append(f"Family History: {family_score} points")
            
            # 7. Lifestyle Factors Evaluation
            lifestyle_score = 0
            
            # Smoking
            smoking_status = self.smoking_var.get()
            smoking_scores = {
                "Never smoked": 0,
                "Former smoker (>2 years)": -30,
                "Former smoker (<2 years)": -60,
                "Current light smoker (<10/day)": -150,
                "Current heavy smoker (10+/day)": -300
            }
            
            smoking_score = smoking_scores.get(smoking_status, -50)
            lifestyle_score += smoking_score
            if "Current" in smoking_status:
                risk_factors.append("Current smoker")
                
            # Alcohol
            alcohol_status = self.alcohol_var.get()
            alcohol_scores = {
                "None": 0,
                "Occasional (1-2 drinks/week)": 5,
                "Moderate (3-7 drinks/week)": 0,
                "Heavy (8-14 drinks/week)": -40,
                "Excessive (15+ drinks


