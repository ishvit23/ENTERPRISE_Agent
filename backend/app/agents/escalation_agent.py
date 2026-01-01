"""
Escalation Agent: Determines when queries need human intervention.

This agent is responsible for:
1. Evaluating answer quality and confidence
2. Detecting queries that need human expertise
3. Identifying urgent or sensitive matters
4. Routing escalations to appropriate teams
5. Logging escalation decisions
"""
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import re


# Confidence thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.7  # Above this, answer is confident
CONFIDENCE_THRESHOLD_LOW = 0.4   # Below this, definitely escalate

# Keywords that trigger automatic escalation
ESCALATION_KEYWORDS = [
    # Legal/Compliance
    'lawsuit', 'legal action', 'subpoena', 'compliance violation', 'audit finding',
    'regulatory', 'investigation', 'whistleblower',
    
    # HR Sensitive
    'harassment', 'discrimination', 'termination', 'layoff', 'workplace violence',
    'hostile work environment', 'wrongful', 'grievance', 'complaint',
    
    # Financial
    'fraud', 'embezzlement', 'misappropriation', 'financial irregularity',
    
    # Security
    'data breach', 'security incident', 'unauthorized access', 'compromised',
    'ransomware', 'phishing attack', 'credential theft',
    
    # Urgent
    'emergency', 'urgent', 'immediately', 'critical issue', 'outage',
    'system down', 'production issue',
]

# Phrases indicating the AI couldn't answer
UNCERTAIN_PHRASES = [
    "i don't know",
    "i'm not sure",
    "i cannot find",
    "no information available",
    "unable to determine",
    "not mentioned in",
    "outside my knowledge",
    "please contact",
    "recommend speaking to",
    "escalate this",
    "human assistance",
]

# Department routing for escalations
ESCALATION_ROUTING = {
    'legal': ['lawsuit', 'legal action', 'subpoena', 'compliance', 'regulatory', 'contract'],
    'hr': ['harassment', 'discrimination', 'termination', 'grievance', 'complaint', 'benefits', 'leave'],
    'security': ['data breach', 'security incident', 'unauthorized', 'compromised', 'phishing'],
    'it': ['outage', 'system down', 'production issue', 'technical', 'access', 'password'],
    'finance': ['fraud', 'embezzlement', 'expense', 'budget', 'payment'],
    'management': ['urgent', 'emergency', 'critical', 'escalate'],
}


def should_escalate(
    answer: str, 
    confidence: float, 
    question: str = "",
    threshold: float = None
) -> bool:
    """
    Determine if a query should be escalated to a human.
    
    Args:
        answer: The generated answer
        confidence: Confidence score (0.0 to 1.0)
        question: Original question (for keyword detection)
        threshold: Custom confidence threshold
        
    Returns:
        True if escalation is recommended
    """
    threshold = threshold or CONFIDENCE_THRESHOLD_LOW
    
    # Check confidence level
    if confidence < threshold:
        print(f"[EscalationAgent] Low confidence ({confidence:.2f}) triggers escalation")
        return True
    
    # Check for uncertain phrases in answer
    answer_lower = answer.lower()
    for phrase in UNCERTAIN_PHRASES:
        if phrase in answer_lower:
            print(f"[EscalationAgent] Uncertain phrase detected: '{phrase}'")
            return True
    
    # Check for escalation keywords in question
    question_lower = question.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in question_lower:
            print(f"[EscalationAgent] Escalation keyword in question: '{keyword}'")
            return True
    
    return False


def get_escalation_details(
    answer: str,
    confidence: float,
    question: str,
    user: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Get detailed escalation information including routing and priority.
    
    Args:
        answer: The generated answer
        confidence: Confidence score
        question: Original question
        user: User information
        
    Returns:
        Dictionary with escalation details
    """
    details = {
        'should_escalate': False,
        'reason': None,
        'route_to': None,
        'priority': 'normal',
        'suggested_action': None,
    }
    
    # Determine if escalation needed and why
    reasons = []
    
    if confidence < CONFIDENCE_THRESHOLD_LOW:
        reasons.append(f"Low confidence score ({confidence:.2f})")
        
    answer_lower = answer.lower()
    for phrase in UNCERTAIN_PHRASES:
        if phrase in answer_lower:
            reasons.append(f"Answer indicates uncertainty")
            break
    
    question_lower = question.lower()
    triggered_keywords = []
    for keyword in ESCALATION_KEYWORDS:
        if keyword in question_lower:
            triggered_keywords.append(keyword)
    
    if triggered_keywords:
        reasons.append(f"Sensitive keywords: {', '.join(triggered_keywords[:3])}")
    
    if not reasons:
        return details
    
    details['should_escalate'] = True
    details['reason'] = '; '.join(reasons)
    
    # Determine routing
    details['route_to'] = determine_routing(question)
    
    # Determine priority
    details['priority'] = determine_priority(question, triggered_keywords)
    
    # Suggest action
    details['suggested_action'] = generate_suggested_action(details['route_to'], details['priority'])
    
    # Log escalation
    log_escalation(question, answer, confidence, details, user)
    
    return details


def determine_routing(question: str) -> str:
    """
    Determine which team should handle the escalation.
    
    Args:
        question: The user's question
        
    Returns:
        Team name for routing
    """
    question_lower = question.lower()
    
    for team, keywords in ESCALATION_ROUTING.items():
        for keyword in keywords:
            if keyword in question_lower:
                return team
    
    return 'general_support'


def determine_priority(question: str, keywords: List[str]) -> str:
    """
    Determine escalation priority level.
    
    Args:
        question: The user's question
        keywords: Triggered escalation keywords
        
    Returns:
        Priority level: 'critical', 'high', 'normal', 'low'
    """
    question_lower = question.lower()
    
    # Critical: security incidents, emergencies
    critical_terms = ['security incident', 'data breach', 'emergency', 'system down', 'outage']
    for term in critical_terms:
        if term in question_lower:
            return 'critical'
    
    # High: legal, harassment, fraud
    high_terms = ['lawsuit', 'harassment', 'discrimination', 'fraud', 'urgent']
    for term in high_terms:
        if term in question_lower:
            return 'high'
    
    # Check if multiple sensitive keywords triggered
    if len(keywords) >= 2:
        return 'high'
    
    return 'normal'


def generate_suggested_action(route_to: str, priority: str) -> str:
    """
    Generate a suggested action for the escalation.
    
    Args:
        route_to: Team for routing
        priority: Priority level
        
    Returns:
        Suggested action string
    """
    actions = {
        'legal': "Contact the Legal department at legal@company.com or ext. 3000",
        'hr': "Contact HR at hr@company.com or ext. 1234",
        'security': "Contact Security immediately at security@company.com or ext. 9999",
        'it': "Contact IT Help Desk at it-support@company.com or ext. 5555",
        'finance': "Contact Finance at finance@company.com or ext. 2345",
        'management': "Contact your department manager or escalations@company.com",
        'general_support': "Contact your department lead for further assistance",
    }
    
    action = actions.get(route_to, actions['general_support'])
    
    if priority == 'critical':
        action = f"URGENT: {action} - Immediate response required"
    elif priority == 'high':
        action = f"Priority: {action} - Response within 4 hours"
    
    return action


def log_escalation(
    question: str,
    answer: str,
    confidence: float,
    details: Dict[str, Any],
    user: Dict[str, Any] = None
) -> None:
    """
    Log escalation events for tracking and analysis.
    
    Args:
        question: Original question
        answer: Generated answer
        confidence: Confidence score
        details: Escalation details
        user: User information
    """
    try:
        import os
        os.makedirs("logs", exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        user_email = user.get('sub', 'unknown') if user else 'unknown'
        user_dept = user.get('department', 'unknown') if user else 'unknown'
        
        log_entry = (
            f"ESCALATION | {timestamp} | "
            f"user={user_email} | dept={user_dept} | "
            f"priority={details.get('priority')} | route={details.get('route_to')} | "
            f"confidence={confidence:.2f} | reason={details.get('reason')} | "
            f"question={question[:100]}\n"
        )
        
        with open("logs/escalation_log.txt", "a") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"[EscalationAgent] Failed to log escalation: {e}")


def format_escalation_message(details: Dict[str, Any], original_answer: str = "") -> str:
    """
    Format a user-friendly escalation message.
    
    Args:
        details: Escalation details
        original_answer: The original answer (if any)
        
    Returns:
        Formatted message for the user
    """
    if not details.get('should_escalate'):
        return original_answer
    
    message_parts = []
    
    if original_answer and original_answer.strip():
        message_parts.append(original_answer)
        message_parts.append("\n---\n")
    
    message_parts.append("⚠️ **This query has been flagged for human review.**\n")
    
    if details.get('priority') in ['critical', 'high']:
        message_parts.append(f"**Priority:** {details['priority'].upper()}\n")
    
    if details.get('suggested_action'):
        message_parts.append(f"\n**Recommended Action:** {details['suggested_action']}\n")
    
    message_parts.append(
        "\nA team member will follow up if needed. "
        "For urgent matters, please use the contact information above."
    )
    
    return "".join(message_parts)
