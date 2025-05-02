import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
ENABLE_OPENAI = False

def generate_analysis(vuln):
    cve_id = vuln.get("id", "Unknown ID")
    summary = vuln.get("summary", "No summary provided")
    package = vuln.get("package", "Unknown Package")
    version = vuln.get("version", "Unknown Version")

    prompt = (
        f"You are a security expert. For the following vulnerability, return a JSON object with keys:\n"
        f"1. description - What is the issue in plain English\n"
        f"2. impact - How it can affect an application using {package} version {version}\n"
        f"3. suggestion - How to fix or mitigate the vulnerability\n\n"
        f"Return only valid JSON.\n\n"
        f"Vulnerability ID: {cve_id}\n"
        f"Summary: {summary}\n"
    )

    try:
        if not ENABLE_OPENAI:
            return mock_analysis(vuln)
        
        response = client.chat.completions.create(
                                                    model="gpt-4o",
                                                    messages=[{"role": "user", "content": prompt}],
                                                    temperature=0.4,
                                                    max_tokens=500)
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"❌ AI request failed for {cve_id}: {e}")
        return None

def mock_analysis(vuln):
    return {
        "description": f"Mock analysis for {vuln.get('id', 'unknown')}",
        "impact": "This could affect your application if improperly handled.",
        "suggestion": f"Consider upgrading <b>{vuln.get('package')}</b> to the latest version."
    }