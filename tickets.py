from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Ticket
from app.schemas import (
    TicketResponse,
    ProcessTicketRequest,
    ProcessTicketResponse
)
from app.auth import get_current_active_user
from app.services.ticket_processor import TicketProcessor

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/process", response_model=ProcessTicketResponse)
def process_single_ticket(
    request: ProcessTicketRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a single ticket by ID
    
    Args:
        request: Ticket processing request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Processing result
    """
    # Check if user has configured integrations
    if not current_user.zendesk_subdomain or not current_user.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please configure Zendesk and OpenAI settings first"
        )
    
    # Process ticket
    processor = TicketProcessor(current_user, db)
    result = processor.process_ticket(request.ticket_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to process ticket")
        )
    
    return ProcessTicketResponse(
        ticket_id=result["ticket_id"],
        status="success",
        analysis=result.get("analysis"),
        processing_time=result["processing_time"],
        message="Ticket processed successfully"
    )


@router.post("/process-batch")
def process_batch_tickets(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process multiple unprocessed tickets in batch
    
    Args:
        limit: Maximum number of tickets to process
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Batch processing summary
    """
    # Check if user has configured integrations
    if not current_user.zendesk_subdomain or not current_user.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please configure Zendesk and OpenAI settings first"
        )
    
    # Process batch
    processor = TicketProcessor(current_user, db)
    result = processor.process_batch(limit=limit)
    
    return result


@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    sentiment: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List tickets with optional filters
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        category: Filter by category
        urgency: Filter by urgency
        sentiment: Filter by sentiment
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of tickets
    """
    query = db.query(Ticket).filter(Ticket.user_id == current_user.id)
    
    # Apply filters through joins if analysis exists
    if category or urgency or sentiment:
        from app.models import TicketAnalysis
        query = query.join(TicketAnalysis)
        
        if category:
            query = query.filter(TicketAnalysis.category == category)
        if urgency:
            query = query.filter(TicketAnalysis.urgency == urgency)
        if sentiment:
            query = query.filter(TicketAnalysis.sentiment == sentiment)
    
    # Order by most recent first
    query = query.order_by(Ticket.created_at.desc())
    
    tickets = query.offset(skip).limit(limit).all()
    
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID
    
    Args:
        ticket_id: Ticket ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Ticket details
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == current_user.id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return ticket


@router.get("/stats/summary")
def get_ticket_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for tickets
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Ticket statistics
    """
    from sqlalchemy import func
    from app.models import TicketAnalysis
    
    total_tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user.id
    ).count()
    
    processed_tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user.id,
        Ticket.processed_at.isnot(None)
    ).count()
    
    total_cost = db.query(func.sum(TicketAnalysis.cost)).join(Ticket).filter(
        Ticket.user_id == current_user.id
    ).scalar() or 0.0
    
    return {
        "total_tickets": total_tickets,
        "processed_tickets": processed_tickets,
        "unprocessed_tickets": total_tickets - processed_tickets,
        "total_cost": round(total_cost, 4)
    }
