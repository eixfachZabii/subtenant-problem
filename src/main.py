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

            # Evaluate with AI
            score = self.ai_evaluator.evaluate_candidate(email)

            # Create candidate record
            candidate = {
                "email_id": email['id'],
                "sender": email['sender'],
                "subject": email['subject'],
                "date": email['date'].isoformat() if hasattr(email['date'], 'isoformat') else str(email['date']),
                "processed_at": datetime.now().isoformat(),
                "score": {
                    "total": score.total_score,
                    "student_status": score.student_status,
                    "non_smoking": score.non_smoking,
                    "financial_capability": score.financial_capability,
                    "timing_alignment": score.timing_alignment,
                    "communication_quality": score.communication_quality,
                    "cultural_fit": score.cultural_fit
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
        """Print a summary of a candidate's evaluation"""
        print(f"📊 Candidate Summary:")
        print(f"   From: {candidate['sender']}")
        print(f"   Total Score: {candidate['score']['total']}/100")
        print(
            f"   Top Strengths: Student={candidate['score']['student_status']}, Non-smoking={candidate['score']['non_smoking']}")
        if candidate['red_flags']:
            print(f"   🚩 Red Flags: {', '.join(candidate['red_flags'])}")
        print(f"   AI Reasoning: {candidate['reasoning'][:100]}...")

    def get_candidate_rankings(self) -> List[Dict]:
        """Get all candidates ranked by total score"""
        candidates = self.candidates_data["candidates"].copy()
        candidates.sort(key=lambda x: x["score"]["total"], reverse=True)
        return candidates

    def show_dashboard(self):
        """Display current dashboard with all candidates"""
        print("\n" + "=" * 60)
        print("🏠 PERFECT SUBTENANT FINDER - DASHBOARD")
        print("=" * 60)

        candidates = self.get_candidate_rankings()

        if not candidates:
            print("📭 No candidates processed yet")
            return

        print(f"📊 Total Candidates: {len(candidates)}")
        print(f"🏆 Best Score: {candidates[0]['score']['total']}/100")
        print(f"📈 Average Score: {sum(c['score']['total'] for c in candidates) / len(candidates):.1f}/100")

        print("\n🏆 TOP CANDIDATES:")
        print("-" * 60)

        for i, candidate in enumerate(candidates[:5], 1):  # Show top 5
            status_emoji = "🟢" if candidate['score']['total'] >= 80 else "🟡" if candidate['score'][
                                                                                    'total'] >= 60 else "🔴"
            flags_text = f" 🚩{len(candidate['red_flags'])}" if candidate['red_flags'] else ""

            print(f"{i}. {status_emoji} {candidate['sender']}")
            print(f"   Score: {candidate['score']['total']}/100{flags_text}")
            print(f"   Date: {candidate['date'][:10]}")
            print(
                f"   Strengths: Student={candidate['score']['student_status']}, Financial={candidate['score']['financial_capability']}")
            print()

        print("-" * 60)
        print("Next: Implement Secretary Problem Algorithm (Day 5-6)")

    def run_analysis(self):
        """Main function to run the tenant analysis"""
        print("🚀 Starting Perfect Subtenant Finder...")
        print("📧 Processing all incoming emails as rental applications")
        print(f"🏠 Rental Period: {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']}")

        # Process new emails
        new_candidates = self.process_new_emails()

        # Show dashboard
        self.show_dashboard()


def main():
    """Main entry point"""
    print("🏠 Perfect Subtenant Finder - Day 1 Setup")
    print("=" * 50)

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