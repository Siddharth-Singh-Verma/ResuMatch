from django.shortcuts import render
from .forms import ResumeMatchForm
import fitz  # PyMuPDF
import requests
import json
from django.conf import settings
import re

def home(request):
    return render(request, 'matcher/home.html')

def about(request):
    return render(request, 'matcher/about.html')


def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def parse_gemini_response(response_text):
    match = re.search(r"Match Percentage:\s*(\d+)%", response_text)
    tips = re.findall(r"Tips for Improvement:\n((?:- .+\n)+)", response_text)
    mistakes = re.findall(r"Grammatical Mistakes:\n((?:- .+\n)+)", response_text)

    return {
        "match_percentage": match.group(1) if match else "N/A",
        "tips": tips[0].strip().split("\n") if tips else [],
        "mistakes": mistakes[0].strip().split("\n") if mistakes else [],
    }

def genai(request):
    parsed_result = None
    result = None

    if request.method == "POST":
        form = ResumeMatchForm(request.POST, request.FILES)
        if form.is_valid():
            resume_text = form.cleaned_data.get("resume_text", "")
            resume_pdf = form.cleaned_data.get("resume_pdf")
            # Prefer resume_text if provided, otherwise extract from PDF
            if resume_text and resume_text.strip():
                final_resume_text = resume_text
            elif resume_pdf:
                final_resume_text = extract_text_from_pdf(resume_pdf)
            else:
                final_resume_text = ""

            job_description = form.cleaned_data.get("job_description", "")

            if final_resume_text.strip() and job_description.strip():
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
                headers = {
                    "Content-Type": "application/json"
                }

                prompt = f"""
Compare the resume with the job description and provide the following response strictly in this format:

Match Percentage: <number>%

Tips for Improvement:
- tip 1
- tip 2

Grammatical Mistakes:
- mistake 1
- mistake 2

Resume:
{final_resume_text}

Job Description:
{job_description}
"""

                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }

                try:
                    response = requests.post(url, headers=headers, data=json.dumps(payload))
                    response.raise_for_status()
                    result_json = response.json()
                    raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                    parsed_result = parse_gemini_response(raw_text)
                    if parsed_result:
                        match_percentage = float(parsed_result['match_percentage'])
                        circle_length = 339.292
                        match_circle_offset = circle_length - (match_percentage * circle_length / 100)
                        context['match_circle_offset'] = match_circle_offset
                except Exception as e:
                    result = f"Error from Gemini API: {str(e)}"
            else:
                result = "Please provide resume text or upload a resume."
    else:
        form = ResumeMatchForm()

    return render(request, "matcher/genai.html", {"form": form, "parsed_result": parsed_result, "result": result})
