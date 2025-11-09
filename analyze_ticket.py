"""
analyze_ticket.py - Analyze tickets using OpenAI with PII redaction
"""
import os
import json
import requests
from dotenv import load_dotenv
from pii_redactor import PIIRedactor

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize PII redactor (preserve emails for business context)
redactor = PIIRedactor(preserve_emails=True)


def generate_reply_draft(subject, description, analysis):
    """
    Generate a professional reply draft based on ticket analysis

    Args:
        subject: Ticket subject line
        description: Ticket description/body
        analysis: Dictionary with ticket analysis (summary, root_cause, urgency, sentiment)

    Returns:
        Dictionary with reply_draft, word_count, and generation timestamp
    """
    from datetime import datetime

    # Build context-aware prompt
    prompt = f"""You are a professional customer support agent. Based on this ticket analysis, generate a helpful, empathetic reply draft (2-3 sentences).

Ticket Subject: {subject}
Issue Summary: {analysis.get('summary', 'N/A')}
Category: {analysis.get('root_cause', 'N/A')}
Urgency: {analysis.get('urgency', 'N/A')}
Sentiment: {analysis.get('sentiment', 'N/A')}

Generate a professional reply that:
1. Acknowledges the issue
2. Shows empathy
3. Provides next steps or resolution

Reply draft (2-3 sentences only):"""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional customer support agent. Generate helpful, concise reply drafts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,  # Slightly higher for natural replies
                "max_tokens": 150,   # 2-3 sentences
                "top_p": 1.0
            },
            timeout=30
        )
        response.raise_for_status()

        # Extract reply draft
        draft_text = response.json()['choices'][0]['message']['content'].strip()
        word_count = len(draft_text.split())

        # Simple quality score based on length (50-150 words is good)
        if 30 <= word_count <= 150:
            quality_score = 100
        elif 20 <= word_count < 30 or 150 < word_count <= 200:
            quality_score = 75
        else:
            quality_score = 50

        return {
            'reply_draft': draft_text,
            'draft_word_count': word_count,
            'draft_generated_at': datetime.now().isoformat(),
            'draft_quality_score': quality_score,
            'draft_status': 'success'
        }

    except Exception as e:
        print(f"⚠️  Reply draft generation failed: {str(e)}")
        return {
            'reply_draft': "Draft generation failed. Please manually compose a reply.",
            'draft_word_count': 0,
            'draft_generated_at': datetime.now().isoformat(),
            'draft_quality_score': 0,
            'draft_status': 'failed',
            'draft_error': str(e)
        }


def analyze_ticket(subject, description):
    """
    Analyze ticket using OpenAI gpt-4o-mini with PII redaction

    Args:
        subject: Ticket subject line
        description: Ticket description/body

    Returns:
        Dictionary with analysis results including PII redaction info
    """

    # STEP 1: Redact PII from subject and description
    subject_redaction = redactor.redact(subject)
    description_redaction = redactor.redact(description)

    subject_clean = subject_redaction['redacted_text']
    description_clean = description_redaction['redacted_text']

    # STEP 2: Log PII detection
    has_pii = subject_redaction['has_pii'] or description_redaction['has_pii']
    all_redactions = {}

    if subject_redaction['redactions']:
        all_redactions.update(subject_redaction['redactions'])
    if description_redaction['redactions']:
        for key, val in description_redaction['redactions'].items():
            all_redactions[key] = all_redactions.get(key, 0) + val

    if has_pii:
        pii_types = ', '.join(all_redactions.keys())
        total_count = sum(all_redactions.values())
        print(f"🔒 PII detected and redacted: {total_count} instance(s) ({pii_types})")

    # STEP 3: Use redacted text in OpenAI prompt
    prompt = f"""You are a senior support analyst. Analyze this ticket and return ONLY valid JSON:

Ticket: {subject_clean}
{description_clean}

{{
  "summary": "1-sentence summary",
  "root_cause": "bug|refund|feature|other",
  "urgency": "low|medium|high",
  "sentiment": "positive|neutral|negative"
}}
"""
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a support ticket analyzer. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200,
                "top_p": 1.0
            },
            timeout=30
        )
        response.raise_for_status()
        
        # Extract the AI response
        content = response.json()['choices'][0]['message']['content']
        
        # Parse JSON
        analysis = json.loads(content)
        
        # Validate required fields
        required_fields = ["summary", "root_cause", "urgency", "sentiment"]
        if not all(field in analysis for field in required_fields):
            raise ValueError("Missing required fields in AI response")

        # STEP 4: Add PII redaction metadata to response
        analysis['pii_redacted'] = has_pii
        analysis['redactions'] = all_redactions

        # STEP 5: Generate reply draft
        print(f"✍️  Generating reply draft...")
        draft_result = generate_reply_draft(subject_clean, description_clean, analysis)
        analysis.update(draft_result)

        print(f"✅ Analysis complete")
        print(f"   Root Cause: {analysis['root_cause']}")
        print(f"   Urgency: {analysis['urgency']}")
        print(f"   Sentiment: {analysis['sentiment']}")
        if has_pii:
            print(f"   PII Redacted: ✅ Yes ({total_count} instance(s))")
        if draft_result.get('draft_status') == 'success':
            draft_preview = draft_result['reply_draft'][:50] + "..." if len(draft_result['reply_draft']) > 50 else draft_result['reply_draft']
            print(f"   Reply Draft: ✅ Generated ({draft_result['draft_word_count']} words) - \"{draft_preview}\"")
        else:
            print(f"   Reply Draft: ⚠️  Failed to generate")

        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {str(e)}")
        # Return fallback analysis with PII metadata
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": "JSON parse error",
            "pii_redacted": has_pii,
            "redactions": all_redactions
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI API error: {str(e)}")
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": str(e),
            "pii_redacted": has_pii,
            "redactions": all_redactions
        }

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": str(e),
            "pii_redacted": has_pii,
            "redactions": all_redactions
        }


def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 5
            },
            timeout=10
        )
        response.raise_for_status()
        
        print("✅ OpenAI API connection successful")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🤖 Testing OpenAI Connection...\n")

    if test_openai_connection():
        print("\n" + "="*60)
        print("TEST 1: Normal ticket (no PII)")
        print("="*60)

        sample_subject = "My order never arrived"
        sample_description = "I paid for order #1234 three days ago but haven't received it. I want a refund immediately!"

        result1 = analyze_ticket(sample_subject, sample_description)

        print("\n📊 Analysis Result:")
        print(json.dumps(result1, indent=2))

        print("\n" + "="*60)
        print("TEST 2: Ticket with PII (sensitive data)")
        print("="*60)

        pii_subject = "Refund request for failed payment"
        pii_description = """My payment failed but amount was deducted. Please refund to:

Account No: 123456789012
IFSC Code: HDFC0001234
Phone: 9876543210
PAN: ABCDE1234F

This is urgent!"""

        result2 = analyze_ticket(pii_subject, pii_description)

        print("\n📊 Analysis Result:")
        print(json.dumps(result2, indent=2))

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Test 1 - PII Detected: {'✅ Yes' if result1.get('pii_redacted') else '❌ No'}")
        print(f"Test 2 - PII Detected: {'✅ Yes' if result2.get('pii_redacted') else '❌ No'}")
        if result2.get('redactions'):
            print(f"Test 2 - Redacted types: {', '.join(result2['redactions'].keys())}")
        print("="*60)

