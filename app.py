from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

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

# Roadmap Route
@app.route('/roadmap', methods=['GET', 'POST'])
def roadmap():
    if request.method == 'GET':
        # Automatically generate the PDF when the user reaches this page
        user_name = session.get('company_name', 'Your Company')
        generate_pdf_from_user_data(user_name)

    if request.method == 'POST':
        session['user_name'] = request.form.get('name')
        session['user_email'] = request.form.get('email')
        return redirect(url_for('thank_you'))

    captured_data = {key: session.get(key) for key in session.keys()}
    return render_template('roadmap.html', captured_data=captured_data)

# New Route to Generate PDF After Form Submission
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    session['user_name'] = request.form.get('name')
    session['user_email'] = request.form.get('email')

    # Generate the PDF after capturing the name and email
    user_name = session.get('company_name', 'Your Company')
    pdf_path = generate_pdf_from_user_data(user_name)

    # Redirect to the thank you page
    return redirect(url_for('roadmap'))

# Thank You Page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


# PDF Generation Function
def generate_pdf_from_user_data(user_name):
    pdf_stream = io.BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    margin = 30
    line_height = 15

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
                if y < margin + line_height * 2:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 750
        c.drawString(x, y, line.strip())
        return y - line_height

    # Instructions Section
    instructions =  """
    AI Adoption Readiness Report

    This document contains all the information gathered during the onboarding and readiness assessment stages. 
    The goal is to provide ChatGPT with a comprehensive overview of the company, its goals, challenges, 
    current technology stack, and specific AI use cases. ChatGPT will use this information to generate a 
    detailed AI adoption roadmap tailored to the company's needs. Be as thorough as possible and help the company 
    view AI optimistically and get buy-in from the entire company.
    """
    y = write_wrapped_text(c, instructions, margin, y, letter[0] - 2 * margin, line_height)

    # Sections
    sections = {
        "Company Overview": {
            "User Name": session.get("user_name", "N/A"),
            "User Email": session.get("user_email", "N/A"),
            "Company Name": session.get("company_name", "Example Corp"),
            "Industry": session.get("industry", "Finance"),
            "Company Size": session.get("size", "500"),
            "Technology Stack": session.get("technology_stack", "AWS, Salesforce")
        },
        "Business Goals and Challenges": {
            "Business Goals (Next 1-3 Years)": session.get("business_goals_1_3_years", "Expand globally"),
            "Biggest Bottlenecks": session.get("bottlenecks", "Lack of data integration"),
            "AI Achievements": session.get("ai_achievements", "Automation")
        },
        "AI Readiness Assessment": {
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
        },
        "AI Use Case Discovery": {
            "Selected Use Cases": ", ".join(session.get("use_cases", ["Predictive Maintenance"])),
            "Top Priority Use Case": session.get("priority", "Predictive Maintenance"),
            "Custom Use Case": session.get("custom_use_case", "Energy Optimization")
        }
    }

    # Add Sections
    for title, content in sections.items():
        y -= line_height * 2
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, title)
        y -= line_height * 2
        c.setFont("Helvetica", 12)
        for key, value in content.items():
            y = write_wrapped_text(c, f"{key}: {value}", margin, y, letter[0] - 2 * margin, line_height)

    c.save()
    pdf_stream.seek(0)

    # Create local directory if it doesn't exist
    local_dir = "generated_pdfs"
    os.makedirs(local_dir, exist_ok=True)

    # Save PDF file locally
    file_path = os.path.join(local_dir, f"{user_name}_AI_Adoption_Roadmap.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_stream.getbuffer())

    return file_path

if __name__ == '__main__':
    app.run(debug=True)
