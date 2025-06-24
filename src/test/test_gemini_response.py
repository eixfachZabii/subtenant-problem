# test_gemini_response.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def test_gemini_response():
    """Debug Gemini API Response Structure"""
    print("🔍 Testing Gemini Response Structure...")

    # Setup API
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)

    # Try different models
    models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    for model_name in models:
        try:
            print(f"\n🧪 Testing model: {model_name}")
            model = genai.GenerativeModel(model_name)

            # Simple test prompt
            test_prompt = '''Return this exact JSON:
{
    "test": "success",
    "model": "working"
}'''

            response = model.generate_content(test_prompt)

            print(f"✅ Model {model_name} responded!")
            print(f"🔍 Response type: {type(response)}")
            print(f"🔍 Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")

            # Try different ways to access text
            methods = [
                ("response.text", lambda r: r.text),
                ("response.candidates[0].content.parts[0].text", lambda r: r.candidates[0].content.parts[0].text),
                ("response.parts[0].text", lambda r: r.parts[0].text if hasattr(r, 'parts') else "No parts"),
                ("str(response)", lambda r: str(r))
            ]

            for method_name, method_func in methods:
                try:
                    result = method_func(response)
                    print(f"✅ {method_name}: {result[:100]}...")
                    break
                except Exception as e:
                    print(f"❌ {method_name}: {e}")

            # If we found a working model, stop
            break

        except Exception as e:
            print(f"❌ Model {model_name} failed: {e}")

    print("\n🎯 Use the working method in ai_evaluator.py!")


if __name__ == "__main__":
    test_gemini_response()