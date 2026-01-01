"""
Answer Agent: Generates responses using LLM with retrieved context.

This agent is responsible for:
1. Constructing effective prompts with context
2. Calling the LLM (Groq or Ollama) for answer generation
3. Parsing and validating LLM responses
4. Providing confidence scores for answers
5. Falling back gracefully when LLM is unavailable
"""
from starlette.config import Config
import requests
import json
import os
from typing import Tuple

config = Config('.env')

# Groq API (Free, recommended for students)
GROQ_API_KEY = os.getenv('GROQ_API_KEY', config('GROQ_API_KEY', cast=str, default=''))
GROQ_MODEL = config('GROQ_MODEL', cast=str, default='llama-3.1-8b-instant')

# Ollama fallback (for local development)
OLLAMA_HOST = config('OLLAMA_HOST', cast=str, default='host.docker.internal')
OLLAMA_PORT = config('OLLAMA_PORT', cast=str, default='11434')
LLM_MODEL = config('LLM_MODEL', cast=str, default='llama2')

# Use Groq if API key is available, otherwise Ollama
USE_GROQ = bool(GROQ_API_KEY)

# Confidence keywords for heuristic scoring
HIGH_CONFIDENCE_PHRASES = [
    "according to", "the policy states", "as per", "the document says",
    "based on the context", "the guidelines indicate", "it is stated that"
]
LOW_CONFIDENCE_PHRASES = [
    "i don't know", "i'm not sure", "unclear", "no information",
    "cannot find", "not mentioned", "unable to determine", "i cannot"
]


def build_prompt(question: str, context: str, user_department: str = None) -> str:
    """
    Build an effective prompt for the LLM with context and instructions.
    
    Args:
        question: User's question
        context: Retrieved document context
        user_department: Optional department for personalization
        
    Returns:
        Formatted prompt string
    """
    department_note = f" You are assisting a {user_department} department employee." if user_department else ""
    
    if not context or context.strip() == "":
        return f"""You are an Enterprise Knowledge Assistant.{department_note}

The user has asked a question, but no relevant documents were found in the knowledge base.

Question: {question}

Please respond helpfully by:
1. Acknowledging that you couldn't find specific information in the knowledge base
2. Suggesting who they might contact (e.g., HR for benefits, IT for technical issues)
3. Recommending they check with their manager or department lead

Keep your response professional and helpful."""

    return f"""You are an Enterprise Knowledge Assistant.{department_note}

Your task is to answer the user's question using ONLY the information provided in the context below.
Do NOT make up information. If the context doesn't contain enough information to fully answer the question, 
say so clearly and suggest who they might contact for more information.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER'S QUESTION:
{question}

INSTRUCTIONS:
1. Answer based ONLY on the context provided above
2. Be concise but thorough
3. If the context contains relevant policies or guidelines, cite them
4. If you cannot find the answer in the context, clearly state that
5. Suggest contacting the relevant department if more information is needed

YOUR ANSWER:"""


def estimate_confidence(answer: str, context: str) -> float:
    """
    Estimate confidence score based on answer content and context matching.
    
    Args:
        answer: The generated answer
        context: The context that was provided
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    answer_lower = answer.lower()
    
    # Check for low confidence indicators
    for phrase in LOW_CONFIDENCE_PHRASES:
        if phrase in answer_lower:
            return 0.3
    
    # Check for high confidence indicators
    confidence = 0.5  # Base confidence
    for phrase in HIGH_CONFIDENCE_PHRASES:
        if phrase in answer_lower:
            confidence += 0.1
    
    # Boost confidence if answer references specific content
    if context and len(answer) > 50:
        # Check if answer contains terms from context
        context_words = set(context.lower().split())
        answer_words = set(answer_lower.split())
        overlap = len(context_words.intersection(answer_words))
        if overlap > 10:
            confidence += 0.15
    
    # Cap at 0.95 (never 100% confident)
    return min(0.95, confidence)


def generate_answer(question: str, context: str, user_department: str = None) -> Tuple[str, float]:
    """
    Generate an answer using the LLM with the provided context.
    Uses Groq API if available (free, fast), otherwise falls back to Ollama.
    
    Args:
        question: User's question
        context: Retrieved document context
        user_department: Optional department for personalization
        
    Returns:
        Tuple of (answer, confidence_score)
    """
    prompt = build_prompt(question, context, user_department)
    
    print(f"[AnswerAgent] Generating answer for: {question[:50]}...")
    print(f"[AnswerAgent] Context length: {len(context)} chars")
    print(f"[AnswerAgent] Using: {'Groq API' if USE_GROQ else 'Ollama'}")
    
    # Try Groq first (free cloud LLM)
    if USE_GROQ:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an Enterprise Knowledge Assistant. Answer questions based only on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                answer = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if answer:
                    confidence = estimate_confidence(answer, context)
                    print(f"[AnswerAgent] Groq response ({len(answer)} chars, confidence: {confidence:.2f})")
                    return answer, confidence
            else:
                print(f"[AnswerAgent] Groq API error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"[AnswerAgent] Groq error: {e}")
    
    # Fallback to Ollama (local LLM)
    try:
        response = requests.post(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        
        print(f"[AnswerAgent] Ollama response status: {response.status_code}")
        
        if response.ok:
            try:
                result = response.json()
                answer = result.get('response', '').strip()
                
                if answer:
                    confidence = estimate_confidence(answer, context)
                    print(f"[AnswerAgent] Generated answer ({len(answer)} chars, confidence: {confidence:.2f})")
                    return answer, confidence
                    
            except json.JSONDecodeError:
                lines = response.text.strip().splitlines()
                full_answer = ""
                for line in lines:
                    try:
                        obj = json.loads(line)
                        if 'response' in obj:
                            full_answer += obj['response']
                    except:
                        continue
                
                if full_answer.strip():
                    confidence = estimate_confidence(full_answer, context)
                    return full_answer.strip(), confidence
        
        print(f"[AnswerAgent] Ollama request failed: {response.status_code}")
        
    except requests.exceptions.Timeout:
        print("[AnswerAgent] LLM request timed out")
    except requests.exceptions.ConnectionError:
        print("[AnswerAgent] Could not connect to LLM service")
    except Exception as e:
        print(f"[AnswerAgent] Error: {e}")
    
    # Fallback response when LLM is unavailable
    return generate_fallback_answer(question, context)


def generate_fallback_answer(question: str, context: str) -> Tuple[str, float]:
    """
    Generate a fallback answer when LLM is unavailable.
    Uses simple keyword matching to provide basic responses.
    
    Args:
        question: User's question
        context: Retrieved document context
        
    Returns:
        Tuple of (answer, confidence_score)
    """
    if not context or context.strip() == "":
        return (
            "I couldn't find relevant information in the knowledge base to answer your question. "
            "Please contact your department lead or HR for assistance.",
            0.2
        )
    
    # Provide context directly with a note
    answer = (
        "I found some relevant information that may help:\n\n"
        f"{context[:1500]}{'...' if len(context) > 1500 else ''}\n\n"
        "Please review the above information. If you need more specific assistance, "
        "contact your department lead or the relevant team."
    )
    
    return answer, 0.4
