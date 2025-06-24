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

            # Parse the response
            result = self.parse_ai_response(response.text)

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

    def create_evaluation_prompt(self, email_data: Dict) -> str:
        """Create a detailed prompt for AI evaluation"""

        rental_details = f"""
RENTAL OFFER DETAILS:
- Location: {RENTAL_INFO['address']}
- Rent: {RENTAL_INFO['rent']}€ + {RENTAL_INFO['utilities']}€ utilities = {RENTAL_INFO['total_monthly']}€ total
- Deposit: {RENTAL_INFO['deposit']}€
- Period: {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']} ({RENTAL_INFO['duration_months']} months)
- Room: Furnished {RENTAL_INFO['room_type']}, {RENTAL_INFO['room_height']} height
- Requirements: MUST be registered student, MUST be non-smoker
- WG: Shared bathroom/WC, other residents are friendly students
"""

        email_content = f"""
APPLICANT EMAIL:
From: {email_data['sender']}
Subject: {email_data['subject']}
Date: {email_data['date']}

Content:
{email_data['body']}
"""

        evaluation_criteria = f"""
EVALUATION CRITERIA (0-100 points each):

1. STUDENT STATUS ({SCORING_WEIGHTS['student_status']}% weight):
   - Look for: university mentions, student ID, enrollment proof, academic terms
   - Required: Must be registered student (immatrikuliert)
   - Keywords: {', '.join(EVALUATION_KEYWORDS['student_indicators'])}

2. NON-SMOKING ({SCORING_WEIGHTS['non_smoking']}% weight):
   - Look for: explicit non-smoking confirmation
   - Required: Must confirm non-smoker status
   - Keywords: {', '.join(EVALUATION_KEYWORDS['non_smoking_indicators'])}

3. FINANCIAL CAPABILITY ({SCORING_WEIGHTS['financial_capability']}% weight):
   - Look for: income sources, parental support, savings, job mentions
   - Required: Can afford {RENTAL_INFO['total_monthly']}€/month + {RENTAL_INFO['deposit']}€ deposit
   - Keywords: {', '.join(EVALUATION_KEYWORDS['financial_indicators'])}

4. TIMING ALIGNMENT ({SCORING_WEIGHTS['timing_alignment']}% weight):
   - Look for: availability matching exact dates, semester planning
   - Required: Available September 2025 - March 2026
   - Keywords: {', '.join(EVALUATION_KEYWORDS['timing_indicators'])}

5. COMMUNICATION QUALITY ({SCORING_WEIGHTS['communication_quality']}% weight):
   - Assess: German/English proficiency, completeness, professionalism
   - Look for: proper introduction, specific interest, contact details

6. CULTURAL FIT ({SCORING_WEIGHTS['cultural_fit']}% weight):
   - Look for: WG interest, lifestyle compatibility, Munich/neighborhood appreciation
   - Assess: Personality indicators, social compatibility
"""

        prompt = f"""
You are an expert rental application evaluator. Analyze this tenant application email against the specific rental requirements.

{rental_details}

{email_content}

{evaluation_criteria}

INSTRUCTIONS:
1. Score each criterion from 0-100 points
2. Identify any red flags (smoking mentions, financial concerns, timing issues, etc.)
3. Provide reasoning for your scoring decisions
4. Be strict but fair - this is a competitive rental market

RESPOND WITH VALID JSON ONLY:
{{
    "student_status": <score 0-100>,
    "non_smoking": <score 0-100>,
    "financial_capability": <score 0-100>,
    "timing_alignment": <score 0-100>,
    "communication_quality": <score 0-100>,
    "cultural_fit": <score 0-100>,
    "reasoning": "<detailed explanation of scoring>",
    "red_flags": ["<flag1>", "<flag2>"]
}}
"""
        return prompt

    def parse_ai_response(self, response_text: str) -> TenantScore:
        """Parse AI response and calculate weighted total score"""
        try:
            # Extract JSON from response
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]

            data = json.loads(response_text)

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
            raise
        except KeyError as e:
            print(f"❌ Missing required field in AI response: {e}")
            raise


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