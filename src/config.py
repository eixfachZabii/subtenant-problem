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

# Scoring Weights (must sum to 100)
SCORING_WEIGHTS = {
    "student_status": 25,      # Must be registered student
    "non_smoking": 20,         # Absolute requirement
    "financial_capability": 20, # Can afford rent + deposit
    "timing_alignment": 15,    # Available for exact period
    "communication_quality": 10, # Professional, complete application
    "cultural_fit": 10         # WG lifestyle compatibility
}

# Required Keywords for Scoring
EVALUATION_KEYWORDS = {
    "student_indicators": [
        "student", "studentin", "studium", "uni", "universität", "hochschule",
        "semester", "bachelor", "master", "phd", "immatrikuliert", "enrolled",
        "studying", "college", "campus", "lecture", "vorlesung"
    ],
    "non_smoking_indicators": [
        "nichtraucher", "non-smoker", "nonsmoker", "nicht rauchen",
        "no smoking", "rauchfrei", "smoke-free"
    ],
    "financial_indicators": [
        "einkommen", "income", "gehalt", "salary", "bafög", "scholarship",
        "eltern", "parents", "bürgschaft", "guarantee", "job", "arbeit",
        "finanzierung", "financing", "budget"
    ],
    "timing_indicators": [
        "september", "märz", "march", "7 monate", "7 months", "semester",
        "exchange", "austausch", "temporary", "zwischenmiete"
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
    "gemini_model": "gemini-2.5-flash",  # Updated model name
    "max_tokens": 1000,
    "temperature": 0.3,  # Lower for more consistent scoring
    "timeout_seconds": 30
}