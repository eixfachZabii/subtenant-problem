# ai_evaluator.py

import os
import json
import google.generativeai as genai
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import RENTAL_INFO, SCORING_WEIGHTS, EVALUATION_KEYWORDS, API_CONFIG


@dataclass
class TenantScore:
    """Data class for tenant evaluation scores"""
    total_score: float
    student_status: float
    non_smoking: float
    financial_capability: float
    timing_alignment: float
    communication_quality: float
    cultural_fit: float
    reasoning: str
    red_flags: list


class AIEvaluator:
    def __init__(self):
        self.setup_gemini_api()

    def setup_gemini_api(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Try different model names (Google changes them frequently)
        model_names = [
            API_CONFIG['gemini_model'],  # From config
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "models/gemini-1.5-flash"
        ]

        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                test_response = self.model.generate_content("Test")
                print(f"✅ Gemini API configured successfully with model: {model_name}")
                return
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue

        # If no model works, raise an error
        raise ValueError("No working Gemini model found. Please check API key and model availability.")

    def evaluate_candidate(self, email_data: Dict) -> TenantScore:
        """Evaluate a tenant candidate based on their email application"""

        # Create evaluation prompt
        prompt = self.create_evaluation_prompt(email_data)

        try:
            # Generate AI response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=API_CONFIG['max_tokens'],
                    temperature=API_CONFIG['temperature'],
                )
            )

            # Extract text from response (handle new API structure)
            response_text = self.extract_response_text(response)

            # Parse the response
            result = self.parse_ai_response(response_text)

            print(f"🤖 AI Evaluation completed for: {email_data['sender']}")
            print(f"   Total Score: {result.total_score}/100")

            return result

        except Exception as e:
            print(f"❌ Error during AI evaluation: {e}")
            # Return default low scores on error
            return TenantScore(
                total_score=0,
                student_status=0,
                non_smoking=0,
                financial_capability=0,
                timing_alignment=0,
                communication_quality=0,
                cultural_fit=0,
                reasoning=f"Error during evaluation: {str(e)}",
                red_flags=["AI_EVALUATION_ERROR"]
            )

    def extract_response_text(self, response) -> str:
        """Extract text from Gemini response (handles different API versions)"""
        try:
            print(f"🔍 Response type: {type(response)}")
            print(f"🔍 Has text attr: {hasattr(response, 'text')}")
            print(f"🔍 Has candidates: {hasattr(response, 'candidates')}")
            print(f"🔍 Has parts: {hasattr(response, 'parts')}")

            # Method 1: Direct text access (most common)
            if hasattr(response, 'text') and response.text:
                print("✅ Using direct .text access")
                return response.text

            # Method 2: Through candidates
            if hasattr(response, 'candidates') and response.candidates:
                print(f"🔍 Found {len(response.candidates)} candidates")
                candidate = response.candidates[0]

                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content
                    if hasattr(content, 'parts') and content.parts:
                        print(f"🔍 Found {len(content.parts)} parts")
                        part = content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            print("✅ Using candidates[0].content.parts[0].text")
                            return part.text

            # Method 3: Direct parts access
            if hasattr(response, 'parts') and response.parts:
                print(f"🔍 Found {len(response.parts)} direct parts")
                if response.parts[0] and hasattr(response.parts[0], 'text'):
                    print("✅ Using direct parts[0].text")
                    return response.parts[0].text

            # Method 4: Check if response is blocked/filtered
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason'):
                    print(f"⚠️ Response blocked: {feedback.block_reason}")
                    return "Response was blocked by safety filters"

            # Method 5: Try to resolve if it's a streaming response
            if hasattr(response, 'resolve'):
                print("🔄 Trying to resolve response...")
                response.resolve()
                if hasattr(response, 'text') and response.text:
                    return response.text

            # Method 6: Check _result attribute
            if hasattr(response, '_result') and response._result:
                result = response._result
                print(f"🔍 _result type: {type(result)}")
                if hasattr(result, 'candidates') and result.candidates:
                    candidate = result.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        content = candidate.content
                        if hasattr(content, 'parts') and content.parts:
                            part = content.parts[0]
                            if hasattr(part, 'text'):
                                print("✅ Using _result.candidates[0].content.parts[0].text")
                                return part.text

            # Emergency: Just convert to string
            response_str = str(response)
            print(f"🚨 Using string conversion: {response_str[:100]}...")
            return response_str

        except Exception as e:
            print(f"❌ Error extracting response text: {e}")
            import traceback
            traceback.print_exc()

            # Last resort
            return f"Extraction failed: {str(e)}"

    def create_evaluation_prompt(self, email_data: Dict) -> str:
        """Create a simplified prompt for AI evaluation"""

        # Simplified prompt that's less likely to be blocked
        prompt = f"""
Analyze this rental application email and return a JSON score.

EMAIL DETAILS:
From: {email_data['sender']}
Subject: {email_data['subject']}
Content: {email_data['body'][:1000]}

REQUIREMENTS:
- Must be a student
- Must be non-smoker  
- Period: September 2025 to March 2026
- Rent: 636€/month in Munich

Score each category 0-100:

RESPOND WITH ONLY THIS JSON FORMAT:
{{
    "student_status": 80,
    "non_smoking": 70,
    "financial_capability": 75,
    "timing_alignment": 85,
    "communication_quality": 90,
    "cultural_fit": 80,
    "reasoning": "Brief explanation here",
    "red_flags": []
}}
"""
        return prompt.strip()

    def parse_ai_response(self, response_text: str) -> TenantScore:
        """Parse AI response and calculate weighted total score"""
        try:
            # Clean response text
            response_text = response_text.strip()

            # Handle markdown code blocks
            if response_text.startswith('```json'):
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            elif response_text.startswith('```'):
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]

            # Find JSON in response if mixed with other text
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]

            print(f"🔍 Parsing JSON: {response_text[:200]}...")

            data = json.loads(response_text)

            # Validate required fields
            required_fields = ['student_status', 'non_smoking', 'financial_capability',
                               'timing_alignment', 'communication_quality', 'cultural_fit']

            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Missing field: {field}, setting to 0")
                    data[field] = 0

            # Calculate weighted total score
            total_score = (
                    data['student_status'] * SCORING_WEIGHTS['student_status'] / 100 +
                    data['non_smoking'] * SCORING_WEIGHTS['non_smoking'] / 100 +
                    data['financial_capability'] * SCORING_WEIGHTS['financial_capability'] / 100 +
                    data['timing_alignment'] * SCORING_WEIGHTS['timing_alignment'] / 100 +
                    data['communication_quality'] * SCORING_WEIGHTS['communication_quality'] / 100 +
                    data['cultural_fit'] * SCORING_WEIGHTS['cultural_fit'] / 100
            )

            return TenantScore(
                total_score=round(total_score, 1),
                student_status=data['student_status'],
                non_smoking=data['non_smoking'],
                financial_capability=data['financial_capability'],
                timing_alignment=data['timing_alignment'],
                communication_quality=data['communication_quality'],
                cultural_fit=data['cultural_fit'],
                reasoning=data.get('reasoning', 'No reasoning provided'),
                red_flags=data.get('red_flags', [])
            )

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            print(f"Raw response: {response_text}")

            # Emergency fallback: try to extract numbers from text
            return self.emergency_parse_response(response_text)

        except KeyError as e:
            print(f"❌ Missing required field in AI response: {e}")
            print(f"Available fields: {list(data.keys()) if 'data' in locals() else 'None'}")
            raise

    def emergency_parse_response(self, response_text: str) -> TenantScore:
        """Emergency parser if JSON parsing fails"""
        print("🚨 Using emergency response parser...")

        # Default scores
        scores = {
            'student_status': 50,
            'non_smoking': 50,
            'financial_capability': 50,
            'timing_alignment': 50,
            'communication_quality': 50,
            'cultural_fit': 50
        }

        # Try to extract some basic info
        text_lower = response_text.lower()

        # Look for student indicators
        if any(word in text_lower for word in ['student', 'studium', 'uni', 'university']):
            scores['student_status'] = 80

        # Look for non-smoking indicators
        if any(word in text_lower for word in ['nichtraucher', 'non-smoker', 'rauchfrei']):
            scores['non_smoking'] = 90

        total_score = sum(scores[key] * SCORING_WEIGHTS[key] / 100 for key in scores)

        return TenantScore(
            total_score=round(total_score, 1),
            student_status=scores['student_status'],
            non_smoking=scores['non_smoking'],
            financial_capability=scores['financial_capability'],
            timing_alignment=scores['timing_alignment'],
            communication_quality=scores['communication_quality'],
            cultural_fit=scores['cultural_fit'],
            reasoning="Emergency parsing - JSON response failed",
            red_flags=["PARSING_ERROR"]
        )


# Test function
def test_ai_evaluator():
    """Test the AI evaluator with a sample email"""
    print("🚀 Testing AI Evaluator...")

    # Sample email data
    sample_email = {
        'sender': 'max.mustermann@student.uni-muenchen.de',
        'subject': 'Bewerbung für Zimmer in Jutastraße',
        'date': '2025-08-15',
        'body': '''
Hallo,

ich bin Max Mustermann, 23 Jahre alt und studiere Informatik an der LMU München im 5. Semester. 
Ich suche für mein Auslandssemester eine Zwischenmiete von September bis März.

Ich bin Nichtraucher und sehr ordentlich. Finanziell bin ich durch BAföG und einen Nebenjob 
als Tutor abgesichert. Meine Eltern können als Bürgen fungieren.

Das Zimmer wäre perfekt für mich, da es nur 10 Minuten zur Uni ist. Ich interessiere mich 
sehr für das WG-Leben und bin kontaktfreudig.

Viele Grüße,
Max Mustermann
+49 123 456789
        '''
    }

    evaluator = AIEvaluator()
    score = evaluator.evaluate_candidate(sample_email)

    print(f"\n📊 Evaluation Results:")
    print(f"Total Score: {score.total_score}/100")
    print(f"Student Status: {score.student_status}/100")
    print(f"Non-Smoking: {score.non_smoking}/100")
    print(f"Financial: {score.financial_capability}/100")
    print(f"Timing: {score.timing_alignment}/100")
    print(f"Communication: {score.communication_quality}/100")
    print(f"Cultural Fit: {score.cultural_fit}/100")
    print(f"Red Flags: {score.red_flags}")
    print(f"Reasoning: {score.reasoning}")


if __name__ == "__main__":
    test_ai_evaluator()