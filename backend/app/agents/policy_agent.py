"""
Policy Agent: Enforces access control and policy compliance.

This agent is responsible for:
1. Checking department-based access permissions
2. Validating user roles and permissions
3. Enforcing data classification rules
4. Logging policy decisions for audit
5. Checking content for sensitive information
"""
from typing import Dict, Any, Tuple, List
import re
from datetime import datetime


# Sensitive patterns to detect and warn about
SENSITIVE_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),  # Social Security Number
    (r'\b\d{16}\b', 'Credit Card'),  # Credit card number
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'Phone Number'),
]

# Departments and their access relationships
DEPARTMENT_HIERARCHY = {
    'Admin': ['HR', 'Finance', 'Engineering', 'Sales', 'Marketing', 'IT', 'Operations', 'Legal', 'Support', 'Admin'],
    'HR': ['HR'],
    'Finance': ['Finance'],
    'Engineering': ['Engineering'],
    'Sales': ['Sales'],
    'Marketing': ['Marketing'],
    'IT': ['IT'],
    'Operations': ['Operations'],
    'Legal': ['Legal'],
    'Support': ['Support'],
}

# Role permissions
ROLE_PERMISSIONS = {
    'admin': {
        'can_view_all_departments': True,
        'can_upload_documents': True,
        'can_delete_documents': True,
        'can_manage_users': True,
        'can_view_audit_logs': True,
    },
    'user': {
        'can_view_all_departments': False,
        'can_upload_documents': False,
        'can_delete_documents': False,
        'can_manage_users': False,
        'can_view_audit_logs': False,
    }
}


def check_policy(user: Dict[str, Any], document: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if a user has access to a document based on department and role policies.
    
    Args:
        user: User dictionary with 'department', 'role', 'email' etc.
        document: Document dictionary with 'department', 'category' etc.
        
    Returns:
        Tuple of (allowed: bool, reason: str)
    """
    if not user:
        return False, "Authentication required."
    
    user_department = user.get('department', '')
    user_role = user.get('role', 'user')
    doc_department = document.get('department', '')
    doc_category = document.get('category', 'department')
    
    # Admins can access everything
    if user_role == 'admin':
        log_policy_decision(user, document, True, "Admin access granted")
        return True, ""
    
    # Common documents are accessible to all
    if doc_category == 'common':
        log_policy_decision(user, document, True, "Common document access")
        return True, ""
    
    # Check department match
    allowed_departments = DEPARTMENT_HIERARCHY.get(user_department, [user_department])
    if doc_department in allowed_departments:
        log_policy_decision(user, document, True, "Department match")
        return True, ""
    
    # Access denied
    reason = f"Access denied: Your department ({user_department}) cannot access {doc_department} documents."
    log_policy_decision(user, document, False, reason)
    return False, reason


def check_role_permission(user: Dict[str, Any], permission: str) -> Tuple[bool, str]:
    """
    Check if a user's role has a specific permission.
    
    Args:
        user: User dictionary with 'role' key
        permission: Permission name to check
        
    Returns:
        Tuple of (allowed: bool, reason: str)
    """
    role = user.get('role', 'user')
    permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS['user'])
    
    if permissions.get(permission, False):
        return True, ""
    
    return False, f"Permission denied: {permission} requires elevated privileges."


def check_sensitive_content(text: str) -> List[Tuple[str, str]]:
    """
    Check text for potentially sensitive information.
    
    Args:
        text: Text to scan for sensitive patterns
        
    Returns:
        List of (matched_text, type) tuples for detected sensitive data
    """
    findings = []
    
    for pattern, data_type in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Partially redact the match
            if len(match) > 4:
                redacted = match[:2] + '*' * (len(match) - 4) + match[-2:]
            else:
                redacted = '*' * len(match)
            findings.append((redacted, data_type))
    
    if findings:
        print(f"[PolicyAgent] WARNING: Detected {len(findings)} sensitive data patterns")
    
    return findings


def validate_department(department: str) -> Tuple[bool, str]:
    """
    Validate that a department name is recognized.
    
    Args:
        department: Department name to validate
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    valid_departments = list(DEPARTMENT_HIERARCHY.keys())
    
    if department in valid_departments:
        return True, ""
    
    return False, f"Invalid department: {department}. Valid options: {', '.join(valid_departments)}"


def log_policy_decision(
    user: Dict[str, Any], 
    resource: Dict[str, Any], 
    allowed: bool, 
    reason: str
) -> None:
    """
    Log policy decisions for audit purposes.
    
    Args:
        user: User making the request
        resource: Resource being accessed
        allowed: Whether access was granted
        reason: Reason for the decision
    """
    try:
        import os
        os.makedirs("logs", exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        user_email = user.get('sub', user.get('email', 'unknown'))
        user_dept = user.get('department', 'unknown')
        user_role = user.get('role', 'unknown')
        resource_dept = resource.get('department', 'unknown')
        
        log_entry = (
            f"POLICY | {timestamp} | "
            f"user={user_email} | role={user_role} | dept={user_dept} | "
            f"resource_dept={resource_dept} | allowed={allowed} | reason={reason}\n"
        )
        
        with open("logs/policy_audit.txt", "a") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"[PolicyAgent] Failed to log policy decision: {e}")


def get_accessible_departments(user: Dict[str, Any]) -> List[str]:
    """
    Get list of departments a user can access.
    
    Args:
        user: User dictionary
        
    Returns:
        List of accessible department names
    """
    role = user.get('role', 'user')
    department = user.get('department', '')
    
    if role == 'admin':
        return list(DEPARTMENT_HIERARCHY.keys())
    
    return DEPARTMENT_HIERARCHY.get(department, [department])
