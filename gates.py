import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import math

class LoanExpertSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Loan Expert System")
        self.root.geometry("800x900")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Loan Application Assessment System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for organized sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Personal Information Tab
        self.personal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.personal_frame, text="Personal Info")
        self.create_personal_info_section()
        
        # Financial Information Tab
        self.financial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.financial_frame, text="Financial Info")
        self.create_financial_info_section()
        
        # Loan Details Tab
        self.loan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loan_frame, text="Loan Details")
        self.create_loan_details_section()
        
        # Results Tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Assessment Results")
        self.create_results_section()
        
        # Bottom buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Evaluate Application", 
                  command=self.evaluate_loan).pack(side=tk.LEFT, padx=(0, 10))
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
        
        # Employment Status
        ttk.Label(personal_info_frame, text="Employment Status:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.employment_var = tk.StringVar()
        employment_combo = ttk.Combobox(personal_info_frame, textvariable=self.employment_var, 
                                       values=["Full-time", "Part-time", "Self-employed", "Unemployed", "Retired"])
        employment_combo.grid(row=1, column=1, pady=2)
        employment_combo.state(['readonly'])
        
        # Years at Current Job
        ttk.Label(personal_info_frame, text="Years at Current Job:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.job_years_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.job_years_var, width=20).grid(row=2, column=1, pady=2)
        
        # Marital Status
        ttk.Label(personal_info_frame, text="Marital Status:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.marital_var = tk.StringVar()
        marital_combo = ttk.Combobox(personal_info_frame, textvariable=self.marital_var, 
                                    values=["Single", "Married", "Divorced", "Widowed"])
        marital_combo.grid(row=3, column=1, pady=2)
        marital_combo.state(['readonly'])
        
        # Number of Dependents
        ttk.Label(personal_info_frame, text="Number of Dependents:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.dependents_var = tk.StringVar()
        ttk.Entry(personal_info_frame, textvariable=self.dependents_var, width=20).grid(row=4, column=1, pady=2)
        
        # Criminal Record
        ttk.Label(personal_info_frame, text="Criminal Record:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.criminal_var = tk.StringVar()
        criminal_combo = ttk.Combobox(personal_info_frame, textvariable=self.criminal_var, 
                                     values=["None", "Minor violations", "Felony (>5 years ago)", "Recent felony (<5 years)"])
        criminal_combo.grid(row=5, column=1, pady=2)
        criminal_combo.state(['readonly'])
        
    def create_financial_info_section(self):
        # Financial Information
        financial_frame = ttk.LabelFrame(self.financial_frame, text="Financial Information", 
                                       padding="10")
        financial_frame.pack(fill=tk.BOTH, expand=True)
        
        # Annual Income
        ttk.Label(financial_frame, text="Annual Income ($):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.income_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.income_var, width=20).grid(row=0, column=1, pady=2)
        
        # Monthly Expenses
        ttk.Label(financial_frame, text="Monthly Expenses ($):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.expenses_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.expenses_var, width=20).grid(row=1, column=1, pady=2)
        
        # Credit Score
        ttk.Label(financial_frame, text="Credit Score (300-850):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.credit_score_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.credit_score_var, width=20).grid(row=2, column=1, pady=2)
        
        # Existing Debt
        ttk.Label(financial_frame, text="Total Existing Debt ($):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.existing_debt_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.existing_debt_var, width=20).grid(row=3, column=1, pady=2)
        
        # Assets
        ttk.Label(financial_frame, text="Total Assets ($):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.assets_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.assets_var, width=20).grid(row=4, column=1, pady=2)
        
        # Savings Account Balance
        ttk.Label(financial_frame, text="Savings Balance ($):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.savings_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.savings_var, width=20).grid(row=5, column=1, pady=2)
        
        # Banking History
        ttk.Label(financial_frame, text="Years with Bank:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.banking_history_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.banking_history_var, width=20).grid(row=6, column=1, pady=2)
        
        # Previous Loan History
        ttk.Label(financial_frame, text="Previous Loan History:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.loan_history_var = tk.StringVar()
        history_combo = ttk.Combobox(financial_frame, textvariable=self.loan_history_var, 
                                    values=["No previous loans", "Good payment history", "Occasional late payments", "Defaults/Foreclosure"])
        history_combo.grid(row=7, column=1, pady=2)
        history_combo.state(['readonly'])
        
    def create_loan_details_section(self):
        # Loan Details
        loan_details_frame = ttk.LabelFrame(self.loan_frame, text="Loan Request Details", 
                                          padding="10")
        loan_details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Loan Amount
        ttk.Label(loan_details_frame, text="Requested Loan Amount ($):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.loan_amount_var = tk.StringVar()
        ttk.Entry(loan_details_frame, textvariable=self.loan_amount_var, width=20).grid(row=0, column=1, pady=2)
        
        # Loan Term
        ttk.Label(loan_details_frame, text="Loan Term (years):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.loan_term_var = tk.StringVar()
        ttk.Entry(loan_details_frame, textvariable=self.loan_term_var, width=20).grid(row=1, column=1, pady=2)
        
        # Loan Purpose
        ttk.Label(loan_details_frame, text="Loan Purpose:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.loan_purpose_var = tk.StringVar()
        purpose_combo = ttk.Combobox(loan_details_frame, textvariable=self.loan_purpose_var, 
                                    values=["Home purchase", "Home improvement", "Auto purchase", "Business", 
                                           "Education", "Debt consolidation", "Personal/Other"])
        purpose_combo.grid(row=2, column=1, pady=2)
        purpose_combo.state(['readonly'])
        
        # Collateral
        ttk.Label(loan_details_frame, text="Collateral Available:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.collateral_var = tk.StringVar()
        collateral_combo = ttk.Combobox(loan_details_frame, textvariable=self.collateral_var, 
                                       values=["None", "Real Estate", "Vehicle", "Securities", "Other valuable assets"])
        collateral_combo.grid(row=3, column=1, pady=2)
        collateral_combo.state(['readonly'])
        
        # Collateral Value
        ttk.Label(loan_details_frame, text="Collateral Value ($):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.collateral_value_var = tk.StringVar()
        ttk.Entry(loan_details_frame, textvariable=self.collateral_value_var, width=20).grid(row=4, column=1, pady=2)
        
        # Down Payment
        ttk.Label(loan_details_frame, text="Down Payment ($):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.down_payment_var = tk.StringVar()
        ttk.Entry(loan_details_frame, textvariable=self.down_payment_var, width=20).grid(row=5, column=1, pady=2)
        
    def create_results_section(self):
        # Results display
        results_label = ttk.Label(self.results_frame, text="Assessment Results", font=('Arial', 12, 'bold'))
        results_label.pack(pady=(10, 10))
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, height=25, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def get_numeric_value(self, var, default=0):
        """Safely convert string to numeric value"""
        try:
            value = var.get().replace(',', '').replace('$', '')
            return float(value) if value else default
        except:
            return default
            
    def calculate_debt_to_income_ratio(self, monthly_debt, monthly_income):
        """Calculate debt-to-income ratio"""
        if monthly_income <= 0:
            return float('inf')
        return (monthly_debt / monthly_income) * 100
        
    def calculate_loan_to_value_ratio(self, loan_amount, collateral_value):
        """Calculate loan-to-value ratio"""
        if collateral_value <= 0:
            return float('inf')
        return (loan_amount / collateral_value) * 100
        
    def evaluate_credit_score(self, score):
        """Evaluate credit score and return score and description"""
        if score >= 800:
            return 100, "Excellent"
        elif score >= 740:
            return 85, "Very Good"
        elif score >= 670:
            return 70, "Good"
        elif score >= 580:
            return 45, "Fair"
        elif score >= 300:
            return 20, "Poor"
        else:
            return 0, "Invalid"
            
    def evaluate_loan(self):
        """Main loan evaluation logic"""
        try:
            # Get all input values
            age = self.get_numeric_value(self.age_var, 0)
            income = self.get_numeric_value(self.income_var, 0)
            expenses = self.get_numeric_value(self.expenses_var, 0)
            credit_score = self.get_numeric_value(self.credit_score_var, 0)
            existing_debt = self.get_numeric_value(self.existing_debt_var, 0)
            assets = self.get_numeric_value(self.assets_var, 0)
            savings = self.get_numeric_value(self.savings_var, 0)
            banking_years = self.get_numeric_value(self.banking_history_var, 0)
            loan_amount = self.get_numeric_value(self.loan_amount_var, 0)
            loan_term = self.get_numeric_value(self.loan_term_var, 0)
            collateral_value = self.get_numeric_value(self.collateral_value_var, 0)
            down_payment = self.get_numeric_value(self.down_payment_var, 0)
            job_years = self.get_numeric_value(self.job_years_var, 0)
            dependents = self.get_numeric_value(self.dependents_var, 0)
            
            # Initialize scoring system (out of 1000 points)
            total_score = 0
            max_score = 1000
            evaluation_details = []
            
            # 1. Credit Score Evaluation (200 points)
            credit_points, credit_desc = self.evaluate_credit_score(credit_score)
            credit_points = (credit_points / 100) * 200
            total_score += credit_points
            evaluation_details.append(f"Credit Score ({credit_score}): {credit_desc} - {credit_points:.0f}/200 points")
            
            # 2. Income Evaluation (150 points)
            if income > 100000:
                income_points = 150
            elif income > 75000:
                income_points = 120
            elif income > 50000:
                income_points = 90
            elif income > 30000:
                income_points = 60
            elif income > 15000:
                income_points = 30
            else:
                income_points = 0
            total_score += income_points
            evaluation_details.append(f"Annual Income (${income:,.0f}): {income_points}/150 points")
            
            # 3. Debt-to-Income Ratio (150 points)
            monthly_income = income / 12
            monthly_debt = existing_debt / 12 + (expenses if expenses > 0 else monthly_income * 0.3)
            
            # Estimate monthly loan payment
            if loan_term > 0:
                interest_rate = 0.06  # Assume 6% annual rate
                monthly_rate = interest_rate / 12
                num_payments = loan_term * 12
                if monthly_rate > 0:
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                else:
                    monthly_payment = loan_amount / num_payments
                total_monthly_debt = monthly_debt + monthly_payment
            else:
                total_monthly_debt = monthly_debt
                
            dti_ratio = self.calculate_debt_to_income_ratio(total_monthly_debt, monthly_income)
            
            if dti_ratio <= 28:
                dti_points = 150
            elif dti_ratio <= 36:
                dti_points = 120
            elif dti_ratio <= 43:
                dti_points = 80
            elif dti_ratio <= 50:
                dti_points = 40
            else:
                dti_points = 0
                
            total_score += dti_points
            evaluation_details.append(f"Debt-to-Income Ratio ({dti_ratio:.1f}%): {dti_points}/150 points")
            
            # 4. Employment Stability (100 points)
            employment_status = self.employment_var.get()
            employment_points = 0
            
            if employment_status == "Full-time":
                employment_points = 80
            elif employment_status == "Part-time":
                employment_points = 50
            elif employment_status == "Self-employed":
                employment_points = 60
            elif employment_status == "Retired":
                employment_points = 70
            else:
                employment_points = 0
                
            # Add job stability bonus
            if job_years >= 5:
                employment_points += 20
            elif job_years >= 2:
                employment_points += 10
            elif job_years >= 1:
                employment_points += 5
                
            employment_points = min(employment_points, 100)
            total_score += employment_points
            evaluation_details.append(f"Employment ({employment_status}, {job_years} years): {employment_points}/100 points")
            
            # 5. Assets and Collateral (150 points)
            asset_points = 0
            
            # Asset evaluation
            if assets >= loan_amount * 2:
                asset_points += 75
            elif assets >= loan_amount:
                asset_points += 50
            elif assets >= loan_amount * 0.5:
                asset_points += 30
            elif assets > 0:
                asset_points += 15
                
            # Collateral evaluation
            collateral_type = self.collateral_var.get()
            if collateral_type != "None" and collateral_value > 0:
                ltv_ratio = self.calculate_loan_to_value_ratio(loan_amount, collateral_value)
                if ltv_ratio <= 60:
                    asset_points += 75
                elif ltv_ratio <= 80:
                    asset_points += 50
                elif ltv_ratio <= 100:
                    asset_points += 25
                else:
                    asset_points += 10
                    
            asset_points = min(asset_points, 150)
            total_score += asset_points
            evaluation_details.append(f"Assets/Collateral (${assets:,.0f} assets, ${collateral_value:,.0f} collateral): {asset_points}/150 points")
            
            # 6. Criminal Record (50 points)
            criminal_record = self.criminal_var.get()
            criminal_points = 0
            
            if criminal_record == "None":
                criminal_points = 50
            elif criminal_record == "Minor violations":
                criminal_points = 35
            elif criminal_record == "Felony (>5 years ago)":
                criminal_points = 20
            else:
                criminal_points = 0
                
            total_score += criminal_points
            evaluation_details.append(f"Criminal Record ({criminal_record}): {criminal_points}/50 points")
            
            # 7. Banking History and Savings (75 points)
            banking_points = 0
            
            # Banking relationship
            if banking_years >= 5:
                banking_points += 25
            elif banking_years >= 2:
                banking_points += 15
            elif banking_years >= 1:
                banking_points += 10
                
            # Savings evaluation
            if savings >= loan_amount * 0.2:
                banking_points += 35
            elif savings >= loan_amount * 0.1:
                banking_points += 25
            elif savings >= 10000:
                banking_points += 15
            elif savings > 0:
                banking_points += 10
                
            # Loan history
            loan_history = self.loan_history_var.get()
            if loan_history == "Good payment history":
                banking_points += 15
            elif loan_history == "No previous loans":
                banking_points += 10
            elif loan_history == "Occasional late payments":
                banking_points += 5
            else:
                banking_points += 0
                
            banking_points = min(banking_points, 75)
            total_score += banking_points
            evaluation_details.append(f"Banking/Savings ({banking_years} years, ${savings:,.0f} savings): {banking_points}/75 points")
            
            # 8. Loan Purpose and Risk Assessment (75 points)
            purpose = self.loan_purpose_var.get()
            purpose_points = 0
            
            purpose_scores = {
                "Home purchase": 75,
                "Home improvement": 65,
                "Auto purchase": 60,
                "Education": 70,
                "Debt consolidation": 50,
                "Business": 45,
                "Personal/Other": 35
            }
            
            purpose_points = purpose_scores.get(purpose, 0)
            total_score += purpose_points
            evaluation_details.append(f"Loan Purpose ({purpose}): {purpose_points}/75 points")
            
            # 9. Age and Demographics (50 points)
            age_points = 0
            
            if 25 <= age <= 65:
                age_points = 50
            elif 18 <= age < 25:
                age_points = 30
            elif 65 < age <= 75:
                age_points = 40
            else:
                age_points = 20
                
            # Dependent penalty
            if dependents > 3:
                age_points -= 10
            elif dependents > 1:
                age_points -= 5
                
            age_points = max(age_points, 0)
            total_score += age_points
            evaluation_details.append(f"Demographics (Age {age}, {dependents} dependents): {age_points}/50 points")
            
            # Calculate final percentage and recommendation
            percentage_score = (total_score / max_score) * 100
            
            # Determine recommendation
            if percentage_score >= 80:
                recommendation = "APPROVED"
                risk_level = "Low Risk"
                suggested_rate = "Prime Rate (4.5-6.0%)"
            elif percentage_score >= 65:
                recommendation = "APPROVED WITH CONDITIONS"
                risk_level = "Medium Risk"
                suggested_rate = "Above Prime Rate (6.5-8.0%)"
            elif percentage_score >= 45:
                recommendation = "CONDITIONAL APPROVAL"
                risk_level = "High Risk"
                suggested_rate = "High Rate (8.5-12.0%) or Require Co-signer"
            else:
                recommendation = "DECLINED"
                risk_level = "Very High Risk"
                suggested_rate = "N/A"
            
            # Prepare detailed report
            report = f"""
LOAN APPLICATION ASSESSMENT REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

APPLICANT SUMMARY:
Age: {age}
Employment: {employment_status} ({job_years} years)
Annual Income: ${income:,.0f}
Credit Score: {credit_score}
Requested Loan: ${loan_amount:,.0f} for {loan_term} years
Purpose: {purpose}

FINANCIAL RATIOS:
Debt-to-Income Ratio: {dti_ratio:.1f}%
Loan-to-Value Ratio: {self.calculate_loan_to_value_ratio(loan_amount, collateral_value):.1f}%
Assets-to-Debt Ratio: {(assets / max(existing_debt, 1)):.2f}

EVALUATION BREAKDOWN:
"""
            
            for detail in evaluation_details:
                report += f"• {detail}\n"
                
            report += f"""
TOTAL SCORE: {total_score:.0f}/{max_score} ({percentage_score:.1f}%)

FINAL RECOMMENDATION: {recommendation}
RISK ASSESSMENT: {risk_level}
SUGGESTED INTEREST RATE: {suggested_rate}

ADDITIONAL CONSIDERATIONS:
"""
            
            # Add specific recommendations based on the evaluation
            if percentage_score < 80:
                report += "• Consider requiring additional collateral or co-signer\n"
            if dti_ratio > 36:
                report += "• High debt-to-income ratio - monitor carefully\n"
            if credit_score < 670:
                report += "• Credit score below good range - higher interest rate recommended\n"
            if criminal_record not in ["None", "Minor violations"]:
                report += "• Criminal history requires additional review\n"
            if job_years < 2:
                report += "• Limited employment history - consider probationary terms\n"
            if savings < loan_amount * 0.1:
                report += "• Low savings reserve - potential liquidity risk\n"
                
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, report)
            
            # Switch to results tab
            self.notebook.select(self.results_frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during evaluation: {str(e)}")
            
    def clear_all_fields(self):
        """Clear all input fields"""
        variables = [
            self.age_var, self.employment_var, self.job_years_var, self.marital_var,
            self.dependents_var, self.criminal_var, self.income_var, self.expenses_var,
            self.credit_score_var, self.existing_debt_var, self.assets_var, self.savings_var,
            self.banking_history_var, self.loan_history_var, self.loan_amount_var,
            self.loan_term_var, self.loan_purpose_var, self.collateral_var,
            self.collateral_value_var, self.down_payment_var
        ]
        
        for var in variables:
            var.set("")
            
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
                title="Save Assessment Report"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported successfully to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoanExpertSystem(root)
    root.mainloop()



