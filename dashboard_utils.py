# dashboard_utils.py
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class DashboardData:
    """Load and process ticket processor logs"""
    
    def __init__(self, logs_dir="logs"):
        self.logs_dir = Path(logs_dir)
    
    def get_recent_results(self, days=7):
        """Load results from last N days"""
        results = []
        cutoff = datetime.now() - timedelta(days=days)
        
        # Find all results_*.json files
        for file in self.logs_dir.glob("results_*.json"):
            try:
                # Parse timestamp from filename: results_20251105_223301.json
                date_str = file.stem.split('_')[1]  # "20251105"
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date >= cutoff:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        results.append(data)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        return results
    
    def get_all_tickets(self, days=7):
        """Get all processed tickets from recent results"""
        all_tickets = []
        results = self.get_recent_results(days)
        
        for result_file in results:
            if 'results' in result_file:
                for ticket in result_file['results']:
                    if ticket.get('status') == 'success':
                        all_tickets.append({
                            'ticket_id': ticket.get('ticket_id'),
                            'category': ticket.get('analysis', {}).get('root_cause', 'unknown'),
                            'urgency': ticket.get('analysis', {}).get('urgency', 'unknown'),
                            'sentiment': ticket.get('analysis', {}).get('sentiment', 'unknown'),
                            'processing_time': ticket.get('processing_time', 0),
                            'timestamp': result_file.get('timestamp', ''),
                            'summary': ticket.get('analysis', {}).get('summary', '')
                        })
        
        return pd.DataFrame(all_tickets)
    
    def calculate_metrics(self, days=7):
        """Calculate dashboard metrics"""
        results = self.get_recent_results(days)
        
        if not results:
            return {
                'total_processed': 0,
                'success_rate': 0,
                'avg_time': 0,
                'total_cost': 0
            }
        
        total_processed = sum(r.get('processed', 0) for r in results)
        total_failed = sum(r.get('failed', 0) for r in results)
        total_tickets = total_processed + total_failed
        
        # Calculate average processing time
        all_times = []
        for r in results:
            if 'results' in r:
                for ticket in r['results']:
                    if ticket.get('status') == 'success':
                        all_times.append(ticket.get('processing_time', 0))
        
        avg_time = sum(all_times) / len(all_times) if all_times else 0
        
        # Estimate cost ($0.001 per ticket)
        total_cost = total_tickets * 0.001
        
        return {
            'total_processed': total_processed,
            'total_failed': total_failed,
            'success_rate': (total_processed / total_tickets * 100) if total_tickets > 0 else 0,
            'avg_time': avg_time,
            'total_cost': total_cost
        }
    
    def get_category_breakdown(self, days=7):
        """Get ticket category distribution"""
        df = self.get_all_tickets(days)
        if df.empty:
            return {}
        
        counts = df['category'].value_counts()
        return counts.to_dict()
    
    def get_sentiment_breakdown(self, days=7):
        """Get sentiment distribution"""
        df = self.get_all_tickets(days)
        if df.empty:
            return {}
        
        counts = df['sentiment'].value_counts()
        return counts.to_dict()
    
    def get_urgency_breakdown(self, days=7):
        """Get urgency distribution"""
        df = self.get_all_tickets(days)
        if df.empty:
            return {}
        
        counts = df['urgency'].value_counts()
        return counts.to_dict()
    
    def get_recent_tickets(self, limit=10):
        """Get most recent processed tickets"""
        df = self.get_all_tickets(days=1)
        if df.empty:
            return pd.DataFrame()
        
        # Sort by timestamp (most recent first)
        df = df.sort_values('timestamp', ascending=False)
        return df.head(limit)

def calculate_roi(tickets_per_month, hourly_rate=50):
    """Calculate ROI metrics"""
    
    # Manual processing
    manual_hours = (tickets_per_month * 5) / 60  # 5 minutes per ticket
    manual_cost = manual_hours * hourly_rate
    
    # AI processing
    ai_hours = (tickets_per_month * 3.5) / 3600  # 3.5 seconds per ticket
    ai_cost_compute = tickets_per_month * 0.001  # $0.001 per ticket
    ai_cost_managed = 1000  # Managed service fee
    ai_total_cost = ai_cost_compute + ai_cost_managed
    
    # Savings
    monthly_savings = manual_cost - ai_total_cost
    annual_savings = monthly_savings * 12
    
    # Break-even (how many months to recover setup cost)
    setup_cost = 5000  # Professional tier
    breakeven_months = setup_cost / monthly_savings if monthly_savings > 0 else 0
    
    return {
        'tickets_per_month': tickets_per_month,
        'manual_hours': round(manual_hours, 1),
        'manual_cost': round(manual_cost, 2),
        'ai_hours': round(ai_hours, 2),
        'ai_total_cost': round(ai_total_cost, 2),
        'monthly_savings': round(monthly_savings, 2),
        'annual_savings': round(annual_savings, 2),
        'breakeven_months': round(breakeven_months, 1)
    }