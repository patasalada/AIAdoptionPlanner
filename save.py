from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Onboarding Route
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == 'POST':
        session['company_name'] = request.form.get('company_name')
        session['industry'] = request.form.get('industry')
        session['size'] = request.form.get('size')
        session['technology_stack'] = request.form.get('technology_stack')
        session['business_goals_1_3_years'] = request.form.get('business_goals_1_3_years')
        session['bottlenecks'] = request.form.get('bottlenecks')
        session['ai_achievements'] = request.form.get('ai_achievements')
        return redirect(url_for('readiness_assessment'))
    return render_template('onboarding.html')

# Readiness Assessment Route
@app.route('/readiness_assessment', methods=['GET', 'POST'])
def readiness_assessment():
    if request.method == 'POST':
        session['data_challenges'] = request.form.get('data_challenges')
        session['ai_tools'] = request.form.get('ai_tools')
        session['tech_gaps'] = request.form.get('tech_gaps')
        session['ai_skills'] = request.form.get('ai_skills')
        session['training_plan'] = request.form.get('training_plan')
        session['leadership_support'] = request.form.get('leadership_support')
        session['change_management'] = request.form.get('change_management')
        session['ai_budget'] = request.form.get('ai_budget')
        session['resource_constraints'] = request.form.get('resource_constraints')
        session['readiness_score'] = request.form.get('readiness_score')
        return redirect(url_for('use_case_discovery'))
    return render_template('readiness_assessment.html')

# Use Case Discovery Route
@app.route('/use_case_discovery', methods=['GET', 'POST'])
def use_case_discovery():
    if request.method == 'POST':
        session['use_cases'] = request.form.getlist('use_case')
        session['priority'] = request.form.get('priority')
        session['custom_use_case'] = request.form.get('custom_use_case', '')
        return redirect(url_for('roadmap'))
    return render_template('use_case_discovery.html')

# Roadmap Route - Display Captured Data and Provide PDF Download Option
@app.route('/roadmap')
def roadmap():
    captured_data = {key: session.get(key) for key in session.keys()}  # Get all session data
    return render_template('roadmap.html', captured_data=captured_data)

# Download PDF Route - Generates a PDF from User Input Data
@app.route('/download_pdf')
def download_pdf():
    pdf_file = generate_pdf_from_user_data()  # Generate PDF with all session data
    return send_file(pdf_file, as_attachment=True, download_name="User_Data_Captured.pdf", mimetype="application/pdf")


def generate_pdf_from_user_data():
    pdf_stream = io.BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    margin = 30
    line_height = 15
    section_spacing = 25  # Additional spacing between sections
    page_width = letter[0] - (2 * margin)

    # Helper function to wrap text and handle page breaks
    def write_wrapped_text(c, text, x, y, max_width, line_height):
        words = text.split()
        line = ""
        for word in words:
            if c.stringWidth(line + word) < max_width:
                line += word + " "
            else:
                c.drawString(x, y, line)
                y -= line_height
                line = word + " "
                if y < margin + line_height * 2:  # Start new page if space is low
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 750
        c.drawString(x, y, line.strip())
        return y - line_height

    # Ensure instructions start on a fresh page if they run long
    def add_instructions(text):
        nonlocal y
        y = write_wrapped_text(c, text, margin, y, page_width, line_height)
        y -= line_height * 2
        if y < margin + line_height * 3:
            c.showPage()
            y = 750

    instructions = """
    AI Adoption Readiness Report

    This document contains all the information gathered during the onboarding and readiness assessment stages. 
    The goal is to provide ChatGPT with a comprehensive overview of the company, its goals, challenges, 
    current technology stack, and specific AI use cases. ChatGPT will use this information to generate a 
    detailed AI adoption roadmap tailored to the company's needs. Be as thorough as possible and help the company 
    view AI optimistically and get buy-in from the entire company.
    """
    add_instructions(instructions)

    # Function to add section with larger title and spaced entries
    def add_section(title, data):
        nonlocal y
        if y < margin + line_height * 4:  # Check if there's enough space for the title
            c.showPage()
            y = 750
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, title)
        y -= line_height * 2 + section_spacing  # Apply section spacing here
        c.setFont("Helvetica", 12)

        # Wrap text for each key-value pair with extra space after each
        for key, value in data.items():
            content = f"{key}: {value}"
            y = write_wrapped_text(c, content, margin, y, page_width, line_height)
            y -= line_height * 1.5  # Extra space between entries

    # Organized Data Sections
    company_overview = {
        "Company Name": session.get("company_name", "Example Corp"),
        "Industry": session.get("industry", "Finance"),
        "Company Size": session.get("size", "500"),
        "Technology Stack": session.get("technology_stack", "AWS, Salesforce")
    }
    business_goals = {
        "Business Goals (Next 1-3 Years)": session.get("business_goals_1_3_years", "Expand globally, Increase revenue"),
        "Biggest Bottlenecks or Inefficiencies": session.get("bottlenecks", "Lack of data integration"),
        "What the Company Hopes to Achieve with AI": session.get("ai_achievements",
                                                                 "Automation, Improved decision-making")
    }
    readiness_assessment = {
        "Data Challenges": session.get("data_challenges", "Data silos"),
        "AI Tools": session.get("ai_tools", "None"),
        "Technology Gaps": session.get("tech_gaps", "Lack of cloud infrastructure"),
        "AI Skills Level": session.get("ai_skills", "Beginner"),
        "Training Plan": session.get("training_plan", "Planned for next year"),
        "Leadership Support": session.get("leadership_support", "High"),
        "Change Management Experience": session.get("change_management", "Good"),
        "AI Budget": session.get("ai_budget", "$50,000"),
        "Resource Constraints": session.get("resource_constraints", "Limited IT staff"),
        "Readiness Score": session.get("readiness_score", "70")
    }
    use_case_discovery = {
        "Selected Use Cases": ", ".join(session.get("use_cases", ["Predictive Maintenance", "Quality Control"])),
        "Top Priority Use Case": session.get("priority", "Predictive Maintenance"),
        "Custom Use Case": session.get("custom_use_case", "Energy Optimization")
    }

    # Add each section to the PDF
    add_section("Company Overview", company_overview)
    add_section("Business Goals and Challenges", business_goals)
    add_section("AI Readiness Assessment", readiness_assessment)
    add_section("AI Use Case Discovery", use_case_discovery)

    c.save()
    pdf_stream.seek(0)
    return pdf_stream

if __name__ == '__main__':
    app.run(debug=True)
