from flask import Flask, request, render_template
import os
import fitz
from openai import OpenAI
import json

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_info(text):
    prompt = f"""
    Extract the following from this resume text:
    - First Name
    - Last Name
    - Current Role
    - Skillset (as a list)
    
    Resume Text:
    {text}

    Return the output in JSON format.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    file = request.files['resume']
    text = extract_text_from_pdf(file)
    data = extract_info(text)

    return render_template('result.html',
        first_name=data["First Name"],
        last_name=data["Last Name"],
        current_role=data["Current Role"],
        skills=data["Skillset"]
    )

if __name__ == '__main__':
    app.run(debug=True)
    