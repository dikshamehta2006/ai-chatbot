import re
import logging
from typing import Tuple, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("emotional_chatbot.guardrails")

class GuardrailEvaluation(BaseModel):
    is_safe: bool = True
    is_crisis: bool = False
    flag_type: Optional[str] = None
    sanitized_text: str
    reasons: List[str] = []
    action_taken: str = "PASS"

# High-risk crisis trigger regex patterns
CRISIS_PATTERNS = [
    r"\b(suicide|suicidal)\b",
    r"\b(kill\s+(my\s*self|me))\b",
    r"\b(end\s+(my\s*life|it\s*all))\b",
    r"\b(want\s+to\s+die)\b",
    r"\b(better\s+off\s+dead)\b",
    r"\b(cutting\s+my\s*self)\b",
    r"\b(overdose|hang\s+myself)\b",
    r"\b(take\s+my\s+own\s+life)\b",
    r"\b(jump\s+off\s+(a\s+bridge|a\s+building|the\s+roof))\b",
    r"\b(slit\s+my\s+wrists?)\b",
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"disregard\s+(all\s+)?rules?",
    r"you\s+are\s+now\s+(unrestricted|DAN|jailbroken)",
    r"reveal\s+(your\s+)?(system\s+prompt|master\s+prompt)",
    r"bypass\s+(safety|content\s+filters?)",
]

# PII regex patterns
EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_PATTERN = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
CREDIT_CARD_PATTERN = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"

def sanitize_pii(text: str) -> Tuple[str, List[str]]:
    """Masks sensitive personally identifiable information (PII)."""
    detected = []
    
    if re.search(CREDIT_CARD_PATTERN, text):
        detected.append("CREDIT_CARD")
        text = re.sub(CREDIT_CARD_PATTERN, "[REDACTED_FINANCIAL_INFO]", text)
        
    if re.search(SSN_PATTERN, text):
        detected.append("SSN")
        text = re.sub(SSN_PATTERN, "[REDACTED_ID]", text)
        
    if re.search(EMAIL_PATTERN, text):
        detected.append("EMAIL")
        text = re.sub(EMAIL_PATTERN, "[REDACTED_EMAIL]", text)
        
    if re.search(PHONE_PATTERN, text):
        detected.append("PHONE")
        text = re.sub(PHONE_PATTERN, "[REDACTED_PHONE]", text)
        
    return text, detected

def evaluate_guardrails(text: str) -> GuardrailEvaluation:
    """Evaluates input text through multi-tier safety checks."""
    if not text or not text.strip():
        return GuardrailEvaluation(sanitized_text=text)

    # 1. PII Sanitization
    sanitized_text, pii_detected = sanitize_pii(text)
    
    # 2. Crisis & Self-Harm Red-Flag Check
    text_lower = text.lower()
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"CRISIS GUARDRAIL TRIGGERED: Matched pattern '{pattern}'")
            return GuardrailEvaluation(
                is_safe=False,
                is_crisis=True,
                flag_type="SELF_HARM",
                sanitized_text=sanitized_text,
                reasons=[f"Matched acute distress/crisis indicator: '{pattern}'"],
                action_taken="DISPATCH_EMERGENCY_RESOURCES"
            )

    # 3. Prompt Injection Defense
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"PROMPT INJECTION DETECTED: Matched pattern '{pattern}'")
            return GuardrailEvaluation(
                is_safe=False,
                is_crisis=False,
                flag_type="PROMPT_INJECTION",
                sanitized_text=sanitized_text,
                reasons=["Adversarial prompt injection pattern detected"],
                action_taken="DEFLECT_TO_EMPATHETIC_COMPANION"
            )

    # 4. Safe with potential PII logged
    flag_type = "PII_REDACTED" if pii_detected else None
    return GuardrailEvaluation(
        is_safe=True,
        is_crisis=False,
        flag_type=flag_type,
        sanitized_text=sanitized_text,
        reasons=[f"PII Redacted: {', '.join(pii_detected)}"] if pii_detected else [],
        action_taken="PASS"
    )

def verify_output_safety(output_text: str) -> str:
    """Post-generation check to catch clinical diagnosis or prescription leakage."""
    unwanted_medical_patterns = [
        (r"\bi\s+diagnose\s+you\s+with\b", "I hear the symptoms you describe, though only a doctor can provide a diagnosis"),
        (r"\byou\s+should\s+take\s+(xanax|prozac|zoloft|adderall|lexapro)\b", "speaking with a medical doctor about medication options could be helpful"),
    ]
    cleaned = output_text
    for pattern, replacement in unwanted_medical_patterns:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned
