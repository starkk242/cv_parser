import re
import spacy
from typing import Dict
from datetime import datetime
from huggingface_hub import InferenceClient
from openai import OpenAI
import json

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not available, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def extract_information(text: str, settings) -> Dict:
    """Extract relevant information from resume text using AI and fallback to spaCy."""

    try:
        # Try AI-based extraction first

        # Initialize Hugging Face client
        # client = InferenceClient(
        #     provider="cerebras",
        #     api_key=settings.HUGGING_FACE_TOKEN
        # )

        client = OpenAI(
            api_key=settings.OPEN_AI,
            base_url="https://inference.baseten.co/v1"
        )

        prompt = f"""
        Extract information from this resume text and respond in the following JSON format:
        {{
            "name": "full name",
            "email": "email address",
            "phone": "phone number",
            "education": ["list of education details"],
            "skills": ["list of skills"],
            "experience": [
                {{"description": "experience description"}}
            ]
        }}

        Resume text:
        {text}

        Return only the JSON structure, no other text.
        """

        # completion = client.chat.completions.create(
        #     model="Qwen/Qwen3-32B",
        #     messages=[{"role": "user", "content": prompt}]
        # )

        # # Parse AI response
        # json_str = completion.choices[0].message.content


        response = client.chat.completions.create(
            model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        
        # Parse the response content
        content = response.choices[0].message.content
        json_str = content.strip('`json\n').strip()

        while '<think>' in json_str and '</think>' in json_str:
            start = json_str.find('<think>')
            end = json_str.find('</think>') + len('</think>')
            json_str = json_str[:start] + json_str[end:]
        
        result = json.loads(json_str)
        result["parsed_date"] = datetime.now().isoformat()
        return result

    except Exception as e:
        # Fallback to spaCy-based extraction
        print(e)
        doc = nlp(text)
        
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+`\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, text)
        
        phone_pattern = r"(?:\+91[\s-]?(?:\d{5}\s\d{5}|\d{10}|\d{4}-\d{6}))|(?:\+\d{1,3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4})|(?:\b\d{3}[-\.]?\d{3}[-\.]?\d{4}\b)|(?:\b\d{10}\b)"
        phones = re.findall(phone_pattern, text)
        
        name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
        
        education = []
        edu_keywords = {"degree", "bachelor", "master", "phd", "diploma", "university", "college", "school", "certification"}
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in edu_keywords):
                education.append(sent.text.strip())
        
        skills = []
        for token in doc:
            if token.pos_ in {"PROPN", "NOUN"} and len(token.text) > 2 and token.text.lower() not in {"the", "and", "for", "with"}:
                skills.append(token.text)
        
        experience = []
        exp_keywords = {"experience", "work", "employment", "job", "position", "role", "career", "professional"}
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in exp_keywords):
                experience.append({"description": sent.text.strip()})
        
        return {
            "name": name,
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "education": list(set(education)),
            "skills": list(set(skills)),
            "experience": experience[:5],
            "parsed_date": datetime.now().isoformat()
        }