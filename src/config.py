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
    "max_emails_per_check": 50
}

# UPDATED: Your Real Priorities - Scoring Weights (must sum to 100)
SCORING_WEIGHTS = {
    "timing_alignment": 35,      # MOST IMPORTANT: Exact 7 months (Sept 2025 - March 2026)
    "financial_capability": 25,  # Important: Can afford rent + deposit
    "trustworthiness": 20,       # Important: Reliable, references, stable background
    "furniture_acceptance": 15,  # Important: Explicitly mentions keeping your furniture
    "personalization": 5,        # Bonus: Non-generic, personalized application
}

# Required Keywords for Your Priorities
EVALUATION_KEYWORDS = {
    "timing_exact_match": [
        "september 2025", "sept 2025", "march 2026", "märz 2026", "7 monate", "7 months",
        "semester", "exchange semester", "auslandssemester", "temporary", "zwischenmiete",
        "befristet", "ab september", "bis märz", "from september", "until march",
        "exactly 7 months", "genau 7 monate", "september bis märz"
    ],
    "timing_flexible": [
        "flexible", "länger möglich", "can extend", "shorter also ok", "kürzere zeit"
    ],
    "financial_indicators": [
        "einkommen", "income", "gehalt", "salary", "bafög", "bafoeg", "scholarship", "stipendium",
        "eltern", "parents", "bürgschaft", "guarantee", "job", "arbeit", "arbeite", "angestellt",
        "finanzierung", "budget", "bezahlen", "afford", "kaution", "deposit", "euro", "€",
        "verdiene", "earning", "werkstudent", "minijob", "vollzeit", "teilzeit", "savings", "ersparnisse"
    ],
    "trustworthiness_indicators": [
        "referenzen", "references", "previous landlord", "vorherige vermieter", "recommendation",
        "empfehlung", "verantwortlich", "responsible", "zuverlässig", "reliable", "ehrlich", "honest",
        "keine probleme", "no problems", "good tenant", "guter mieter", "schufa", "clean record",
        "arbeitsvertrag", "employment contract", "unbefristet", "permanent position"
    ],
    "furniture_acceptance": [
        "möbliert", "furnished", "furniture", "möbel", "einrichtung", "complete setup",
        "perfekt möbliert", "fully furnished", "everything included", "alles enthalten",
        "deine möbel", "your furniture", "existing furniture", "vorhandene einrichtung",
        "übernehme alles", "take everything", "nothing to buy", "nichts kaufen"
    ],
    "furniture_problems": [
        "eigene möbel", "own furniture", "bring furniture", "möbel mitbringen",
        "new furniture", "neue möbel", "change furniture", "möbel ändern"
    ],
    "personalization_indicators": [
        "jutastraße", "neuhausen", "nymphenburg", "specific location mention",
        "why this room", "warum dieses zimmer", "personal reason", "persönlicher grund",
        "my situation", "meine situation", "about me", "über mich", "my background"
    ],
    "generic_indicators": [
        "dear sir/madam", "sehr geehrte damen und herren", "to whom it may concern",
        "i am writing to", "hiermit bewerbe ich mich", "standard application",
        "copy paste", "same message", "multiple applications"
    ]
}

# Your Red Flags - Auto-reject or heavy penalty
RED_FLAGS = {
    "wrong_timeframe": "Wants different dates or permanent rental",
    "wants_longer": "Explicitly wants to stay longer than March 2026",
    "wants_shorter": "Only wants 2-3 months or less",
    "no_financial_info": "No mention of income, job, or how they'll pay",
    "own_furniture": "Wants to bring own furniture or change setup",
    "too_cheap_expectations": "Expects much lower rent or negotiation",
    "group_application": "Wants to bring friends or multiple people",
    "party_lifestyle": "Heavy emphasis on parties, social life, drinking",
    "generic_application": "Clearly copy-pasted, no personalization",
    "unreliable_contact": "No phone number or proper contact info"
}

# Your Bonus Criteria
BONUS_CRITERIA = {
    "perfect_timing_match": 15,      # Explicitly mentions Sept 2025 - March 2026
    "exchange_student": 10,          # Exchange/semester abroad (reliable timeline)
    "furniture_enthusiasm": 10,      # Specifically mentions loving furnished setup
    "local_knowledge": 5,            # Knows Munich/Neuhausen area
    "professional_references": 10,   # Offers landlord references
    "stable_employment": 8,          # Has employment contract or stable income
    "deposit_ready": 5,              # Mentions having deposit available
    "personal_connection": 8,        # Mentions why specifically your place appeals
    "german_language": 3,            # Application in good German (trust factor)
    "detailed_application": 5,       # Thorough, thoughtful application
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
    "gemini_model": "gemini-1.5-flash",
    "max_tokens": 800,
    "temperature": 0.1,  # Lower for more consistent scoring
    "timeout_seconds": 30
}