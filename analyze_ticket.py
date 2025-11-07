"""
analyze_ticket.py - Analyze tickets using OpenAI
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def analyze_ticket(subject, description):
    """
    Analyze ticket using OpenAI gpt-4o-mini
    
    Args:
        subject: Ticket subject line
        description: Ticket description/body
        
    Returns:
        Dictionary with analysis results
    """
    
    prompt = f"""You are a senior support analyst. Analyze this ticket and return ONLY valid JSON:

Ticket: {subject}
{description}

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
        
        print(f"✅ Analysis complete")
        print(f"   Root Cause: {analysis['root_cause']}")
        print(f"   Urgency: {analysis['urgency']}")
        print(f"   Sentiment: {analysis['sentiment']}")
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {str(e)}")
        # Return fallback analysis
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": "JSON parse error"
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI API error: {str(e)}")
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": str(e)
        }
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {
            "summary": "Unable to analyze ticket automatically",
            "root_cause": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "error": str(e)
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
        print("\n📝 Testing ticket analysis...\n")
        
        # Test with sample ticket
        sample_subject = "My order never arrived"
        sample_description = "I paid for order #1234 three days ago but haven't received it. I want a refund immediately!"
        
        result = analyze_ticket(sample_subject, sample_description)
        
        print("\n📊 Analysis Result:")
        print(json.dumps(result, indent=2))

