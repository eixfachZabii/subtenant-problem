# test_env.py

import os
from dotenv import load_dotenv


def test_environment():
    """Test ob Environment Variables richtig geladen werden"""
    print("🔧 Teste Environment Variables...")

    # Load .env file
    load_dotenv()

    # Check for .env file
    if os.path.exists('../../.env'):
        print("✅ .env Datei gefunden")
        with open('../../.env', 'r') as f:
            content = f.read()
            print(f"📄 Inhalt der .env Datei:")
            # Hide API key for security
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    if 'GEMINI_API_KEY' in line:
                        print(f"   GEMINI_API_KEY=AIzaSy... (versteckt)")
                    else:
                        print(f"   {line}")
    else:
        print("❌ .env Datei nicht gefunden!")
        print("Erstellen Sie .env aus .env.template:")
        print("cp .env.template .env")
        return False

    # Test environment variables
    gemini_key = os.getenv('GEMINI_API_KEY')
    target_email = os.getenv('TARGET_EMAIL')

    print(f"\n🔑 Environment Variables:")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}... (gefunden)")
    else:
        print("❌ GEMINI_API_KEY: Nicht gefunden!")

    if target_email:
        print(f"✅ TARGET_EMAIL: {target_email}")
    else:
        print("❌ TARGET_EMAIL: Nicht gefunden!")

    # Test Gemini API connection
    if gemini_key:
        print(f"\n🤖 Teste Gemini API Verbindung...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)

            # First, list available models
            print("📋 Verfügbare Modelle:")
            models = genai.list_models()
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"   ✅ {model.name}")

            # Test with updated model name
            model_name = "gemini-2.5-flash"
            print(f"\n🧪 Teste Modell: {model_name}")
            model = genai.GenerativeModel(model_name)

            # Simple test
            response = model.generate_content("Hello, respond with 'API works!'")
            print(f"✅ Gemini API Response: {response.text}")
            return True
        except Exception as e:
            print(f"❌ Gemini API Fehler: {e}")

            # Try alternative model names
            alternative_models = ["gemini-1.5-pro", "gemini-1.0-pro", "models/gemini-1.5-flash"]
            for alt_model in alternative_models:
                try:
                    print(f"🔄 Versuche alternatives Modell: {alt_model}")
                    model = genai.GenerativeModel(alt_model)
                    response = model.generate_content("Test")
                    print(f"✅ {alt_model} funktioniert!")
                    print(f"💡 Aktualisieren Sie config.py mit: gemini_model = '{alt_model}'")
                    return True
                except Exception as alt_e:
                    print(f"❌ {alt_model} funktioniert nicht: {alt_e}")

            return False

    return gemini_key is not None


if __name__ == "__main__":
    success = test_environment()
    if success:
        print("\n🎉 Environment Setup komplett! Sie können jetzt ai_evaluator.py testen.")
    else:
        print("\n🔧 Bitte beheben Sie die Environment-Probleme zuerst.")