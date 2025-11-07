import time
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Ticket, TicketAnalysis, ProcessingLog, User
from app.services.zendesk_service import ZendeskService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class TicketProcessor:
    """Main service for processing tickets end-to-end"""
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        
        # Initialize services
        self.zendesk = ZendeskService(
            subdomain=user.zendesk_subdomain,
            email=user.zendesk_email,
            api_token=user.zendesk_api_token
        )
        self.openai = OpenAIService(api_key=user.openai_api_key)
    
    def _log(self, ticket_id: int, status: str, stage: str, error: Optional[str] = None):
        """Create a processing log entry"""
        log = ProcessingLog(
            ticket_id=ticket_id,
            status=status,
            stage=stage,
            error_message=error
        )
        self.db.add(log)
        self.db.commit()
    
    def process_ticket(self, zendesk_ticket_id: int) -> Dict:
        """
        Process a single ticket through the entire pipeline
        
        Args:
            zendesk_ticket_id: The Zendesk ticket ID
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        ticket_db_id = None
        
        try:
            # Step 1: Fetch ticket from Zendesk
            logger.info(f"Fetching ticket {zendesk_ticket_id} from Zendesk")
            ticket_data = self.zendesk.get_ticket(zendesk_ticket_id)
            
            if not ticket_data:
                return {
                    "success": False,
                    "error": "Failed to fetch ticket from Zendesk",
                    "processing_time": time.time() - start_time
                }
            
            # Step 2: Save or update ticket in database
            ticket = self.db.query(Ticket).filter(
                Ticket.zendesk_ticket_id == zendesk_ticket_id,
                Ticket.user_id == self.user.id
            ).first()
            
            if not ticket:
                ticket = Ticket(
                    user_id=self.user.id,
                    zendesk_ticket_id=zendesk_ticket_id,
                    subject=ticket_data.get("subject", ""),
                    description=ticket_data.get("description", ""),
                    status=ticket_data.get("status"),
                    priority=ticket_data.get("priority"),
                    requester_email=ticket_data.get("requester", {}).get("email"),
                    ticket_created_at=datetime.fromisoformat(
                        ticket_data.get("created_at", "").replace("Z", "+00:00")
                    )
                )
                self.db.add(ticket)
                self.db.commit()
                self.db.refresh(ticket)
            
            ticket_db_id = ticket.id
            self._log(ticket_db_id, "processing", "fetch")
            
            # Step 3: Analyze with OpenAI
            logger.info(f"Analyzing ticket {zendesk_ticket_id} with AI")
            analysis_result = self.openai.analyze_ticket(
                subject=ticket.subject,
                description=ticket.description
            )
            
            # Step 4: Calculate cost
            tokens_used = analysis_result.get("tokens_used", 0)
            cost = self.openai.calculate_cost(tokens_used)
            
            # Step 5: Save analysis to database
            analysis = TicketAnalysis(
                ticket_id=ticket.id,
                summary=analysis_result["summary"],
                category=analysis_result["category"],
                urgency=analysis_result["urgency"],
                sentiment=analysis_result["sentiment"],
                processing_time=time.time() - start_time,
                cost=cost,
                model_used=analysis_result.get("model_used"),
                tokens_used=tokens_used
            )
            self.db.add(analysis)
            
            # Update ticket
            ticket.processed_at = datetime.utcnow()
            self.db.commit()
            
            self._log(ticket_db_id, "processing", "analyze")
            
            # Step 6: Update Zendesk with tags and internal note
            logger.info(f"Updating ticket {zendesk_ticket_id} in Zendesk")
            
            tags = [
                "ai-processed",
                f"category:{analysis_result['category']}",
                f"urgency:{analysis_result['urgency']}",
                f"sentiment:{analysis_result['sentiment']}"
            ]
            
            internal_note = f"""🤖 AI Analysis:
            
Summary: {analysis_result['summary']}
Category: {analysis_result['category']}
Urgency: {analysis_result['urgency']}
Sentiment: {analysis_result['sentiment']}

Processing Time: {round(time.time() - start_time, 2)}s
Cost: ${cost:.6f}
"""
            
            update_success = self.zendesk.update_ticket(
                ticket_id=zendesk_ticket_id,
                tags=tags,
                internal_note=internal_note
            )
            
            if update_success:
                self._log(ticket_db_id, "success", "update")
            else:
                self._log(ticket_db_id, "partial_success", "update", 
                         "Analysis saved but Zendesk update failed")
            
            # Return success response
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "ticket_id": zendesk_ticket_id,
                "analysis": {
                    "summary": analysis_result["summary"],
                    "category": analysis_result["category"],
                    "urgency": analysis_result["urgency"],
                    "sentiment": analysis_result["sentiment"]
                },
                "processing_time": round(processing_time, 2),
                "cost": cost,
                "zendesk_updated": update_success
            }
            
        except Exception as e:
            logger.error(f"Failed to process ticket {zendesk_ticket_id}: {str(e)}")
            
            if ticket_db_id:
                self._log(ticket_db_id, "failed", "unknown", str(e))
            
            return {
                "success": False,
                "ticket_id": zendesk_ticket_id,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def process_batch(self, limit: int = 10) -> Dict:
        """
        Process multiple unprocessed tickets in batch
        
        Args:
            limit: Maximum number of tickets to process
            
        Returns:
            Summary of batch processing
        """
        logger.info(f"Starting batch processing (limit: {limit})")
        
        # Fetch unprocessed tickets
        unprocessed = self.zendesk.get_unprocessed_tickets(limit=limit)
        
        results = {
            "total": len(unprocessed),
            "processed": 0,
            "failed": 0,
            "results": []
        }
        
        for ticket_data in unprocessed:
            ticket_id = ticket_data.get("id")
            result = self.process_ticket(ticket_id)
            
            results["results"].append(result)
            
            if result["success"]:
                results["processed"] += 1
            else:
                results["failed"] += 1
        
        logger.info(
            f"Batch complete: {results['processed']} processed, "
            f"{results['failed']} failed"
        )
        
        return results
