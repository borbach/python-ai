import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import math

class RentalPropertyCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Rental Property Profit/Loss Calculator")
#        self.root.geometry("600x700")
        self.root.geometry("600x1000")
        self.root.resizable(True, True)
        
        # Variables to store input values
        self.mortgage_rate = tk.DoubleVar()
        self.mortgage_amount = tk.DoubleVar()
        self.down_payment = tk.DoubleVar()
        self.mortgage_length = tk.IntVar()
        
        self.tax1 = tk.DoubleVar()
        self.tax2 = tk.DoubleVar()
        self.tax3 = tk.DoubleVar()
        self.insurance1 = tk.DoubleVar()
        self.insurance2 = tk.DoubleVar()
        self.water_bill = tk.DoubleVar()
        
        self.rent_entries = []
        self.num_rent_units = tk.IntVar(value=2)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Rental Property Calculator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Mortgage Information Section
        mortgage_frame = ttk.LabelFrame(main_frame, text="Mortgage Information", padding="10")
        mortgage_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mortgage_frame, text="Mortgage Rate (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(mortgage_frame, textvariable=self.mortgage_rate, width=15).grid(row=0, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(mortgage_frame, text="Mortgage Amount ($):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(mortgage_frame, textvariable=self.mortgage_amount, width=15).grid(row=1, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(mortgage_frame, text="Down Payment ($):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(mortgage_frame, textvariable=self.down_payment, width=15).grid(row=2, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(mortgage_frame, text="Mortgage Length (years):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(mortgage_frame, textvariable=self.mortgage_length, width=15).grid(row=3, column=1, padx=(10, 0), pady=2)
        
        # Annual Expenses Section
        expenses_frame = ttk.LabelFrame(main_frame, text="Annual Expenses", padding="10")
        expenses_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(expenses_frame, text="School Tax (Annual $):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.tax1, width=15).grid(row=0, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(expenses_frame, text="County Tax (Annual $):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.tax2, width=15).grid(row=1, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(expenses_frame, text="Long Beach Tax (Annual $):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.tax3, width=15).grid(row=2, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(expenses_frame, text="Hazard Insurance (Annual $):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.insurance1, width=15).grid(row=3, column=1, padx=(10, 0), pady=2)

        ttk.Label(expenses_frame, text="Flood Insurance (Annual $):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.insurance2, width=15).grid(row=4, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(expenses_frame, text="Water Bill (Annual $):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(expenses_frame, textvariable=self.water_bill, width=15).grid(row=5, column=1, padx=(10, 0), pady=2)
        
        # Rental Income Section
        income_frame = ttk.LabelFrame(main_frame, text="Rental Income", padding="10")
        income_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Number of rental units
        rent_config_frame = ttk.Frame(income_frame)
        rent_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rent_config_frame, text="Number of Rental Units:").pack(side=tk.LEFT)
        ttk.Spinbox(rent_config_frame, from_=1, to=10, textvariable=self.num_rent_units, 
                   width=5, command=self.update_rent_entries).pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame for rent entries
        self.rent_frame = ttk.Frame(income_frame)
        self.rent_frame.pack(fill=tk.X)
        
        self.update_rent_entries()
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Fill All", command=self.fill_all).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT)

        
        # Results Frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.results_text = tk.Text(self.results_frame, height=12, width=70, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store calculation results
        self.last_calculation = None
        
    def update_rent_entries(self):
        # Clear existing entries
        for widget in self.rent_frame.winfo_children():
            widget.destroy()
        
        self.rent_entries = []
        num_units = self.num_rent_units.get()
        
        for i in range(num_units):
            rent_var = tk.DoubleVar()
            self.rent_entries.append(rent_var)
            
            ttk.Label(self.rent_frame, text=f"Unit {i+1} Monthly Rent ($):").grid(
                row=i, column=0, sticky=tk.W, pady=2)
            ttk.Entry(self.rent_frame, textvariable=rent_var, width=15).grid(
                row=i, column=1, padx=(10, 0), pady=2)
    
    def calculate_mortgage_payment(self, principal, annual_rate, years):
        """Calculate monthly mortgage payment using the standard formula"""
        if annual_rate == 0:
            return principal / (years * 12)
        
        monthly_rate = annual_rate / 100 / 12
        num_payments = years * 12
        
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        
        return monthly_payment
    
    def calculate(self):
        try:
            # Get mortgage details
            rate = self.mortgage_rate.get()
            total_amount = self.mortgage_amount.get()
            down_payment = self.down_payment.get()
            years = self.mortgage_length.get()
            
            # Calculate loan principal (amount after down payment)
            principal = total_amount - down_payment
            
            if principal <= 0:
                messagebox.showerror("Error", "Principal amount must be positive!")
                return
                
            if years <= 0:
                messagebox.showerror("Error", "Mortgage length must be positive!")
                return
            
           # Calculate mortgage payments
            monthly_mortgage = self.calculate_mortgage_payment(principal, rate, years)
            annual_mortgage = monthly_mortgage * 12
            
            # Calculate total expenses
            total_taxes = self.tax1.get() + self.tax2.get() + self.tax3.get()
            insurance_annual = self.insurance1.get() + self.insurance2.get()
            water_annual = self.water_bill.get()
            
            total_annual_expenses = annual_mortgage + total_taxes + insurance_annual + water_annual
            total_monthly_expenses = total_annual_expenses / 12
            
            # Calculate total income
            total_monthly_rent = sum(rent.get() for rent in self.rent_entries)
            total_annual_rent = total_monthly_rent * 12
            
            # Calculate profit/loss
            annual_profit_loss = total_annual_rent - total_annual_expenses
            monthly_profit_loss = annual_profit_loss / 12
            
            # Store results for export
            self.last_calculation = {
                'mortgage_rate': rate,
                'mortgage_amount': total_amount,
                'down_payment': down_payment,
                'principal': principal,
                'mortgage_length': years,
                'monthly_mortgage': monthly_mortgage,
                'annual_mortgage': annual_mortgage,
                'tax1': self.tax1.get(),
                'tax2': self.tax2.get(),
                'tax3': self.tax3.get(),
                'total_taxes': total_taxes,
                'insurance': insurance_annual,
                'water_bill': water_annual,
                'total_annual_expenses': total_annual_expenses,
                'total_monthly_expenses': total_monthly_expenses,
                'rent_amounts': [rent.get() for rent in self.rent_entries],
                'total_monthly_rent': total_monthly_rent,
                'total_annual_rent': total_annual_rent,
                'annual_profit_loss': annual_profit_loss,
                'monthly_profit_loss': monthly_profit_loss
            }
            
            # Display results
            self.display_results()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values!")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
    
    def display_results(self):
        if not self.last_calculation:
            return
        
        calc = self.last_calculation
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Format and display results
        result_text = f"""
RENTAL PROPERTY FINANCIAL ANALYSIS
{'='*50}

MORTGAGE DETAILS:
• Mortgage Amount: ${calc['mortgage_amount']:,.2f}
• Down Payment: ${calc['down_payment']:,.2f}
• Principal (Financed): ${calc['principal']:,.2f}
• Interest Rate: {calc['mortgage_rate']:.2f}%
• Loan Term: {calc['mortgage_length']} years

MONTHLY PAYMENTS:
• Mortgage Payment: ${calc['monthly_mortgage']:,.2f}
• Total Monthly Expenses: ${calc['total_monthly_expenses']:,.2f}

ANNUAL COSTS:
• Mortgage Payments: ${calc['annual_mortgage']:,.2f}
• Tax 1: ${calc['tax1']:,.2f}
• Tax 2: ${calc['tax2']:,.2f}
• Tax 3: ${calc['tax3']:,.2f}
• Total Taxes: ${calc['total_taxes']:,.2f}
• Total Insurance: ${calc['insurance']:,.2f}
• Water Bill: ${calc['water_bill']:,.2f}
• TOTAL ANNUAL EXPENSES: ${calc['total_annual_expenses']:,.2f}

RENTAL INCOME:
"""
        
        for i, rent in enumerate(calc['rent_amounts']):
            result_text += f"• Unit {i+1} Monthly Rent: ${rent:,.2f}\n"
        
        result_text += f"""• Total Monthly Rent: ${calc['total_monthly_rent']:,.2f}
• Total Annual Rent: ${calc['total_annual_rent']:,.2f}

PROFIT/LOSS ANALYSIS:
{'='*30}
• Monthly Profit/Loss: ${calc['monthly_profit_loss']:,.2f}
• Annual Profit/Loss: ${calc['annual_profit_loss']:,.2f}

"""
        
        if calc['annual_profit_loss'] > 0:
            result_text += "✅ This property generates a PROFIT!"
        else:
            result_text += "❌ This property generates a LOSS!"
        
        self.results_text.insert(tk.END, result_text)
    
    def export_csv(self):
        if not self.last_calculation:
            messagebox.showwarning("Warning", "Please calculate results first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Results as CSV"
        )
        
        if not filename:
            return
        
        try:
            calc = self.last_calculation
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(['Rental Property Financial Analysis'])
                writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                # Mortgage details
                writer.writerow(['MORTGAGE DETAILS'])
                writer.writerow(['Mortgage Amount', f"${calc['mortgage_amount']:,.2f}"])
                writer.writerow(['Down Payment', f"${calc['down_payment']:,.2f}"])
                writer.writerow(['Principal Financed', f"${calc['principal']:,.2f}"])
                writer.writerow(['Interest Rate', f"{calc['mortgage_rate']:.2f}%"])
                writer.writerow(['Loan Term', f"{calc['mortgage_length']} years"])
                writer.writerow([])
                
                # Monthly payments
                writer.writerow(['MONTHLY PAYMENTS'])
                writer.writerow(['Mortgage Payment', f"${calc['monthly_mortgage']:,.2f}"])
                writer.writerow(['Total Monthly Expenses', f"${calc['total_monthly_expenses']:,.2f}"])
                writer.writerow([])
                
                # Annual expenses
                writer.writerow(['ANNUAL EXPENSES'])
                writer.writerow(['Mortgage Payments', f"${calc['annual_mortgage']:,.2f}"])
                writer.writerow(['Tax 1', f"${calc['tax1']:,.2f}"])
                writer.writerow(['Tax 2', f"${calc['tax2']:,.2f}"])
                writer.writerow(['Tax 3', f"${calc['tax3']:,.2f}"])
                writer.writerow(['Total Taxes', f"${calc['total_taxes']:,.2f}"])
                writer.writerow(['Insurance', f"${calc['insurance']:,.2f}"])
                writer.writerow(['Water Bill', f"${calc['water_bill']:,.2f}"])
                writer.writerow(['TOTAL ANNUAL EXPENSES', f"${calc['total_annual_expenses']:,.2f}"])
                writer.writerow([])
                
                # Rental income
                writer.writerow(['RENTAL INCOME'])
                for i, rent in enumerate(calc['rent_amounts']):
                    writer.writerow([f'Unit {i+1} Monthly Rent', f"${rent:,.2f}"])
                writer.writerow(['Total Monthly Rent', f"${calc['total_monthly_rent']:,.2f}"])
                writer.writerow(['Total Annual Rent', f"${calc['total_annual_rent']:,.2f}"])
                writer.writerow([])
                
                # Profit/Loss
                writer.writerow(['PROFIT/LOSS ANALYSIS'])
                writer.writerow(['Monthly Profit/Loss', f"${calc['monthly_profit_loss']:,.2f}"])
                writer.writerow(['Annual Profit/Loss', f"${calc['annual_profit_loss']:,.2f}"])
                
                status = "PROFIT" if calc['annual_profit_loss'] > 0 else "LOSS"
                writer.writerow(['Status', status])
            
            messagebox.showinfo("Success", f"Results exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def fill_all(self):
        """Fills input fields with common values"""
        self.mortgage_rate.set(7)
        self.mortgage_amount.set(900000)
        self.down_payment.set(180000)
        self.mortgage_length.set(30)
        self.tax1.set(5000)
        self.tax2.set(2000)
        self.tax3.set(4000)
        self.insurance1.set(5000)
        self.insurance2.set(2000)
        self.water_bill.set(1000)
        
        for rent in self.rent_entries:
            rent.set(3500)
        
        self.results_text.delete(1.0, tk.END)
        self.last_calculation = None

    def clear_all(self):
        """Clear all input fields and results"""
        self.mortgage_rate.set(0)
        self.mortgage_amount.set(0)
        self.down_payment.set(0)
        self.mortgage_length.set(0)
        self.tax1.set(0)
        self.tax2.set(0)
        self.tax3.set(0)
        self.insurance1.set(0)
        self.insurance2.set(0)
        self.water_bill.set(0)
        
        for rent in self.rent_entries:
            rent.set(0)
        
        self.results_text.delete(1.0, tk.END)
        self.last_calculation = None

def main():
    root = tk.Tk()
    app = RentalPropertyCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()


