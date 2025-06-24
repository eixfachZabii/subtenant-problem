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
    """Data class for tenant evaluation scores based on your real priorities"""
    total_score: float
    timing_alignment: float
    financial_capability: float
    trustworthiness: float
    furniture_acceptance: float
    personalization: float
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

        # Try models in order of success
        model_names = [
            "gemini-2.0-flash",  # Most reliable
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            API_CONFIG['gemini_model'],
        ]

        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test with academic evaluation approach
                test_response = self.model.generate_content(
                    "Test response: {\"timing\": 85}"
                )
                print(f"✅ Gemini API configured successfully with model: {model_name}")
                return
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue

        raise ValueError("No working Gemini model found. Please check API key and model availability.")

    def evaluate_candidate(self, email_data: Dict) -> TenantScore:
        """Evaluate a tenant candidate based on YOUR real priorities"""

        prompt = self.create_evaluation_prompt(email_data)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.1,
                )
            )

            response_text = self.extract_response_text(response)
            result = self.parse_ai_response(response_text)

            print(f"🤖 AI Evaluation completed for: {email_data['sender']}")
            print(f"   Total Score: {result.total_score}/100")

            return result

        except Exception as e:
            print(f"❌ Error during AI evaluation: {e}")
            return TenantScore(
                total_score=0,
                timing_alignment=0,
                financial_capability=0,
                trustworthiness=0,
                furniture_acceptance=0,
                personalization=0,
                reasoning=f"Error during evaluation: {str(e)}",
                red_flags=["AI_EVALUATION_ERROR"],
                bonus_points=0
            )

    def create_evaluation_prompt(self, email_data: Dict) -> str:
        """Create evaluation prompt based on YOUR real priorities"""

        prompt = f"""
You are evaluating rental applications for a 7-month furnished room in Munich (Sept 2025 - March 2026).
The owner will return and needs their furniture kept exactly as is.

CRITICAL: Score based on these priorities:
1. TIMING (35%): Exact 7 months only - no longer, no shorter
2. FINANCIAL (25%): Can afford 636€/month + 1608€ deposit  
3. TRUSTWORTHINESS (20%): Reliable, references, stable background
4. FURNITURE (15%): Will keep furnished setup, no changes
5. PERSONALIZATION (5%): Thoughtful, specific application (not generic)

Applicant Email:
From: {email_data['sender']}
Subject: {email_data['subject']}
Content: {email_data['body'][:800]}

Rate each criterion (0-100):

TIMING_ALIGNMENT: 
- 100: Explicitly needs Sept 2025 - March 2026 (exchange semester, exact dates)
- 80-90: Mentions 7 months, semester abroad, temporary stay
- 60-70: Mentions approximate timeframe but not exact
- 40-50: Vague timing or slightly different dates
- 0-30: Wrong dates, wants permanent, or much shorter/longer

FINANCIAL_CAPABILITY:
- 100: Clear stable income + mentions deposit readiness
- 80-90: Good job/income mentioned (BAföG, salary, parents)
- 60-70: Some financial info but not complete
- 40-50: Vague financial mentions
- 0-30: No financial info or concerning financial situation

TRUSTWORTHINESS:
- 100: References offered + stable background + employment
- 80-90: Good background indicators (job, university, previous rentals)
- 60-70: Some trust indicators but incomplete
- 40-50: Basic info but no strong trust signals
- 0-30: Red flags or very little information

FURNITURE_ACCEPTANCE:
- 100: Explicitly loves furnished setup, mentions keeping everything
- 80-90: Positive about furnished room, no changes mentioned
- 60-70: Accepts furnished but not enthusiastic
- 40-50: Neutral about furniture
- 0-30: Mentions own furniture or wanting changes

PERSONALIZATION:
- 100: Specific details about your place, personal reasons
- 80-90: Clearly tailored application, shows research
- 60-70: Some personalization but generic elements
- 40-50: Mostly generic with minor personal touches
- 0-30: Obviously copy-pasted, no personalization

RED FLAGS to check:
- Wrong timing/dates
- Wants to bring own furniture
- No financial info
- Generic copy-paste application
- Wants longer stay
- Group applications

Return ONLY this JSON:
{{
    "timing_alignment": 85,
    "financial_capability": 75,
    "trustworthiness": 80,
    "furniture_acceptance": 90,
    "personalization": 70,
    "reasoning": "Exchange student with perfect timing, stable finances, loves furnished setup",
    "red_flags": [],
    "bonus_points": 10
}}
"""
        return prompt.strip()

    def extract_response_text(self, response) -> str:
        """Extract text from Gemini response (handles different API versions)"""
        try:
            # Method 1: Try candidates path first (most reliable for new API)
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content
                    if hasattr(content, 'parts') and content.parts:
                        part = content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            return part.text

            # Method 2: Try direct text access
            try:
                if hasattr(response, 'text') and response.text:
                    return response.text
            except ValueError:
                pass

            # Method 3: Direct parts access
            if hasattr(response, 'parts') and response.parts:
                if response.parts[0] and hasattr(response.parts[0], 'text'):
                    return response.parts[0].text

            # Emergency fallback
            return str(response)

        except Exception as e:
            print(f"❌ Error extracting response text: {e}")
            return f"Extraction failed: {str(e)}"

    def parse_ai_response(self, response_text: str) -> TenantScore:
        """Parse AI response and calculate weighted total score based on YOUR priorities"""
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

            # Find JSON in response
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]

            data = json.loads(response_text)

            # Validate required fields with YOUR priorities
            required_fields = ['timing_alignment', 'financial_capability', 'trustworthiness',
                              'furniture_acceptance', 'personalization']

            for field in required_fields:
                if field not in data:
                    print(f"⚠️ Missing field: {field}, setting to 50")
                    data[field] = 50

            # Calculate weighted total score with YOUR priorities
            total_score = (
                data['timing_alignment'] * SCORING_WEIGHTS['timing_alignment'] / 100 +
                data['financial_capability'] * SCORING_WEIGHTS['financial_capability'] / 100 +
                data['trustworthiness'] * SCORING_WEIGHTS['trustworthiness'] / 100 +
                data['furniture_acceptance'] * SCORING_WEIGHTS['furniture_acceptance'] / 100 +
                data['personalization'] * SCORING_WEIGHTS['personalization'] / 100
            )

            # Add bonus points
            bonus_points = data.get('bonus_points', 0)
            total_score += bonus_points

            return TenantScore(
                total_score=round(min(100, total_score), 1),
                timing_alignment=data['timing_alignment'],
                financial_capability=data['financial_capability'],
                trustworthiness=data['trustworthiness'],
                furniture_acceptance=data['furniture_acceptance'],
                personalization=data['personalization'],
                reasoning=data.get('reasoning', 'No reasoning provided'),
                red_flags=data.get('red_flags', []),
                bonus_points=bonus_points
            )

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            return self.emergency_parse_response(response_text)

    def emergency_parse_response(self, response_text: str) -> TenantScore:
        """Emergency parser if JSON parsing fails - based on YOUR priorities"""
        print("🚨 Using emergency response parser...")

        scores = {
            'timing_alignment': 50,
            'financial_capability': 50,
            'trustworthiness': 50,
            'furniture_acceptance': 50,
            'personalization': 50
        }

        text_lower = response_text.lower()

        # Check timing indicators
        if any(word in text_lower for word in ['september', 'march', '7 month', 'semester', 'exchange']):
            scores['timing_alignment'] = 75

        # Check financial indicators
        if any(word in text_lower for word in ['income', 'job', 'bafög', 'salary', 'parents', 'deposit']):
            scores['financial_capability'] = 70

        # Check trustworthiness
        if any(word in text_lower for word in ['reference', 'reliable', 'responsible', 'previous landlord']):
            scores['trustworthiness'] = 75

        # Check furniture acceptance
        if any(word in text_lower for word in ['furnished', 'möbliert', 'furniture', 'complete setup']):
            scores['furniture_acceptance'] = 75

        # Check personalization
        if any(word in text_lower for word in ['jutastraße', 'neuhausen', 'your place', 'specifically']):
            scores['personalization'] = 75

        total_score = sum(scores[key] * SCORING_WEIGHTS[key] / 100 for key in scores)

        return TenantScore(
            total_score=round(total_score, 1),
            timing_alignment=scores['timing_alignment'],
            financial_capability=scores['financial_capability'],
            trustworthiness=scores['trustworthiness'],
            furniture_acceptance=scores['furniture_acceptance'],
            personalization=scores['personalization'],
            reasoning="Emergency parsing - JSON response failed",
            red_flags=["PARSING_ERROR"],
            bonus_points=0
        )


# Test function
def test_ai_evaluator():
    """Test the AI evaluator with your priorities"""
    print("🚀 Testing AI Evaluator with YOUR priorities...")

    # Sample email - perfect timing match
    sample_email = {
        'sender': 'anna.exchange@student.tum.de',
        'subject': 'Zwischenmiete Jutastraße September-März - Austauschsemester',
        'date': '2025-08-15',
        'body': '''
Hallo!

Ich bin Anna, 23, und studiere an der TU München. Ich suche eine Zwischenmiete 
von GENAU September 2025 bis März 2026 für mein Auslandssemester in den USA.

Eure Wohnung in der Jutastraße ist perfekt - ich kenne Neuhausen gut und die 
Lage ist ideal für mich. Besonders toll finde ich, dass alles möbliert ist, 
da ich nach dem Semester direkt in die USA fliege und nichts Eigenes brauche.

Finanziell bin ich durch BAföG (735€) und einen Werkstudentenjob (600€) gut 
aufgestellt. Die Kaution von 1608€ habe ich bereits auf meinem Sparkonto.
Meine Eltern können auch als Bürgen fungieren.

Ich habe bereits zwei Jahre in einer WG gelebt und kann gerne Referenzen von 
meinem vorherigen Vermieter zur Verfügung stellen. Bin sehr ordentlich und 
respektvoll mit fremdem Eigentum.

Das Zimmer wäre wirklich perfekt für mich - genau die richtige Zeit und ich 
würde alles so lassen wie es ist, da ich ja weiß, dass ihr zurückkommt!

Liebe Grüße,
Anna
        '''
    }

    evaluator = AIEvaluator()
    score = evaluator.evaluate_candidate(sample_email)

    print(f"\n📊 Evaluation Results (YOUR Priorities):")
    print(f"🏆 Total Score: {score.total_score}/100")
    print(f"⏰ Timing Alignment (35%): {score.timing_alignment}/100")
    print(f"💰 Financial Capability (25%): {score.financial_capability}/100")
    print(f"🤝 Trustworthiness (20%): {score.trustworthiness}/100")
    print(f"🪑 Furniture Acceptance (15%): {score.furniture_acceptance}/100")
    print(f"✍️ Personalization (5%): {score.personalization}/100")
    print(f"🎁 Bonus Points: {score.bonus_points}")
    print(f"🚩 Red Flags: {score.red_flags}")
    print(f"💭 Reasoning: {score.reasoning}")


if __name__ == "__main__":
    test_ai_evaluator()