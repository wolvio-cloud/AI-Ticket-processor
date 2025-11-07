"""
Multi-Industry Test Runner
Tests the updated processor against known test data
Validates industry detection and category accuracy
"""
import json
import sys
import time
from datetime import datetime

# Import the processor functions (adjust path as needed)
try:
    from Ai_ticket_processor import detect_industry, analyze_with_openai, redactor
    print("✅ Successfully imported processor functions")
except ImportError:
    print("❌ Could not import processor. Make sure Ai_ticket_processor.py is in same directory")
    sys.exit(1)

def load_test_data(filename):
    """Load test tickets from JSON"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data['tickets']
    except FileNotFoundError:
        print(f"❌ Error: Test file '{filename}' not found")
        print("💡 Run: python generate_multi_industry_test_data.py first")
        sys.exit(1)

def test_single_ticket(ticket):
    """Test a single ticket and compare results"""
    description = ticket['description']
    expected_industry = ticket['expected_industry']
    expected_category = ticket['expected_category']
    
    # Detect industry
    detected_industry = detect_industry(description)
    
    # Analyze (this calls OpenAI - costs $0.001 per ticket)
    result = analyze_with_openai(description)
    
    if not result['success']:
        return {
            'ticket_id': ticket['id'],
            'success': False,
            'error': result.get('error', 'Unknown'),
            'expected_industry': expected_industry,
            'expected_category': expected_category
        }
    
    detected_category = result['analysis']['root_cause']
    detected_industry_from_analysis = result.get('industry', 'unknown')
    
    # Check accuracy
    industry_match = (detected_industry_from_analysis == expected_industry)
    
    # For "general" expected, we accept any category since it's a catch-all
    if expected_industry == 'general':
        category_match = True  # Any category is acceptable for general
    else:
        category_match = (detected_category == expected_category)
    
    return {
        'ticket_id': ticket['id'],
        'success': True,
        'description': description[:100],
        'expected_industry': expected_industry,
        'detected_industry': detected_industry_from_analysis,
        'industry_match': industry_match,
        'expected_category': expected_category,
        'detected_category': detected_category,
        'category_match': category_match,
        'pii_protected': result.get('pii_protected', False),
        'processing_time': result['processing_time']
    }

def run_tests(tickets, max_tickets=None):
    """Run tests on all tickets"""
    if max_tickets:
        tickets = tickets[:max_tickets]
    
    print(f"\n🧪 Running tests on {len(tickets)} tickets...")
    print("="*80)
    print("⚠️ Note: This will call OpenAI API and cost ~$0.001 per ticket")
    print(f"   Total cost: ~${len(tickets) * 0.001:.2f}")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\n🚀 Processing tickets...\n")
    
    results = []
    start_time = time.time()
    
    for i, ticket in enumerate(tickets, 1):
        print(f"[{i}/{len(tickets)}] Testing ticket #{ticket['id']}...", end=" ")
        
        result = test_single_ticket(ticket)
        results.append(result)
        
        if result['success']:
            status = "✅" if (result['industry_match'] and result['category_match']) else "⚠️"
            print(f"{status} {result['detected_industry']} → {result['detected_category']}")
        else:
            print(f"❌ ERROR: {result.get('error', 'Unknown')}")
        
        # Rate limiting - be nice to API
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    return results, total_time

def analyze_results(results):
    """Analyze test results and generate report"""
    total = len(results)
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    # Industry accuracy
    industry_correct = [r for r in successful if r['industry_match']]
    industry_accuracy = len(industry_correct) / len(successful) * 100 if successful else 0
    
    # Category accuracy
    category_correct = [r for r in successful if r['category_match']]
    category_accuracy = len(category_correct) / len(successful) * 100 if successful else 0
    
    # Overall accuracy (both industry and category correct)
    both_correct = [r for r in successful if r['industry_match'] and r['category_match']]
    overall_accuracy = len(both_correct) / len(successful) * 100 if successful else 0
    
    # Industry breakdown
    industry_breakdown = {}
    for r in successful:
        ind = r['detected_industry']
        industry_breakdown[ind] = industry_breakdown.get(ind, 0) + 1
    
    # Category breakdown
    category_breakdown = {}
    for r in successful:
        cat = r['detected_category']
        category_breakdown[cat] = category_breakdown.get(cat, 0) + 1
    
    # "General" rate
    general_count = category_breakdown.get('general', 0)
    general_rate = general_count / len(successful) * 100 if successful else 0
    
    # PII protection
    pii_protected_count = sum(1 for r in successful if r.get('pii_protected', False))
    
    return {
        'total': total,
        'successful': len(successful),
        'failed': len(failed),
        'industry_accuracy': industry_accuracy,
        'category_accuracy': category_accuracy,
        'overall_accuracy': overall_accuracy,
        'industry_breakdown': industry_breakdown,
        'category_breakdown': category_breakdown,
        'general_rate': general_rate,
        'general_count': general_count,
        'pii_protected_count': pii_protected_count,
        'failed_tickets': failed
    }

def print_report(analysis, total_time):
    """Print detailed test report"""
    print("\n" + "="*80)
    print("TEST RESULTS REPORT")
    print("="*80)
    
    print(f"\n📊 OVERALL STATISTICS")
    print("-"*80)
    print(f"Total Tickets Tested:    {analysis['total']}")
    print(f"Successfully Processed:  {analysis['successful']}")
    print(f"Failed:                  {analysis['failed']}")
    print(f"Processing Time:         {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Avg Time per Ticket:     {total_time/analysis['total']:.2f}s")
    
    print(f"\n🎯 ACCURACY METRICS")
    print("-"*80)
    print(f"Industry Detection:      {analysis['industry_accuracy']:.1f}%")
    print(f"Category Classification: {analysis['category_accuracy']:.1f}%")
    print(f"Overall Accuracy:        {analysis['overall_accuracy']:.1f}%")
    
    # Accuracy rating
    if analysis['overall_accuracy'] >= 85:
        rating = "✅ EXCELLENT"
    elif analysis['overall_accuracy'] >= 75:
        rating = "✓ GOOD"
    elif analysis['overall_accuracy'] >= 60:
        rating = "⚠️ NEEDS IMPROVEMENT"
    else:
        rating = "❌ POOR"
    print(f"Rating: {rating}")
    
    print(f"\n🏭 INDUSTRY BREAKDOWN")
    print("-"*80)
    for industry, count in sorted(analysis['industry_breakdown'].items(), key=lambda x: x[1], reverse=True):
        pct = count / analysis['successful'] * 100
        print(f"{industry:15s}: {count:4d} tickets ({pct:5.1f}%)")
    
    print(f"\n📁 CATEGORY BREAKDOWN (Top 15)")
    print("-"*80)
    sorted_categories = sorted(analysis['category_breakdown'].items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories[:15]:
        pct = count / analysis['successful'] * 100
        emoji = "⚠️" if category == 'general' else "✅"
        print(f"{emoji} {category:25s}: {count:4d} tickets ({pct:5.1f}%)")
    
    print(f"\n🎯 'GENERAL' CATEGORY ANALYSIS")
    print("-"*80)
    print(f"General Classifications:  {analysis['general_count']}/{analysis['successful']} tickets ({analysis['general_rate']:.1f}%)")
    
    if analysis['general_rate'] < 15:
        status = "✅ EXCELLENT - Under 15% target"
    elif analysis['general_rate'] < 25:
        status = "✓ GOOD - Under 25% threshold"
    elif analysis['general_rate'] < 40:
        status = "⚠️ NEEDS IMPROVEMENT - Above 25%"
    else:
        status = "❌ POOR - Too many 'general' classifications"
    
    print(f"Status: {status}")
    print(f"Target: <15% (Excellent), <25% (Good)")
    
    print(f"\n🔒 PII PROTECTION")
    print("-"*80)
    print(f"Tickets with PII:        {analysis['pii_protected_count']}")
    print(f"PII Protected:           {'✅ YES' if analysis['pii_protected_count'] > 0 else 'No PII detected'}")
    
    if analysis['failed'] > 0:
        print(f"\n❌ FAILED TICKETS")
        print("-"*80)
        for failed in analysis['failed_tickets']:
            print(f"Ticket #{failed['ticket_id']}: {failed.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if analysis['overall_accuracy'] >= 85 and analysis['general_rate'] < 15:
        print("✅ PASSED - System is production-ready!")
        print("   - High accuracy (>85%)")
        print("   - Low 'general' rate (<15%)")
        print("   - Ready for customer demos")
    elif analysis['overall_accuracy'] >= 75 and analysis['general_rate'] < 25:
        print("✓ ACCEPTABLE - System is ready with minor limitations")
        print("   - Good accuracy (>75%)")
        print("   - Acceptable 'general' rate (<25%)")
        print("   - Can start pilots with caveat")
    else:
        print("⚠️ NEEDS WORK - System needs improvement")
        print("   - Accuracy too low or 'general' rate too high")
        print("   - Review prompts and detection logic")
        print("   - Test again after improvements")
    
    print("="*80)

def save_report(analysis, results, filename):
    """Save detailed report to JSON"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tickets': analysis['total'],
            'successful': analysis['successful'],
            'failed': analysis['failed'],
            'industry_accuracy': analysis['industry_accuracy'],
            'category_accuracy': analysis['category_accuracy'],
            'overall_accuracy': analysis['overall_accuracy'],
            'general_rate': analysis['general_rate']
        },
        'industry_breakdown': analysis['industry_breakdown'],
        'category_breakdown': analysis['category_breakdown'],
        'pii_protection': {
            'tickets_protected': analysis['pii_protected_count']
        },
        'detailed_results': results
    }
    
    output_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {output_filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_multi_industry_processor.py <test_data_file.json> [max_tickets]")
        print("\nExample:")
        print("  python test_multi_industry_processor.py test_tickets_multi_industry.json")
        print("  python test_multi_industry_processor.py test_tickets_multi_industry.json 50")
        sys.exit(1)
    
    test_file = sys.argv[1]
    max_tickets = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print("="*80)
    print("MULTI-INDUSTRY PROCESSOR TEST")
    print("="*80)
    
    # Load test data
    print(f"\n📂 Loading test data from: {test_file}")
    tickets = load_test_data(test_file)
    print(f"✅ Loaded {len(tickets)} tickets")
    
    if max_tickets:
        print(f"⚠️ Testing only first {max_tickets} tickets (use full dataset for final validation)")
    
    # Run tests
    results, total_time = run_tests(tickets, max_tickets)
    
    # Analyze results
    print("\n📊 Analyzing results...")
    analysis = analyze_results(results)
    
    # Print report
    print_report(analysis, total_time)
    
    # Save report
    save_report(analysis, results, test_file)
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
