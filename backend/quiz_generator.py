import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables from .env
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def generate_quiz_from_text(text):
    prompt = f"""
You are a quiz generator AI.

Instructions:
1. Read the following input text and determine the topic. The text may contain informal or broken English.
2. Check if the user has specified the number of questions (e.g., "generate 10 questions", "give me 7 MCQs", etc.).
   - If a number is mentioned, use that exact number.
   - If not, generate a suitable number of questions (around 5 to 7) based on the topic and length of input.
3. Create high-quality multiple-choice questions to test understanding of the topic.

Each question must have:
- "question": the question text
- "options": a list of four choices [A, B, C, D]
- "answer": the correct option label (e.g., "B")

Output Format: Return only a **valid JSON array**, like:
[
  {{
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "answer": "C"
  }},
  ...
]

Text:
\"\"\"
{text}
\"\"\"
"""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Extract JSON part safely using regex
        json_match = re.search(r'\[\s*{.*}\s*\]', raw_text, re.DOTALL)
        if json_match:
            quiz_json = json.loads(json_match.group())
            return quiz_json
        else:
            return {"error": "Failed to parse JSON from response", "raw_output": raw_text}

    except Exception as e:
        return {"error": str(e)}

# 🧪 Example usage
'''
text = "Generate 5 multiple-choice questions on World War II for high school students."
result = generate_quiz_from_text(text)

# Pretty print
print(json.dumps(result, indent=2))'''
