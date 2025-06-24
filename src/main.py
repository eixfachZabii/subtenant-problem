# main.py

import os
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

from email_reader import EmailReader
from ai_evaluator import AIEvaluator, TenantScore
from config import RENTAL_INFO

# Load environment variables
load_dotenv()


class SubtenantFinder:
    def __init__(self):
        self.email_reader = EmailReader()
        self.ai_evaluator = AIEvaluator()
        self.candidates_file = "data/candidates.json"
        self.candidates_data = self.load_candidates()

    def load_candidates(self) -> Dict:
        """Load existing candidates data from JSON file"""
        if os.path.exists(self.candidates_file):
            try:
                with open(self.candidates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Warning: Invalid JSON in candidates file, starting fresh")

        return {
            "candidates": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_processed": 0
            }
        }

    def save_candidates(self):
        """Save candidates data to JSON file"""
        self.candidates_data["metadata"]["last_updated"] = datetime.now().isoformat()

        with open(self.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(self.candidates_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"💾 Saved candidates data to {self.candidates_file}")

    def process_new_emails(self, days_back: int = 7) -> List[Dict]:
        """Process new rental application emails"""
        print(f"🔍 Looking for new emails in the last {days_back} days...")

        # Get recent emails
        emails = self.email_reader.get_recent_emails(days_back)

        if not emails:
            print("📭 No new emails found")
            return []

        new_candidates = []

        for email in emails:
            # Check if we've already processed this email
            if self.is_email_processed(email['id']):
                print(f"⏭️  Skipping already processed email: {email['id']}")
                continue

            print(f"\n🤖 Evaluating candidate: {email['sender']}")

            # Evaluate with AI using practical criteria
            score = self.ai_evaluator.evaluate_candidate(email)

            # Create candidate record with new practical criteria
            candidate = {
                "email_id": email['id'],
                "sender": email['sender'],
                "subject": email['subject'],
                "date": email['date'].isoformat() if hasattr(email['date'], 'isoformat') else str(email['date']),
                "processed_at": datetime.now().isoformat(),
                "score": {
                    "total": score.total_score,
                    "financial_capability": score.financial_capability,
                    "non_smoking": score.non_smoking,
                    "timing_alignment": score.timing_alignment,
                    "german_residency": score.german_residency,
                    "tidiness_cleanliness": score.tidiness_cleanliness,
                    "bonus_points": score.bonus_points
                },
                "reasoning": score.reasoning,
                "red_flags": score.red_flags,
                "email_body": email['body'][:500] + "..." if len(email['body']) > 500 else email['body']
                # Store truncated body
            }

            # Add to candidates
            self.candidates_data["candidates"].append(candidate)
            self.candidates_data["metadata"]["total_processed"] += 1
            new_candidates.append(candidate)

            # Print results
            self.print_candidate_summary(candidate)

        # Save updated data
        if new_candidates:
            self.save_candidates()
            print(f"\n✅ Processed {len(new_candidates)} new candidates")

        return new_candidates

    def is_email_processed(self, email_id: str) -> bool:
        """Check if an email has already been processed"""
        for candidate in self.candidates_data["candidates"]:
            if candidate["email_id"] == email_id:
                return True
        return False

    def print_candidate_summary(self, candidate: Dict):
        """Print a summary of a candidate's evaluation using practical criteria"""
        score = candidate['score']
        print(f"📊 Candidate Summary:")
        print(f"   From: {candidate['sender']}")
        print(f"   🏆 Total Score: {score['total']}/100")
        print(f"   💰 Financial: {score['financial_capability']}/100")
        print(f"   🚭 Non-Smoking: {score['non_smoking']}/100")
        print(f"   ⏰ Timing: {score['timing_alignment']}/100")
        print(f"   🇩🇪 German: {score['german_residency']}/100")
        print(f"   🧹 Tidiness: {score['tidiness_cleanliness']}/100")
        if score.get('bonus_points', 0) > 0:
            print(f"   🎁 Bonus: +{score['bonus_points']} points")
        if candidate['red_flags']:
            print(f"   🚩 Red Flags: {', '.join(candidate['red_flags'])}")
        print(f"   💭 AI Reasoning: {candidate['reasoning'][:100]}...")

    def get_candidate_rankings(self) -> List[Dict]:
        """Get all candidates ranked by total score"""
        candidates = self.candidates_data["candidates"].copy()
        candidates.sort(key=lambda x: x["score"]["total"], reverse=True)
        return candidates

    def show_dashboard(self):
        """Display current dashboard with all candidates using practical criteria"""
        print("\n" + "=" * 70)
        print("🏠 PRACTICAL SUBTENANT FINDER - DASHBOARD")
        print("=" * 70)

        candidates = self.get_candidate_rankings()

        if not candidates:
            print("📭 No candidates processed yet")
            return

        print(f"📊 Total Candidates: {len(candidates)}")
        print(f"🏆 Best Score: {candidates[0]['score']['total']}/100")
        print(f"📈 Average Score: {sum(c['score']['total'] for c in candidates) / len(candidates):.1f}/100")
        print(f"💰 Rent: {RENTAL_INFO['total_monthly']}€/month + {RENTAL_INFO['deposit']}€ deposit")
        print(f"📅 Period: {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']}")

        print("\n🏆 TOP CANDIDATES (Practical Scoring):")
        print("-" * 70)

        for i, candidate in enumerate(candidates[:5], 1):  # Show top 5
            score = candidate['score']
            status_emoji = "🟢" if score['total'] >= 80 else "🟡" if score['total'] >= 60 else "🔴"
            flags_text = f" 🚩{len(candidate['red_flags'])}" if candidate['red_flags'] else ""
            bonus_text = f" 🎁+{score.get('bonus_points', 0)}" if score.get('bonus_points', 0) > 0 else ""

            print(f"{i}. {status_emoji} {candidate['sender']}")
            print(f"   Score: {score['total']}/100{flags_text}{bonus_text}")
            print(f"   Date: {candidate['date'][:10]}")

            # Show key practical scores
            print(f"   💰 Financial: {score['financial_capability']}/100 | "
                  f"🚭 Non-Smoking: {score['non_smoking']}/100 | "
                  f"⏰ Timing: {score['timing_alignment']}/100")
            print(f"   🇩🇪 German: {score['german_residency']}/100 | "
                  f"🧹 Tidiness: {score['tidiness_cleanliness']}/100")

            # Highlight red flags
            if candidate['red_flags']:
                print(f"   🚨 Issues: {', '.join(candidate['red_flags'])}")
            print()

        print("-" * 70)
        print("📋 PRACTICAL CRITERIA WEIGHTS:")
        print("   💰 Financial Capability: 30% (most important)")
        print("   🚭 Non-Smoking: 25% (absolute requirement)")
        print("   ⏰ Timing Alignment: 20% (Sept 2025 - March 2026)")
        print("   🇩🇪 German Residency: 15% (legal/deposit security)")
        print("   🧹 Tidiness/Cleanliness: 10% (property care)")
        print("\nNext: Implement Secretary Problem Algorithm (Day 5-6)")

    def identify_top_candidates(self):
        """Identify candidates who meet practical requirements"""
        candidates = self.get_candidate_rankings()

        excellent_candidates = []
        good_candidates = []
        problematic_candidates = []

        for candidate in candidates:
            score = candidate['score']

            # Excellent: High overall score, no major red flags
            if (score['total'] >= 80 and
                    score['non_smoking'] >= 80 and
                    score['financial_capability'] >= 70 and
                    len(candidate['red_flags']) == 0):
                excellent_candidates.append(candidate)

            # Good: Decent scores, minor issues
            elif (score['total'] >= 65 and
                  score['non_smoking'] >= 70 and
                  score['financial_capability'] >= 60):
                good_candidates.append(candidate)

            # Problematic: Major issues
            else:
                problematic_candidates.append(candidate)

        if excellent_candidates:
            print(f"\n🌟 {len(excellent_candidates)} EXCELLENT candidates found!")
            for candidate in excellent_candidates[:3]:
                print(f"   • {candidate['sender']} ({candidate['score']['total']}/100)")

        if good_candidates:
            print(f"\n👍 {len(good_candidates)} GOOD candidates found")

        if problematic_candidates:
            print(f"\n⚠️ {len(problematic_candidates)} candidates have issues")

    def run_analysis(self):
        """Main function to run the practical tenant analysis"""
        print("🚀 Starting Practical Subtenant Finder...")
        print("📧 Processing rental applications with practical criteria")
        print(
            f"🏠 Rental: {RENTAL_INFO['total_monthly']}€/month | {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']}")

        # Process new emails
        new_candidates = self.process_new_emails()

        # Show dashboard
        self.show_dashboard()

        # Identify top candidates
        self.identify_top_candidates()


def main():
    """Main entry point"""
    print("🏠 Practical Subtenant Finder - Updated Scoring System")
    print("=" * 60)

    # Check environment setup
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set up your .env file with:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        return

    if not os.path.exists('data/credentials.json'):
        print("❌ Gmail credentials.json not found")
        print("Please download credentials.json from Google Cloud Console")
        print("https://console.cloud.google.com/")
        return

    try:
        # Initialize and run the finder
        finder = SubtenantFinder()
        finder.run_analysis()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your setup and try again")


if __name__ == "__main__":
    main()