"""
Agents package for Enterprise Knowledge Assistant.

This package contains specialized agents for:
- Retrieval: Fetching relevant documents from ChromaDB
- Answer: Generating responses using LLM
- Policy: Enforcing access control and compliance
- Escalation: Detecting queries needing human intervention
"""

from .retrieval_agent import (
    retrieve_documents,
    retrieve_documents_with_metadata,
    get_relevant_context,
)

from .answer_agent import (
    generate_answer,
    build_prompt,
    estimate_confidence,
)

from .policy_agent import (
    check_policy,
    check_role_permission,
    check_sensitive_content,
    validate_department,
    get_accessible_departments,
)

from .escalation_agent import (
    should_escalate,
    get_escalation_details,
    format_escalation_message,
)

__all__ = [
    # Retrieval
    'retrieve_documents',
    'retrieve_documents_with_metadata',
    'get_relevant_context',
    
    # Answer
    'generate_answer',
    'build_prompt',
    'estimate_confidence',
    
    # Policy
    'check_policy',
    'check_role_permission',
    'check_sensitive_content',
    'validate_department',
    'get_accessible_departments',
    
    # Escalation
    'should_escalate',
    'get_escalation_details',
    'format_escalation_message',
]
