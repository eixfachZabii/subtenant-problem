# config.py

# Rental Property Details
RENTAL_INFO = {
    "address": "Jutastraße 11, 80636 München Neuhausen-Nymphenburg",
    "rent": 536,
    "utilities": 100,
    "total_monthly": 636,
    "deposit": 1608,
    "start_date": "2025-09-01",
    "end_date": "2026-03-31",
    "duration_months": 7,
    "furnished": True,
    "room_type": "Altbau Dachgeschoss",
    "room_height": "2.52m"
}

# Email Configuration
EMAIL_CONFIG = {
    "check_interval_minutes": 15,
    "max_emails_per_check": 50  # Prevent overwhelming the system
}

# UPDATED: Practical Scoring Weights (must sum to 100)
SCORING_WEIGHTS = {
    "financial_capability": 30,  # Can afford rent + deposit + utilities
    "non_smoking": 25,           # Absolute requirement - no exceptions
    "timing_alignment": 20,      # Available for exact period (Sept 2025 - March 2026)
    "german_residency": 15,      # From Germany (easier for deposits, legal issues)
    "tidiness_cleanliness": 10,  # Clean, organized, respectful of property
}

# Required Keywords for Practical Scoring
EVALUATION_KEYWORDS = {
    "financial_indicators": [
        "einkommen", "income", "gehalt", "salary", "bafög", "bafoeg", "scholarship", "stipendium",
        "eltern", "parents", "bürgschaft", "guarantee", "job", "arbeit", "arbeite", "angestellt",
        "finanzierung", "budget", "bezahlen", "afford", "kaution", "deposit", "euro", "€",
        "verdiene", "earning", "werkstudent", "minijob", "vollzeit", "teilzeit"
    ],
    "non_smoking_indicators": [
        "nichtraucher", "nichtraucherin", "non-smoker", "nonsmoker", "nicht rauchen",
        "no smoking", "rauchfrei", "smoke-free", "anti-raucher"
    ],
    "smoking_indicators": [
        "raucher", "raucherin", "smoking", "rauchen", "zigaretten", "cigarettes"
    ],
    "timing_indicators": [
        "september", "sept", "märz", "march", "2025", "2026", "7 monate", "7 months",
        "semester", "exchange", "austausch", "temporary", "zwischenmiete", "befristet",
        "ab september", "bis märz", "from september", "until march"
    ],
    "german_residency_indicators": [
        "deutschland", "germany", "deutsch", "german", "de", "münchen", "munich",
        "berlin", "hamburg", "köln", "düsseldorf", "stuttgart", "frankfurt",
        "geboren in", "born in", "aus deutschland", "from germany", "deutsche",
        "bundesland", "staat", "staatsangehörigkeit", "nationality"
    ],
    "international_indicators": [
        "spain", "spanien", "italy", "italien", "france", "frankreich", "usa",
        "china", "india", "brasil", "mexico", "turkey", "türkei", "poland", "polen",
        "international", "exchange student", "erasmus", "visa", "permit"
    ],
    "tidiness_indicators": [
        "sauber", "clean", "ordentlich", "tidy", "organized", "organisiert", "aufgeräumt",
        "reinlich", "hygiene", "respektvoll", "respectful", "verantwortlich", "responsible",
        "zuverlässig", "reliable", "pfleglich", "careful", "schonend"
    ]
}

# Secretary Problem Settings
SECRETARY_ALGORITHM = {
    "observation_ratio": 0.37,  # 37% rule
    "minimum_candidates": 5,    # Need at least this many to apply algorithm
    "score_threshold": 75,      # Minimum acceptable score (0-100)
    "time_pressure_factor": 0.1 # Reduce threshold as deadline approaches
}

# API Configuration
API_CONFIG = {
    "gemini_model": "gemini-1.5-flash",  # Working model for bypass
    "max_tokens": 800,
    "temperature": 0.1,  # Lower for more consistent scoring
    "timeout_seconds": 30
}

# PRACTICAL RED FLAGS - Auto-reject candidates
RED_FLAGS = {
    "smoking_mentioned": "Mentions smoking or being a smoker",
    "wrong_timeframe": "Wants permanent rental or wrong dates",
    "no_financial_info": "No mention of income, job, or financial capability",
    "high_risk_country": "From country with difficult legal recourse",
    "too_cheap": "Seems to expect much lower rent",
    "group_rental": "Wants to bring multiple people",
    "pets_mentioned": "Mentions having pets (if not allowed)",
    "party_lifestyle": "Mentions parties, loud music, drinking heavily"
}

# PRACTICAL BONUS POINTS
BONUS_CRITERIA = {
    "german_citizen": 10,           # German passport holder
    "munich_local": 5,              # Already lives in Munich
    "professional_job": 10,         # Has stable employment
    "previous_wg_experience": 5,    # Mentions previous WG living
    "references_offered": 10,       # Offers references from previous landlords
    "early_availability": 5,        # Available before September if needed
    "deposit_ready": 10,            # Mentions having deposit ready
}