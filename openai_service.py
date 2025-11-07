import json
import logging
from typing import Dict
from openai import OpenAI
from app.config import settings
from app.schemas import AIAnalysisResponse

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for analyzing tickets using OpenAI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.DEFAULT_OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    def _build_prompt(self, subject: str, description: str) -> str:
        """
        Build the analysis prompt for OpenAI
        
        Args:
            subject: Ticket subject
            description: Ticket description
            
        Returns:
            Formatted prompt string
        """
        return f"""Analyze this support ticket and return ONLY valid JSON:

Subject: {subject}
Description: {description}

Return exactly this structure:
{{
  "summary": "one sentence summary of the issue",
  "category": "bug|feature|billing|support|other",
  "urgency": "low|medium|high",
  "sentiment": "positive|neutral|negative"
}}

Classification guidelines:
- bug: System malfunction or error
- feature: New functionality request
- billing: Payment or subscription issue
- support: General help or how-to question
- other: Doesn't fit above categories

Urgency levels:
- high: Blocking customer, urgent language, refund request
- medium: Important but not blocking
- low: Nice-to-have, suggestion, general question

Sentiment:
- positive: Polite, thankful, constructive
- neutral: Factual, straightforward
- negative: Angry, frustrated, demanding"""
    
    def analyze_ticket(
        self, 
        subject: str, 
        description: str
    ) -> Dict:
        """
        Analyze a ticket using OpenAI
        
        Args:
            subject: Ticket subject
            description: Ticket description
            
        Returns:
            Dictionary with analysis results and metadata
        """
        try:
            prompt = self._build_prompt(subject, description)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a support ticket analyzer. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1.0
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse JSON response
            analysis = json.loads(content)
            
            # Validate response has required fields
            required_fields = ["summary", "category", "urgency", "sentiment"]
            if not all(field in analysis for field in required_fields):
                raise ValueError("Missing required fields in AI response")
            
            # Add metadata
            analysis["tokens_used"] = tokens_used
            analysis["model_used"] = self.model
            
            logger.info(f"Successfully analyzed ticket: {analysis['category']}/{analysis['urgency']}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
            # Return fallback analysis
            return {
                "summary": "Unable to analyze ticket automatically",
                "category": "other",
                "urgency": "medium",
                "sentiment": "neutral",
                "tokens_used": 0,
                "model_used": self.model,
                "error": "JSON parse error"
            }
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            # Return fallback analysis
            return {
                "summary": "Unable to analyze ticket automatically",
                "category": "other",
                "urgency": "medium",
                "sentiment": "neutral",
                "tokens_used": 0,
                "model_used": self.model,
                "error": str(e)
            }
    
    def calculate_cost(self, tokens_used: int) -> float:
        """
        Calculate the cost of an OpenAI API call
        
        Args:
            tokens_used: Total tokens used in the request
            
        Returns:
            Cost in dollars
        """
        # gpt-4o-mini pricing (as of documentation)
        # Input: $0.150 per 1M tokens
        # Output: $0.600 per 1M tokens
        # Simplified: Average ~$0.375 per 1M tokens
        cost_per_million = 0.375
        cost = (tokens_used / 1_000_000) * cost_per_million
        return round(cost, 6)
    
    def test_connection(self) -> bool:
        """
        Test the OpenAI API connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False
