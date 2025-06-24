# test_gemini_fix.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def test_gemini_response_extraction():
    """Test the fixed Gemini response extraction"""
    print("🔍 Testing Fixed Gemini Response Extraction...")

    # Setup API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False

    genai.configure(api_key=api_key)

    # Test with the model from config
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Model initialized successfully")
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        # Try alternative
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            print("✅ Using fallback model: gemini-1.5-flash")
        except Exception as e2:
            print(f"❌ Fallback model also failed: {e2}")
            return False

    # Test prompt that should return JSON
    test_prompt = '''Analyze this rental application email and return a JSON score.

EMAIL DETAILS:
From: anna.test@student.tum.de
Subject: Bewerbung für Zimmer
Content: Hallo, ich bin Anna, 24 Jahre alt und studiere Bauingenieurwesen im Master an der TUM. Ich bin Nichtraucherin und suche ein Zimmer von September bis März.

REQUIREMENTS:
- Must be a student
- Must be non-smoker  
- Period: September 2025 to March 2026
- Rent: 636€/month in Munich

Score each category 0-100:

RESPOND WITH ONLY THIS JSON FORMAT:
{
    "student_status": 85,
    "non_smoking": 90,
    "financial_capability": 75,
    "timing_alignment": 95,
    "communication_quality": 80,
    "cultural_fit": 85,
    "reasoning": "Strong student candidate, clear non-smoker, perfect timing match",
    "red_flags": []
}'''

    try:
        print("🤖 Generating response...")
        response = model.generate_content(test_prompt)
        print("✅ Response generated successfully")

        # Test the fixed extraction method
        extracted_text = extract_response_text_fixed(response)
        print(f"✅ Text extracted: {len(extracted_text)} characters")
        print(f"📝 First 200 chars: {extracted_text[:200]}...")

        # Try to parse as JSON
        import json
        try:
            # Clean the response
            if extracted_text.startswith('```json'):
                start = extracted_text.find('{')
                end = extracted_text.rfind('}') + 1
                extracted_text = extracted_text[start:end]
            elif extracted_text.startswith('```'):
                start = extracted_text.find('{')
                end = extracted_text.rfind('}') + 1
                extracted_text = extracted_text[start:end]

            # Find JSON in response if mixed with other text
            if '{' in extracted_text and '}' in extracted_text:
                start = extracted_text.find('{')
                end = extracted_text.rfind('}') + 1
                extracted_text = extracted_text[start:end]

            data = json.loads(extracted_text)
            print("✅ JSON parsing successful!")
            print(f"📊 Scores found: {list(data.keys())}")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response for debugging: {extracted_text}")
            return False

    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return False


def extract_response_text_fixed(response) -> str:
    """Fixed method to extract text from Gemini response"""
    try:
        print(f"🔍 Response type: {type(response)}")

        # Method 1: Try candidates path first (most reliable for new API)
        if hasattr(response, 'candidates') and response.candidates:
            print(f"✅ Found {len(response.candidates)} candidates")
            candidate = response.candidates[0]

            if hasattr(candidate, 'content') and candidate.content:
                content = candidate.content
                if hasattr(content, 'parts') and content.parts:
                    print(f"✅ Found {len(content.parts)} parts")
                    part = content.parts[0]
                    if hasattr(part, 'text') and part.text:
                        print("✅ Using candidates[0].content.parts[0].text")
                        return part.text

        # Method 2: Try direct text access (only for simple responses)
        try:
            if hasattr(response, 'text') and response.text:
                print("✅ Using direct .text access")
                return response.text
        except ValueError:
            # This is expected for complex responses, just continue
            print("ℹ️  Direct .text access not available for this response type")

        # Method 3: Direct parts access
        if hasattr(response, 'parts') and response.parts:
            print(f"✅ Found {len(response.parts)} direct parts")
            if response.parts[0] and hasattr(response.parts[0], 'text'):
                print("✅ Using direct parts[0].text")
                return response.parts[0].text

        # Emergency fallback
        response_str = str(response)
        print(f"🚨 Using string conversion: {response_str[:100]}...")
        return response_str

    except Exception as e:
        print(f"❌ Error extracting response text: {e}")
        return f"Extraction failed: {str(e)}"


if __name__ == "__main__":
    success = test_gemini_response_extraction()
    if success:
        print("\n🎉 Gemini API fix successful! The ai_evaluator.py should now work correctly.")
    else:
        print("\n🔧 There are still issues with the Gemini API. Check your setup.")