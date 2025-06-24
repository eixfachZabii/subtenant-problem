# Perfect Subtenant Finder - Simple 1-Week Roadmap

## Day 1-2: Core Setup & Email Processing

### Day 1: Basic Structure
- Set up Python project with `gmail-api`, `google-generative-ai`, `pandas`
- Create `main.py`, `email_reader.py`, `ai_evaluator.py`
- Get Gmail API credentials and test basic email reading

### Day 2: Email Parsing
- Build function to fetch emails from jutastrasse.wg@gmail.com
- Extract email content and sender details
- Save applicant data to simple JSON file for persistence

## Day 3-4: AI Analysis & Scoring

### Day 3: Gemini Integration
- Set up Gemini API with prompt for tenant evaluation
- Create scoring function that analyzes email content for:
  - Student status mentions
  - Non-smoking confirmation  
  - Financial capability indicators
  - Timing/availability match
- Return structured score (0-100)

### Day 4: Scoring System
- Implement weighted scoring based on your criteria
- Create simple candidate ranking system
- Test with sample emails to tune prompts

## Day 5-6: Secretary Problem Algorithm

### Day 5: Algorithm Implementation
- Build secretary problem logic:
  - Track total applications received
  - Calculate 37% observation threshold
  - Store best score from observation phase
  - Make accept/reject decisions in selection phase

### Day 6: Decision Engine
- Integrate all components into `main.py`
- Add simple console output showing decisions and reasoning
- Create basic email templates for responses (manual sending for now)

## Day 7: Testing & Polish

### Day 7: Final Integration
- Test full workflow with real emails
- Add error handling and logging
- Create simple CLI commands to run analysis and see results
- Document usage in README

## Core File Structure

```
subtenant-finder/
├── main.py              # Main orchestrator
├── email_reader.py      # Gmail API integration  
├── ai_evaluator.py      # Gemini scoring
├── secretary_algo.py    # Decision algorithm
├── config.py           # Criteria and settings
├── candidates.json     # Simple data storage
└── requirements.txt
```

## Minimum Viable Product (MVP)

- **Input**: Emails from jutastrasse.wg@gmail.com
- **Process**: AI scoring + Secretary problem decision
- **Output**: Console showing "ACCEPT" or "REJECT" with reasoning
- **Data**: JSON file tracking all candidates and decisions

## Easy Extensions (Post-Week 1)

- Web dashboard with Streamlit (1 day)
- Automated email responses (1 day)  
- Database upgrade from JSON (half day)
- Better AI prompts and scoring (ongoing)
- Alternative algorithms beyond secretary problem (1-2 days)

## Key Success Criteria

By end of week 1, you should have:
- ✅ Automated email reading from your Gmail
- ✅ AI-powered candidate evaluation and scoring
- ✅ Secretary problem algorithm making accept/reject decisions
- ✅ Simple console interface showing results and reasoning
- ✅ JSON database tracking all candidates and decisions

This keeps the core concept intact while being achievable in one focused week with AI assistance!