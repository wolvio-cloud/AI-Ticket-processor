"""
ai_ticket_processor.py - Main orchestrator for ticket processing
"""
import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

from fetch_tickets import get_recent_tickets, get_ticket_by_id
from analyze_ticket import analyze_ticket
from update_ticket import update_ticket

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_single_ticket(ticket_id):
    """
    Process a single ticket through the entire pipeline
    
    Args:
        ticket_id: Zendesk ticket ID
        
    Returns:
        Dictionary with processing results
    """
    start_time = time.time()
    
    logger.info(f"Starting processing for ticket #{ticket_id}")
    
    try:
        # Step 1: Fetch ticket
        logger.info(f"📥 Fetching ticket #{ticket_id}...")
        ticket = get_ticket_by_id(ticket_id)
        
        if not ticket:
            logger.error(f"Failed to fetch ticket #{ticket_id}")
            return {
                "ticket_id": ticket_id,
                "success": False,
                "error": "Failed to fetch ticket"
            }
        
        # Step 2: Analyze with AI
        logger.info(f"🤖 Analyzing ticket #{ticket_id}...")
        analysis = analyze_ticket(
            subject=ticket.get('subject', ''),
            description=ticket.get('description', '')
        )
        
        # Step 3: Update Zendesk
        logger.info(f"📤 Updating ticket #{ticket_id}...")
        update_success = update_ticket(ticket_id, analysis)
        
        processing_time = time.time() - start_time
        
        result = {
            "ticket_id": ticket_id,
            "success": True,
            "analysis": analysis,
            "processing_time": round(processing_time, 2),
            "updated": update_success
        }
        
        logger.info(f"✅ Ticket #{ticket_id} processed in {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error processing ticket #{ticket_id}: {str(e)}")
        return {
            "ticket_id": ticket_id,
            "success": False,
            "error": str(e),
            "processing_time": time.time() - start_time
        }


def process_batch(limit=10):
    """
    Process multiple recent tickets in batch
    
    Args:
        limit: Maximum number of tickets to process
        
    Returns:
        Dictionary with batch results
    """
    logger.info(f"🚀 Starting batch processing (limit: {limit})")
    
    start_time = time.time()
    
    # Fetch recent tickets
    tickets = get_recent_tickets(limit)
    
    if not tickets:
        logger.warning("No tickets found to process")
        return {
            "total": 0,
            "processed": 0,
            "failed": 0,
            "results": []
        }
    
    results = {
        "total": len(tickets),
        "processed": 0,
        "failed": 0,
        "results": []
    }
    
    # Process each ticket
    for i, ticket in enumerate(tickets, 1):
        ticket_id = ticket['id']
        
        logger.info(f"\n[{i}/{len(tickets)}] Processing ticket #{ticket_id}")
        print(f"\n{'='*60}")
        print(f"[{i}/{len(tickets)}] Ticket #{ticket_id}: {ticket.get('subject', 'No subject')}")
        print('='*60)
        
        result = process_single_ticket(ticket_id)
        results['results'].append(result)
        
        if result['success']:
            results['processed'] += 1
        else:
            results['failed'] += 1
        
        # Rate limiting - add small delay between tickets
        if i < len(tickets):
            time.sleep(1)
    
    total_time = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 BATCH PROCESSING COMPLETE")
    print('='*60)
    print(f"Total Tickets: {results['total']}")
    print(f"✅ Processed: {results['processed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"⚡ Avg Time: {total_time/len(tickets):.2f}s per ticket")
    print('='*60)
    
    logger.info(f"Batch complete: {results['processed']} processed, {results['failed']} failed")
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Ticket Processor')
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of tickets to process (default: 5)'
    )
    parser.add_argument(
        '--ticket-id',
        type=int,
        help='Process a specific ticket by ID'
    )
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    print("🎯 AI TICKET PROCESSOR")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if args.ticket_id:
        # Process single ticket
        result = process_single_ticket(args.ticket_id)
        print(f"\n📋 Result:")
        print(json.dumps(result, indent=2))
    else:
        # Process batch
        results = process_batch(args.limit)
        
        # Save results to file
        results_file = f"logs/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
