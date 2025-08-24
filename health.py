import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import datetime
import os

class HealthPlanProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Plan Recommendation System")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.selected_age_group = tk.StringVar()
        self.recommendations_text = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Health Plan Recommendation System", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Age selection frame
        age_frame = tk.LabelFrame(main_frame, text="Select Age Group", 
                                 font=('Arial', 12, 'bold'), bg='#f0f0f0')
        age_frame.pack(fill='x', pady=(0, 20))
        
        # Dropdown for age groups
        age_label = tk.Label(age_frame, text="Choose Age Category:", 
                           font=('Arial', 10), bg='#f0f0f0')
        age_label.pack(pady=10)
        
        # Create comprehensive age group options
        age_options = self.create_age_options()
        
        self.age_dropdown = ttk.Combobox(age_frame, textvariable=self.selected_age_group,
                                        values=age_options, state='readonly', width=30)
        self.age_dropdown.pack(pady=10)
        
        # Go button
        go_button = tk.Button(age_frame, text="Get Recommendations", 
                             command=self.get_recommendations,
                             font=('Arial', 10, 'bold'), bg='#3498db', fg='white',
                             padx=20, pady=5)
        go_button.pack(pady=10)
        
        # Recommendations display frame
        rec_frame = tk.LabelFrame(main_frame, text="Medical Recommendations", 
                                 font=('Arial', 12, 'bold'), bg='#f0f0f0')
        rec_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Text area for recommendations
        self.recommendations_display = scrolledtext.ScrolledText(rec_frame, 
                                                               wrap=tk.WORD, 
                                                               width=70, height=15,
                                                               font=('Arial', 10))
        self.recommendations_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Warning label
        warning_text = ("⚠️ IMPORTANT DISCLAIMER: These recommendations are AI-generated and for "
                       "informational purposes only. Always consult with a qualified healthcare "
                       "professional before making any medical decisions or changes to your health regimen.")
        warning_label = tk.Label(main_frame, text=warning_text, 
                               font=('Arial', 9, 'italic'), bg='#fff3cd', fg='#856404',
                               wraplength=750, justify='left', padx=10, pady=10)
        warning_label.pack(fill='x', pady=(0, 20))
        
        # Action buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x')
        
        # Print PDF and Exit button
        pdf_button = tk.Button(button_frame, text="Print PDF and Exit", 
                              command=self.print_pdf_and_exit,
                              font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                              padx=20, pady=5)
        pdf_button.pack(side='right')
        
        # Clear button
        clear_button = tk.Button(button_frame, text="Clear", 
                               command=self.clear_recommendations,
                               font=('Arial', 10), bg='#95a5a6', fg='white',
                               padx=20, pady=5)
        clear_button.pack(side='right', padx=(0, 10))
        
    def create_age_options(self):
        options = []
        
        # Infants (0 to 5 years in 3-month increments)
        options.append("INFANTS:")
        for months in range(0, 61, 3):  # 0 to 60 months (5 years)
            if months + 3 <= 60:
                if months < 12:
                    options.append(f"  {months} to {months + 3} months")
                else:
                    years_start = months // 12
                    months_start = months % 12
                    years_end = (months + 3) // 12
                    months_end = (months + 3) % 12
                    
                    if months_end == 0:
                        options.append(f"  {years_start} year {months_start} months to {years_end} years")
                    else:
                        options.append(f"  {years_start} year {months_start} months to {years_end} year {months_end} months")
        
        # Children (5 to 20 years)
        options.append("CHILDREN:")
        for age in range(5, 21):
            options.append(f"  {age} years old")
        
        # Adults (20 to 100 years in 5-year increments)
        options.append("ADULTS:")
        for age in range(20, 101, 5):
            if age + 5 <= 100:
                options.append(f"  {age} to {age + 4} years")
            else:
                options.append(f"  {age} to 100 years")
        
        return options
    
    def get_recommendations(self):
        selected = self.selected_age_group.get()
        
        if not selected or selected in ["INFANTS:", "CHILDREN:", "ADULTS:"]:
            messagebox.showwarning("Selection Required", 
                                 "Please select a specific age group.")
            return
        
        # Show loading message
        self.recommendations_display.delete(1.0, tk.END)
        self.recommendations_display.insert(tk.END, "Generating recommendations... Please wait.")
        self.root.update()
        
        # Generate recommendations based on age group
        recommendations = self.generate_medical_recommendations(selected)
        
        # Display recommendations
        self.recommendations_display.delete(1.0, tk.END)
        self.recommendations_display.insert(tk.END, recommendations)
        self.recommendations_text = recommendations
    
    def generate_medical_recommendations(self, age_group):
        """Generate medical recommendations based on age group"""
        
        # Clean age group text
        age_text = age_group.strip()
        
        # Comprehensive medical recommendations based on age groups
        if "months" in age_text and any(x in age_text for x in ["0 to 3", "3 to 6", "6 to 9", "9 to 12"]):
            return self.infant_recommendations_0_12_months(age_text)
        elif "year" in age_text and "months" in age_text:
            return self.toddler_recommendations(age_text)
        elif "5 years old" in age_text:
            return self.child_recommendations_5_years()
        elif any(x in age_text for x in [f"{i} years old" for i in range(6, 21)]):
            return self.child_teen_recommendations(age_text)
        elif "20 to 24 years" in age_text:
            return self.young_adult_recommendations()
        elif "25 to 29 years" in age_text or "30 to 34 years" in age_text:
            return self.adult_recommendations_25_35()
        elif any(x in age_text for x in ["35 to 39", "40 to 44", "45 to 49"]):
            return self.middle_age_recommendations_35_50()
        elif "50 to 54 years" in age_text or "55 to 59 years" in age_text:
            return self.mature_adult_recommendations_50_60()
        elif any(x in age_text for x in ["60 to 64", "65 to 69", "70 to 74"]):
            return self.senior_recommendations_60_75()
        else:
            return self.elderly_recommendations_75_plus()
    
    def infant_recommendations_0_12_months(self, age_text):
        return f"""
MEDICAL RECOMMENDATIONS FOR {age_text.upper()}

🍼 NUTRITION & FEEDING:
• Exclusive breastfeeding recommended for first 6 months
• If formula feeding, use iron-fortified infant formula
• Introduction of solid foods around 6 months
• Avoid honey, cow's milk, and choking hazards

💉 IMMUNIZATIONS (CDC Schedule):
• Birth: Hepatitis B
• 2 months: DTaP, IPV, Hib, PCV13, RV
• 4 months: DTaP, IPV, Hib, PCV13, RV
• 6 months: DTaP, IPV, Hib, PCV13, RV, Influenza (annual)

🏥 REGULAR CHECK-UPS:
• Well-baby visits at 3-5 days, 1 month, 2 months, 4 months, 6 months
• Growth and development monitoring (height, weight, head circumference)
• Developmental milestone assessments

👁️ SCREENINGS:
• Vision and hearing screenings
• Lead screening (high-risk areas)
• Tuberculosis screening (if indicated)

🛡️ SAFETY:
• Safe sleep practices (back sleeping, firm mattress)
• Car seat safety
• Childproofing home environment
• Water safety precautions

⚕️ PREVENTIVE CARE:
• Fluoride supplementation (if water not fluoridated)
• Vitamin D supplementation for breastfed infants
• Iron supplementation as recommended by pediatrician
"""

    def toddler_recommendations(self, age_text):
        return f"""
MEDICAL RECOMMENDATIONS FOR {age_text.upper()}

🍎 NUTRITION:
• Transition to whole milk after 12 months
• Balanced diet with fruits, vegetables, whole grains, lean proteins
• Limit juice intake, avoid sugary drinks
• Begin using cups instead of bottles

💉 IMMUNIZATIONS:
• 12-15 months: MMR, PCV13, Hib, Varicella
• 15-18 months: DTaP
• Annual influenza vaccine
• Hepatitis A series (12-23 months)

🏥 REGULAR CHECK-UPS:
• Well-child visits at 12, 15, 18, 24 months, then annually
• Growth monitoring and developmental assessments
• Behavioral and social development evaluation

👁️ SCREENINGS:
• Lead screening at 12 and 24 months
• Vision and hearing assessments
• Autism screening at 18 and 24 months
• Dental examination by first birthday or first tooth

🦷 DENTAL CARE:
• Begin tooth brushing with fluoride toothpaste
• First dental visit by age 1 or within 6 months of first tooth
• Avoid prolonged bottle use, especially at bedtime

🛡️ SAFETY:
• Childproofing updates as mobility increases
• Poison control measures
• Water and playground safety
• Proper car seat installation and use
"""

    def child_recommendations_5_years(self):
        return f"""
MEDICAL RECOMMENDATIONS FOR 5 YEARS OLD

🍎 NUTRITION & LIFESTYLE:
• Balanced diet with 5 servings of fruits/vegetables daily
• Limit screen time to 1 hour on weekdays, 2 hours on weekends
• Encourage physical activity (at least 1 hour daily)
• Establish regular sleep schedule (10-11 hours per night)

💉 IMMUNIZATIONS:
• DTaP booster (4-6 years)
• IPV booster (4-6 years)
• MMR booster (4-6 years)
• Varicella booster (4-6 years)
• Annual influenza vaccine

🏥 REGULAR CHECK-UPS:
• Annual well-child visits
• Growth and development monitoring
• School readiness assessment
• Behavioral health screening

👁️ SCREENINGS:
• Vision screening (annually or before school)
• Hearing screening
• Blood pressure measurement
• BMI calculation and obesity screening
• Cholesterol screening (if family history or risk factors)

🦷 DENTAL CARE:
• Dental check-ups every 6 months
• Fluoride treatments
• Proper brushing and beginning to floss
• Sealants for permanent molars when they emerge

🧠 DEVELOPMENT:
• Social skills development
• Pre-academic skills assessment
• Speech and language evaluation if concerns
• Emotional regulation skills
"""

    def child_teen_recommendations(self, age_text):
        age_num = int(age_text.split()[0])
        
        base_recommendations = f"""
MEDICAL RECOMMENDATIONS FOR {age_text.upper()}

🍎 NUTRITION & LIFESTYLE:
• Balanced nutrition with emphasis on calcium and vitamin D
• Limit processed foods and sugary drinks
• Encourage daily physical activity
• Appropriate screen time limits
"""
        
        if age_num <= 10:
            base_recommendations += """
• Sleep: 9-11 hours per night
• Continue building healthy eating habits

💉 IMMUNIZATIONS:
• Annual influenza vaccine
• Catch-up vaccines as needed
• Tdap booster at age 11-12

🏥 REGULAR CHECK-UPS:
• Annual well-child visits
• Growth monitoring
• Academic performance assessment
• Social development evaluation

👁️ SCREENINGS:
• Annual vision and hearing screening
• Blood pressure monitoring
• BMI and obesity screening
• Depression screening (starting age 12)
• Scoliosis screening

🦷 DENTAL CARE:
• Dental visits every 6 months
• Sealants for permanent molars
• Orthodontic evaluation around age 7
"""
        else:  # Teens 11-20
            base_recommendations += f"""
• Sleep: 8-10 hours per night (teens)
• Discuss nutrition for growth spurts

💉 IMMUNIZATIONS:
• Tdap booster (11-12 years)
• HPV vaccine series (11-12 years, up to age 26)
• Meningococcal vaccine (11-12 years, booster at 16)
• Annual influenza vaccine
• COVID-19 vaccines as recommended

🏥 REGULAR CHECK-UPS:
• Annual well-visits with increasing privacy
• Confidential discussions about health behaviors
• Mental health screening
• Substance use screening

👁️ SCREENINGS:
• Annual vision and hearing screening
• Blood pressure monitoring
• BMI screening and eating disorder assessment
• Depression and anxiety screening
• STI screening (if sexually active)
• Cholesterol screening (if risk factors)

🧠 ADOLESCENT HEALTH:
• Discuss puberty and body changes
• Sexual health education
• Mental health awareness
• Substance abuse prevention
• Driving safety education
"""
        
        return base_recommendations

    def young_adult_recommendations(self):
        return """
MEDICAL RECOMMENDATIONS FOR 20-24 YEARS

🏥 PREVENTIVE CARE:
• Annual physical examination
• Establish relationship with primary care provider
• Transition from pediatric to adult healthcare

💉 IMMUNIZATIONS:
• Annual influenza vaccine
• Tdap booster every 10 years
• HPV vaccine (if not completed, up to age 26)
• Meningococcal vaccine (if in high-risk groups)
• COVID-19 vaccines as recommended

👁️ SCREENINGS:
• Blood pressure monitoring
• Cholesterol screening (every 4-6 years, or more frequently if risk factors)
• Depression and anxiety screening
• Substance use screening
• STI screening (if sexually active)
• Cervical cancer screening (starting at age 21)

🦷 DENTAL CARE:
• Dental check-ups every 6 months
• Professional cleanings
• Wisdom teeth evaluation

💪 LIFESTYLE:
• Regular exercise (150 minutes moderate activity per week)
• Maintain healthy weight
• Limit alcohol consumption
• Avoid tobacco and recreational drugs
• Practice safe sex
• Adequate sleep (7-9 hours per night)

🧠 MENTAL HEALTH:
• Stress management techniques
• Work-life balance
• Social support systems
• Professional counseling if needed
"""

    def adult_recommendations_25_35(self):
        return """
MEDICAL RECOMMENDATIONS FOR 25-35 YEARS

🏥 REGULAR CHECK-UPS:
• Annual physical examination with primary care provider
• Discuss family planning goals
• Preconception counseling (if planning pregnancy)

💉 IMMUNIZATIONS:
• Annual influenza vaccine
• Tdap booster every 10 years
• HPV vaccine (up to age 26 if not previously vaccinated)
• COVID-19 vaccines as recommended
• Travel vaccines as needed

👁️ SCREENINGS:
• Blood pressure: annually
• Cholesterol: every 4-6 years (more frequent if risk factors)
• Diabetes screening: every 3 years starting at age 35 (or earlier if risk factors)
• Cervical cancer screening: every 3 years (ages 21-29) or every 5 years with HPV co-testing (ages 30-65)
• Breast cancer: clinical breast exam annually, discuss family history
• Skin cancer: annual skin examination (more frequent if risk factors)
• Depression screening

🦷 DENTAL CARE:
• Dental check-ups and cleanings every 6 months
• Periodontal disease prevention
• Regular oral cancer screening

💪 LIFESTYLE OPTIMIZATION:
• Regular cardiovascular exercise
• Strength training 2-3 times per week
• Maintain healthy BMI (18.5-24.9)
• Mediterranean-style diet emphasis
• Limit alcohol (1 drink/day women, 2 drinks/day men)
• No tobacco use
• Stress management and adequate sleep

👶 REPRODUCTIVE HEALTH:
• Family planning discussions
• Folic acid supplementation (if planning pregnancy)
• Fertility awareness
• Contraception counseling
"""

    def middle_age_recommendations_35_50(self):
        return """
MEDICAL RECOMMENDATIONS FOR 35-50 YEARS

🏥 COMPREHENSIVE HEALTH ASSESSMENT:
• Annual physical examination
• Cardiovascular risk assessment
• Cancer risk evaluation
• Family history review and genetic counseling if indicated

💉 IMMUNIZATIONS:
• Annual influenza vaccine
• Tdap booster every 10 years
• Shingles vaccine (Shingrix) starting at age 50
• COVID-19 vaccines as recommended

👁️ ENHANCED SCREENINGS:
• Blood pressure: annually (more frequent if elevated)
• Cholesterol: every 4-6 years (annually if risk factors)
• Diabetes screening: every 3 years (annually if prediabetic)
• Cervical cancer: every 3-5 years (depending on method)
• Breast cancer: annual mammography starting at age 40-50 (discuss with provider)
• Colorectal cancer: screening starting at age 45-50
• Lung cancer: low-dose CT if 20+ pack-year smoking history
• Osteoporosis: DEXA scan for postmenopausal women
• Prostate cancer: discuss PSA screening with men starting at age 50

👁️ VISION & HEARING:
• Comprehensive eye exam every 2 years
• Hearing assessment if concerns
• Glaucoma screening

🦷 DENTAL CARE:
• Dental check-ups every 6 months
• Periodontal disease monitoring
• Oral cancer screening

💪 METABOLIC HEALTH:
• Weight management strategies
• Regular exercise (150 min moderate + 2 days strength training)
• Heart-healthy diet
• Blood glucose monitoring
• Thyroid function testing (especially women)

🧠 MENTAL HEALTH:
• Stress management
• Work-life balance assessment
• Depression and anxiety screening
• Cognitive health awareness
"""

    def mature_adult_recommendations_50_60(self):
        return """
MEDICAL RECOMMENDATIONS FOR 50-60 YEARS

🏥 COMPREHENSIVE PREVENTIVE CARE:
• Annual physical with comprehensive metabolic panel
• Cardiovascular risk stratification
• Cancer risk assessment and family history review
• Medication review and optimization

💉 IMMUNIZATIONS:
• Annual influenza vaccine
• Shingles vaccine (Shingrix) - 2 doses
• Tdap booster every 10 years
• Pneumococcal vaccine (discuss timing with provider)
• COVID-19 vaccines as recommended

👁️ CRITICAL SCREENINGS:
• Blood pressure: every visit (target <130/80 for most)
• Cholesterol: annually (consider statin therapy based on risk)
• Diabetes: annual HbA1c and glucose
• Colorectal cancer: colonoscopy every 10 years or alternative methods
• Breast cancer: annual mammography
• Cervical cancer: continue per guidelines until age 65
• Prostate cancer: annual PSA discussion for men
• Lung cancer: annual low-dose CT if smoking history criteria met
• Osteoporosis: DEXA scan every 2 years for women, men with risk factors

👁️ SENSORY HEALTH:
• Annual comprehensive eye exam (glaucoma, macular degeneration)
• Hearing assessment every 3 years
• Diabetic retinopathy screening if diabetic

🦷 ORAL HEALTH:
• Dental visits every 6 months
• Periodontal disease management
• Oral cancer screening
• Dry mouth assessment (medication side effects)

💪 METABOLIC & CARDIOVASCULAR:
• Exercise stress test if indicated
• Echocardiogram if symptoms or risk factors
• Carotid artery screening if risk factors
• Ankle-brachial index if peripheral artery disease suspected
• Thyroid function testing every 5 years

🧠 COGNITIVE & MENTAL HEALTH:
• Baseline cognitive assessment
• Depression screening
• Sleep disorder evaluation
• Stress management and lifestyle counseling

⚕️ HORMONE HEALTH:
• Menopause management for women
• Testosterone screening for men with symptoms
• Bone health optimization
"""

    def senior_recommendations_60_75(self):
        return """
MEDICAL RECOMMENDATIONS FOR 60-75 YEARS

🏥 GERIATRIC PREVENTIVE CARE:
• Comprehensive annual physical examination
• Medication reconciliation and deprescribing review
• Fall risk assessment
• Functional status evaluation
• Advanced directive discussions

💉 IMMUNIZATIONS:
• Annual high-dose influenza vaccine
• Shingles vaccine (Shingrix) if not previously received
• Pneumococcal vaccines (PCV13 and PPSV23)
• Tdap booster every 10 years
• COVID-19 vaccines as recommended
• RSV vaccine (new recommendation for 60+)

👁️ ESSENTIAL SCREENINGS:
• Blood pressure: every visit
• Diabetes: annual HbA1c and comprehensive metabolic panel
• Cholesterol: annually with statin consideration
• Colorectal cancer: continue until age 75 (individualized after 75)
• Breast cancer: annual mammography until age 75
• Cervical cancer: may discontinue after age 65 if adequate screening
• Prostate cancer: individualized screening discussion
• Osteoporosis: DEXA scan every 2 years
• Abdominal aortic aneurysm: one-time screening for men 65-75 who smoked

👁️ SENSORY & NEUROLOGICAL:
• Annual comprehensive eye exam (cataracts, glaucoma, AMD)
• Annual hearing assessment
• Cognitive screening (Mini-Mental State Exam or Montreal Cognitive Assessment)
• Depression screening (PHQ-9)

🦷 ORAL HEALTH:
• Dental visits every 6 months
• Denture fit and oral health assessment
• Xerostomia (dry mouth) management

💪 MOBILITY & FUNCTION:
• Balance and gait assessment
• Muscle strength evaluation
• Joint health and arthritis management
• Physical therapy evaluation if needed
• Home safety assessment

🧠 COGNITIVE & BEHAVIORAL:
• Memory assessment
• Driving safety evaluation
• Social isolation screening
• Advance care planning
• Medication adherence review

⚕️ CHRONIC DISEASE MANAGEMENT:
• Blood pressure optimization
• Diabetes management with relaxed targets
• Heart disease monitoring
• COPD assessment if smoking history
• Kidney function monitoring
• Polypharmacy management
"""

    def elderly_recommendations_75_plus(self):
        return """
MEDICAL RECOMMENDATIONS FOR 75+ YEARS

🏥 COMPREHENSIVE GERIATRIC ASSESSMENT:
• Comprehensive annual examination with geriatric focus
• Functional independence assessment (ADLs/IADLs)
• Cognitive evaluation and dementia screening
• Caregiver support assessment
• Quality of life and comfort care discussions

💉 IMMUNIZATIONS:
• Annual high-dose influenza vaccine
• Pneumococcal vaccines (PCV20 or PCV15 + PPSV23)
• Shingles vaccine if not contraindicated
• COVID-19 vaccines as recommended
• RSV vaccine
• Tdap as appropriate

👁️ INDIVIDUALIZED SCREENINGS:
• Blood pressure monitoring with individualized targets
• Diabetes management with relaxed HbA1c goals (7.5-8.5%)
• Cancer screening: individualized based on life expectancy and quality of life
• Osteoporosis: continued monitoring with fall prevention focus
• Depression screening and treatment

👁️ SENSORY IMPAIRMENT MANAGEMENT:
• Annual vision assessment (cataracts, glaucoma, AMD)
• Hearing aid evaluation and optimization
• Visual and hearing aid maintenance

🦷 ORAL HEALTH:
• Regular dental care adapted to functional status
• Oral hygiene assistance if needed
• Swallowing assessment if concerns

💪 FUNCTIONAL HEALTH:
• Fall prevention programs
• Physical therapy and occupational therapy
• Mobility aid assessment (walkers, wheelchairs)
• Home modification recommendations
• Balance and strength training

🧠 COGNITIVE & BEHAVIORAL:
• Dementia screening and management
• Behavioral symptom management
• Medication review for cognitive effects
• Sleep disorder assessment
• Social engagement promotion

⚕️ CHRONIC CONDITION MANAGEMENT:
• Heart failure management
• COPD optimization
• Arthritis and pain management
• Medication simplification
• Palliative care discussions when appropriate

🏠 CARE COORDINATION:
• Home health services coordination
• Long-term care planning
• Family caregiver support
• End-of-life care preferences
• Advance directive completion and review

⚠️ SAFETY PRIORITIES:
• Medication safety and interaction review
• Fall risk reduction
• Elder abuse screening
• Emergency preparedness planning
"""

    def clear_recommendations(self):
        self.recommendations_display.delete(1.0, tk.END)
        self.recommendations_text = ""
        self.selected_age_group.set("")

    def print_pdf_and_exit(self):
        if not self.recommendations_text:
            messagebox.showwarning("No Content", 
                                 "Please generate recommendations first.")
            return
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Health Recommendations PDF"
        )
        
        if not filename:
            return
        
        try:
            self.create_pdf(filename)
            
            # Show success message with file location
            messagebox.showinfo("PDF Created Successfully", 
                              f"Health recommendations saved to:\n{filename}")
            
            # Exit the application
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error Creating PDF", 
                               f"An error occurred while creating the PDF:\n{str(e)}")

    def create_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor='darkblue',
            alignment=1  # Center alignment
        )
        
        warning_style = ParagraphStyle(
            'Warning',
            parent=styles['Normal'],
            fontSize=10,
            textColor='red',
            backColor='lightyellow',
            borderColor='red',
            borderWidth=1,
            borderPadding=10,
            spaceAfter=20
        )
        
        # Add title
        story.append(Paragraph("Health Plan Recommendations", title_style))
        story.append(Spacer(1, 20))
        
        # Add selected age group
        age_group = self.selected_age_group.get()
        story.append(Paragraph(f"<b>Age Group:</b> {age_group}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add warning
        warning_text = ("⚠️ IMPORTANT MEDICAL DISCLAIMER: These recommendations are AI-generated "
                       "and provided for informational purposes only. They do not constitute "
                       "professional medical advice, diagnosis, or treatment. Always consult "
                       "with a qualified healthcare professional before making any medical "
                       "decisions or changes to your health regimen. Your doctor can provide "
                       "personalized recommendations based on your individual health history, "
                       "current condition, and specific needs.")
        story.append(Paragraph(warning_text, warning_style))
        
        # Add recommendations
        # Split the text into paragraphs and format appropriately
        lines = self.recommendations_text.strip().split('\n')
        for line in lines:
            if line.strip():
                if line.strip().startswith('MEDICAL RECOMMENDATIONS'):
                    # Main heading
                    story.append(Paragraph(line.strip(), styles['Heading2']))
                elif line.strip().startswith(('🍼', '💉', '🏥', '👁️', '🛡️', '⚕️', '🍎', '🦷', '🧠', '💪')):
                    # Section headers with emojis
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(f"<b>{line.strip()}</b>", styles['Heading3']))
                elif line.strip().startswith('•'):
                    # Bullet points
                    story.append(Paragraph(line.strip(), styles['Normal']))
                else:
                    # Regular text
                    if line.strip():
                        story.append(Paragraph(line.strip(), styles['Normal']))
            else:
                story.append(Spacer(1, 6))
        
        # Add footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)

def main():
    root = tk.Tk()
    app = HealthPlanProgram(root)
    root.mainloop()

if __name__ == "__main__":
    main()


