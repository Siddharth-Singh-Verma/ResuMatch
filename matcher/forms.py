from django import forms

class ResumeMatchForm(forms.Form):
    resume_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}), label="Resume Text", required=False)
    job_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}), label="Job Description", required=True)
    resume_pdf = forms.FileField(required=False, label="Resume PDF")

    def clean(self):
        cleaned_data = super().clean()
        resume_text = cleaned_data.get('resume_text', '').strip()
        resume_pdf = cleaned_data.get('resume_pdf')
        job_description = cleaned_data.get('job_description', '').strip()

        if not job_description:
            raise forms.ValidationError("Job description is required.")
        if not resume_text and not resume_pdf:
            raise forms.ValidationError("Please provide either resume text or upload a resume PDF.")
        return cleaned_data
