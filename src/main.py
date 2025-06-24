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
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.candidates_file), exist_ok=True)

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

            # Evaluate with AI using YOUR real priorities
            score = self.ai_evaluator.evaluate_candidate(email)

            # Create candidate record with YOUR priority criteria
            candidate = {
                "email_id": email['id'],
                "sender": email['sender'],
                "subject": email['subject'],
                "date": email['date'].isoformat() if hasattr(email['date'], 'isoformat') else str(email['date']),
                "processed_at": datetime.now().isoformat(),
                "score": {
                    "total": score.total_score,
                    "timing_alignment": score.timing_alignment,
                    "financial_capability": score.financial_capability,
                    "trustworthiness": score.trustworthiness,
                    "furniture_acceptance": score.furniture_acceptance,
                    "personalization": score.personalization,
                    "bonus_points": score.bonus_points
                },
                "reasoning": score.reasoning,
                "red_flags": score.red_flags,
                "email_body": email['body'][:500] + "..." if len(email['body']) > 500 else email['body']
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
        """Print a summary of a candidate's evaluation using YOUR real priorities"""
        score = candidate['score']
        print(f"📊 Candidate Summary:")
        print(f"   From: {candidate['sender']}")
        print(f"   🏆 Total Score: {score['total']}/100")
        print(f"   ⏰ Timing (35%): {score['timing_alignment']}/100")
        print(f"   💰 Financial (25%): {score['financial_capability']}/100")
        print(f"   🤝 Trust (20%): {score['trustworthiness']}/100")
        print(f"   🪑 Furniture (15%): {score['furniture_acceptance']}/100")
        print(f"   ✍️ Personal (5%): {score['personalization']}/100")
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
        """Display current dashboard with all candidates using YOUR priorities"""
        print("\n" + "=" * 70)
        print("🏠 SUBTENANT FINDER - YOUR PRIORITIES DASHBOARD")
        print("=" * 70)

        candidates = self.get_candidate_rankings()

        if not candidates:
            print("📭 No candidates processed yet")
            print("\n💡 Run the system to start processing emails!")
            print("   python main.py")
            return

        print(f"📊 Total Candidates: {len(candidates)}")
        print(f"🏆 Best Score: {candidates[0]['score']['total']}/100")
        print(f"📈 Average Score: {sum(c['score']['total'] for c in candidates) / len(candidates):.1f}/100")
        print(f"💰 Rent: {RENTAL_INFO['total_monthly']}€/month + {RENTAL_INFO['deposit']}€ deposit")
        print(f"📅 Period: {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']} (EXACT 7 months)")
        print(f"🪑 Furnished: Must keep your furniture setup")

        print("\n🏆 TOP CANDIDATES (Based on YOUR Priorities):")
        print("-" * 70)

        for i, candidate in enumerate(candidates[:5], 1):  # Show top 5
            score = candidate['score']
            status_emoji = "🟢" if score['total'] >= 80 else "🟡" if score['total'] >= 65 else "🔴"
            flags_text = f" 🚩{len(candidate['red_flags'])}" if candidate['red_flags'] else ""
            bonus_text = f" 🎁+{score.get('bonus_points', 0)}" if score.get('bonus_points', 0) > 0 else ""

            print(f"{i}. {status_emoji} {candidate['sender']}")
            print(f"   Score: {score['total']}/100{flags_text}{bonus_text}")
            print(f"   Date: {candidate['date'][:10]}")

            # Show YOUR priority scores
            print(f"   ⏰ Timing: {score['timing_alignment']}/100 | "
                  f"💰 Financial: {score['financial_capability']}/100 | "
                  f"🤝 Trust: {score['trustworthiness']}/100")
            print(f"   🪑 Furniture: {score['furniture_acceptance']}/100 | "
                  f"✍️ Personal: {score['personalization']}/100")

            # Show critical issues based on YOUR priorities
            timing_ok = score['timing_alignment'] >= 70
            financial_ok = score['financial_capability'] >= 60
            furniture_ok = score['furniture_acceptance'] >= 60

            issues = []
            if not timing_ok:
                issues.append("❌ Timing mismatch")
            if not financial_ok:
                issues.append("❌ Financial concerns")
            if not furniture_ok:
                issues.append("❌ Furniture issues")
            if candidate['red_flags']:
                issues.extend([f"🚨 {flag}" for flag in candidate['red_flags']])

            if issues:
                print(f"   Issues: {' | '.join(issues)}")
            else:
                print(f"   ✅ No major issues detected")
            print()

        print("-" * 70)
        print("📋 YOUR PRIORITY WEIGHTS:")
        print("   ⏰ Timing Alignment: 35% (EXACT Sept 2025 - March 2026)")
        print("   💰 Financial Capability: 25% (636€/month + 1608€ deposit)")
        print("   🤝 Trustworthiness: 20% (reliable, references, stable)")
        print("   🪑 Furniture Acceptance: 15% (keep your setup unchanged)")
        print("   ✍️ Personalization: 5% (thoughtful, non-generic application)")
        print("\n💡 Green = Excellent (80+) | Yellow = Good (65-79) | Red = Issues (<65)")

    def identify_top_candidates(self):
        """Identify candidates who meet YOUR requirements"""
        candidates = self.get_candidate_rankings()

        perfect_candidates = []
        good_candidates = []
        problematic_candidates = []

        for candidate in candidates:
            score = candidate['score']

            # Perfect: Great timing + financials + no red flags
            if (score['total'] >= 80 and
                    score['timing_alignment'] >= 75 and
                    score['financial_capability'] >= 65 and
                    len(candidate['red_flags']) == 0):
                perfect_candidates.append(candidate)

            # Good: Decent scores, manageable issues
            elif (score['total'] >= 65 and
                  score['timing_alignment'] >= 60 and
                  score['financial_capability'] >= 50):
                good_candidates.append(candidate)

            # Problematic: Major timing or financial issues
            else:
                problematic_candidates.append(candidate)

        if perfect_candidates:
            print(f"\n🌟 {len(perfect_candidates)} PERFECT candidates found!")
            for candidate in perfect_candidates[:3]:
                timing = candidate['score']['timing_alignment']
                financial = candidate['score']['financial_capability']
                furniture = candidate['score']['furniture_acceptance']
                print(f"   • {candidate['sender']} ({candidate['score']['total']}/100)")
                print(f"     ⏰ Timing: {timing}/100 | 💰 Financial: {financial}/100 | 🪑 Furniture: {furniture}/100")

        if good_candidates:
            print(f"\n👍 {len(good_candidates)} GOOD candidates (minor issues)")
            for candidate in good_candidates[:2]:
                print(f"   • {candidate['sender']} ({candidate['score']['total']}/100)")

        if problematic_candidates:
            print(f"\n⚠️ {len(problematic_candidates)} PROBLEMATIC candidates")

        # Show timing analysis (your most important criterion)
        exact_timing = [c for c in candidates if c['score']['timing_alignment'] >= 80]
        if exact_timing:
            print(f"\n⏰ {len(exact_timing)} candidates have EXCELLENT timing match!")
            print("   These should be your top priority!")

        return perfect_candidates

    def show_detailed_analysis(self):
        """Show detailed analysis focusing on YOUR priorities"""
        candidates = self.get_candidate_rankings()

        if not candidates:
            print("📭 No candidates to analyze yet")
            return

        print("\n" + "🔍 DETAILED ANALYSIS - YOUR PRIORITIES" + "\n")
        print("=" * 60)

        # Timing Analysis (Your #1 Priority)
        print("⏰ TIMING ANALYSIS (35% weight - Most Important)")
        excellent_timing = [c for c in candidates if c['score']['timing_alignment'] >= 80]
        good_timing = [c for c in candidates if 60 <= c['score']['timing_alignment'] < 80]
        poor_timing = [c for c in candidates if c['score']['timing_alignment'] < 60]

        print(f"   🟢 Excellent (80+): {len(excellent_timing)} candidates")
        print(f"   🟡 Good (60-79): {len(good_timing)} candidates")
        print(f"   🔴 Poor (<60): {len(poor_timing)} candidates")

        if excellent_timing:
            print("   🎯 FOCUS ON THESE (perfect timing):")
            for c in excellent_timing[:3]:
                print(f"      • {c['sender']} ({c['score']['timing_alignment']}/100)")

        # Financial Analysis (Your #2 Priority)
        print(f"\n💰 FINANCIAL ANALYSIS (25% weight)")
        strong_finance = [c for c in candidates if c['score']['financial_capability'] >= 70]
        weak_finance = [c for c in candidates if c['score']['financial_capability'] < 50]

        print(f"   🟢 Strong finances (70+): {len(strong_finance)} candidates")
        print(f"   🔴 Financial concerns (<50): {len(weak_finance)} candidates")

        # Furniture Analysis (Important for you)
        print(f"\n🪑 FURNITURE ACCEPTANCE (15% weight)")
        furniture_good = [c for c in candidates if c['score']['furniture_acceptance'] >= 70]
        furniture_issues = [c for c in candidates if c['score']['furniture_acceptance'] < 50]

        print(f"   🟢 Will keep your setup (70+): {len(furniture_good)} candidates")
        print(f"   🔴 Furniture issues (<50): {len(furniture_issues)} candidates")

        if furniture_issues:
            print("   ⚠️ Watch out for these (might change your furniture):")
            for c in furniture_issues[:2]:
                print(f"      • {c['sender']} ({c['score']['furniture_acceptance']}/100)")

        # Red Flags Summary
        flagged = [c for c in candidates if c['red_flags']]
        if flagged:
            print(f"\n🚩 RED FLAGS SUMMARY")
            print(f"   {len(flagged)} candidates have issues:")
            for c in flagged[:3]:
                print(f"   • {c['sender']}: {', '.join(c['red_flags'])}")

        # Final Recommendations
        print(f"\n🎯 RECOMMENDATIONS BASED ON YOUR PRIORITIES:")

        # Filter for candidates that meet your core requirements
        qualified = [c for c in candidates if
                     c['score']['timing_alignment'] >= 70 and
                     c['score']['financial_capability'] >= 60 and
                     len(c['red_flags']) == 0]

        if qualified:
            print(f"   ✅ {len(qualified)} candidates meet your basic requirements")
            print("   📋 Interview these candidates:")
            for i, c in enumerate(qualified[:3], 1):
                print(f"      {i}. {c['sender']} (Score: {c['score']['total']}/100)")
                print(f"         ⏰ Timing: {c['score']['timing_alignment']}/100 | "
                      f"💰 Finance: {c['score']['financial_capability']}/100")
        else:
            print("   ⚠️ No candidates meet all basic requirements yet")
            print("   💡 Consider adjusting criteria or waiting for more applications")

    def run_analysis(self):
        """Main function to run the tenant analysis with YOUR priorities"""
        print("🚀 Starting Subtenant Finder...")
        print("📧 Processing rental applications with YOUR real priorities")
        print(
            f"🏠 Rental: {RENTAL_INFO['total_monthly']}€/month | {RENTAL_INFO['start_date']} to {RENTAL_INFO['end_date']}")

        # Process new emails
        new_candidates = self.process_new_emails()

        # Show dashboard
        self.show_dashboard()

        # Identify top candidates
        self.identify_top_candidates()

        # Show detailed analysis
        self.show_detailed_analysis()

        # Secretary Problem hint
        total_candidates = len(self.candidates_data["candidates"])
        if total_candidates >= 5:
            print(f"\n🤖 SECRETARY PROBLEM READY!")
            print(f"   📊 You have {total_candidates} candidates")
            print(f"   📈 Observation phase: ~{int(total_candidates * 0.37)} candidates")
            print(f"   🎯 Next: Implement secretary algorithm (see readme Day 5-6)")


def main():
    """Main entry point"""
    print("🏠 Subtenant Finder - YOUR Real Priorities System")
    print("=" * 60)

    # Check environment setup
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set up your .env file with:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        return

    if not os.path.exists('./data/credentials.json'):
        print("❌ Gmail credentials.json not found")
        print("Please download credentials.json from Google Cloud Console")
        print("https://console.cloud.google.com/")
        return

    try:
        # Initialize and run the finder
        finder = SubtenantFinder()

        # Check if we have existing data
        if finder.candidates_data["candidates"]:
            print(f"📋 Found {len(finder.candidates_data['candidates'])} existing candidates")

            # Ask user what they want to do
            print("\nOptions:")
            print("1. Process new emails and update dashboard")
            print("2. Just show dashboard with existing data")
            print("3. Show detailed analysis")

            try:
                choice = input("\nWhat would you like to do? (1/2/3): ").strip()

                if choice == "2":
                    finder.show_dashboard()
                    finder.identify_top_candidates()
                elif choice == "3":
                    finder.show_dashboard()
                    finder.show_detailed_analysis()
                else:
                    finder.run_analysis()

            except KeyboardInterrupt:
                print("\n\n👋 Analysis interrupted by user")
                finder.show_dashboard()
        else:
            # No existing data, run full analysis
            finder.run_analysis()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your setup and try again")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()