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
    """Data class for practical tenant evaluation scores"""
    total_score: float
    financial_capability: float
    non_smoking: float
    timing_alignment: float
    german_residency: float
    tidiness_cleanliness: float
    reasoning: str
    red_flags: list
    bonus_points: int


class AIEvaluator:
    def __init__(self):
        self.setup_gemini_api()

    def setup_gemini_api(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Try models in order of success - Strategy 3 worked with gemini-1.5-flash
        model_names = [
            "gemini-2.0-flash",  # Strategy 3 success model
            "gemini-1.5-pro",  # Alternative that often works
            API_CONFIG['gemini_model'],  # From config
            "gemini-2.5-flash",
            "gemini-1.0-pro",
            "models/gemini-1.5-flash"
        ]

        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test with academic evaluation approach
                test_response = self.model.generate_content(
                    "Evaluate academic background: Student studying engineering. Score: {\"student_status\": 85}"
                )
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
            # Generate AI response using working configuration
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,  # Reduced for faster response
                    temperature=0.1,  # Lower temperature for consistency
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
                financial_capability=0,
                non_smoking=0,
                timing_alignment=0,
                german_residency=0,
                tidiness_cleanliness=0,
                reasoning=f"Error during evaluation: {str(e)}",
                red_flags=["AI_EVALUATION_ERROR"],
                bonus_points=0
            )

    def extract_response_text(self, response) -> str:
        """Extract text from Gemini response (handles different API versions)"""
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
                try:
                    if hasattr(response, 'text') and response.text:
                        return response.text
                except ValueError:
                    pass

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
        """Create practical rental evaluation prompt"""

        # Practical rental criteria - focused on what actually matters
        prompt = f"""
Evaluate this person's suitability for a temporary room rental (September 2025 - March 2026) in Munich, Germany.

Rental Details: 636€/month, 1608€ deposit, furnished room, no smoking allowed

Applicant Email:
From: {email_data['sender']}
Subject: {email_data['subject']}
Content: {email_data['body'][:600]}

Rate each practical criterion (0-100):

1. FINANCIAL CAPABILITY (30% weight): Can they afford 636€ rent + 1608€ deposit + utilities? Look for: income, job, salary, BAföG, parental support, savings mentioned.

2. NON-SMOKING (25% weight): Are they definitely non-smokers? Look for: "Nichtraucher", "non-smoker", smoking mentions. Heavy penalty if they smoke.

3. TIMING ALIGNMENT (20% weight): Available September 2025 - March 2026? Look for: semester dates, exchange programs, temporary stays, specific months mentioned.

4. GERMAN RESIDENCY (15% weight): Are they from Germany? Look for: German cities, "aus Deutschland", German university, German address. International students score lower.

5. TIDINESS/CLEANLINESS (10% weight): Will they keep the place clean? Look for: "sauber", "ordentlich", "responsible", "respectful", cleanliness mentions.

Return this exact JSON format:
{{
    "financial_capability": 85,
    "non_smoking": 90,
    "timing_alignment": 80,
    "german_residency": 70,
    "tidiness_cleanliness": 75,
    "reasoning": "Strong financial background, confirmed non-smoker, perfect timing",
    "red_flags": [],
    "bonus_points": 5
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

            # Validate required fields with new criteria
            required_fields = ['financial_capability', 'non_smoking', 'timing_alignment',
                               'german_residency', 'tidiness_cleanliness']

            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Missing field: {field}, setting to 50")
                    data[field] = 50

            # Calculate weighted total score with new weights
            total_score = (
                    data['financial_capability'] * SCORING_WEIGHTS['financial_capability'] / 100 +
                    data['non_smoking'] * SCORING_WEIGHTS['non_smoking'] / 100 +
                    data['timing_alignment'] * SCORING_WEIGHTS['timing_alignment'] / 100 +
                    data['german_residency'] * SCORING_WEIGHTS['german_residency'] / 100 +
                    data['tidiness_cleanliness'] * SCORING_WEIGHTS['tidiness_cleanliness'] / 100
            )

            # Add bonus points (if any)
            bonus_points = data.get('bonus_points', 0)
            total_score += bonus_points

            return TenantScore(
                total_score=round(min(100, total_score), 1),  # Cap at 100
                financial_capability=data['financial_capability'],
                non_smoking=data['non_smoking'],
                timing_alignment=data['timing_alignment'],
                german_residency=data['german_residency'],
                tidiness_cleanliness=data['tidiness_cleanliness'],
                reasoning=data.get('reasoning', 'No reasoning provided'),
                red_flags=data.get('red_flags', []),
                bonus_points=bonus_points
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
        """Emergency parser if JSON parsing fails - using practical criteria"""
        print("🚨 Using emergency response parser...")

        # Default scores for practical criteria
        scores = {
            'financial_capability': 50,
            'non_smoking': 50,
            'timing_alignment': 50,
            'german_residency': 50,
            'tidiness_cleanliness': 50
        }

        # Try to extract some basic info
        text_lower = response_text.lower()

        # Look for financial indicators
        financial_keywords = ['income', 'salary', 'job', 'bafög', 'eltern', 'parents', 'money']
        if any(word in text_lower for word in financial_keywords):
            scores['financial_capability'] = 70

        # Look for non-smoking indicators
        if any(word in text_lower for word in ['nichtraucher', 'non-smoker', 'rauchfrei']):
            scores['non_smoking'] = 90
        elif any(word in text_lower for word in ['raucher', 'smoking']):
            scores['non_smoking'] = 10

        # Look for timing indicators
        if any(word in text_lower for word in ['september', 'march', 'semester', 'temporary']):
            scores['timing_alignment'] = 75

        # Look for German indicators
        if any(word in text_lower for word in ['deutschland', 'germany', 'münchen', 'deutsch']):
            scores['german_residency'] = 80

        # Look for tidiness indicators
        if any(word in text_lower for word in ['sauber', 'clean', 'ordentlich', 'tidy']):
            scores['tidiness_cleanliness'] = 75

        total_score = sum(scores[key] * SCORING_WEIGHTS[key] / 100 for key in scores)

        return TenantScore(
            total_score=round(total_score, 1),
            financial_capability=scores['financial_capability'],
            non_smoking=scores['non_smoking'],
            timing_alignment=scores['timing_alignment'],
            german_residency=scores['german_residency'],
            tidiness_cleanliness=scores['tidiness_cleanliness'],
            reasoning="Emergency parsing - JSON response failed",
            red_flags=["PARSING_ERROR"],
            bonus_points=0
        )


# Test function
def test_ai_evaluator():
    """Test the AI evaluator with a sample email"""
    print("🚀 Testing Practical AI Evaluator...")

    # Sample email data - German student with good financials
    sample_email = {
        'sender': 'max.mueller@student.uni-muenchen.de',
        'subject': 'Bewerbung für Zimmer September-März',
        'date': '2025-08-15',
        'body': '''
Hallo,

ich bin Max Müller, 23 Jahre alt, und studiere Informatik an der LMU München. 
Ich suche eine Zwischenmiete von September 2025 bis März 2026 für mein Auslandssemester.

Ich bin Nichtraucher und sehr ordentlich und sauber. Finanziell bin ich durch einen 
Werkstudentenjob (1200€/Monat) und BAföG gut abgesichert. Die Kaution von 1608€ 
kann ich sofort überweisen.

Ich komme aus München und kenne mich hier gut aus. Meine Eltern wohnen auch hier 
und können als Bürgen fungieren falls nötig.

Das Zimmer wäre perfekt für mich, da es nur 10 Minuten zur Uni ist.

Viele Grüße,
Max Müller
+49 89 123456789
        '''
    }

    evaluator = AIEvaluator()
    score = evaluator.evaluate_candidate(sample_email)

    print(f"\n📊 Practical Evaluation Results:")
    print(f"Total Score: {score.total_score}/100")
    print(f"💰 Financial Capability: {score.financial_capability}/100")
    print(f"🚭 Non-Smoking: {score.non_smoking}/100")
    print(f"⏰ Timing Alignment: {score.timing_alignment}/100")
    print(f"🇩🇪 German Residency: {score.german_residency}/100")
    print(f"🧹 Tidiness/Cleanliness: {score.tidiness_cleanliness}/100")
    print(f"🎁 Bonus Points: {score.bonus_points}")
    print(f"🚩 Red Flags: {score.red_flags}")
    print(f"💭 Reasoning: {score.reasoning}")


if __name__ == "__main__":
    test_ai_evaluator()