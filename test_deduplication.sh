#!/bin/bash

# Test Deduplication Fix
# This script tests that the deduplication fix is working correctly

echo "=========================================="
echo "DEDUPLICATION FIX - TEST SCRIPT"
echo "=========================================="
echo ""

echo "Test 1: Process 10 tickets (first run)"
echo "Expected: All 10 tickets processed"
echo "===================="
python Ai_ticket_processor.py --limit 10
echo ""

echo "Press Enter to continue to Test 2..."
read

echo "Test 2: Process same 10 tickets again (second run)"
echo "Expected: 0 unprocessed tickets found OR all 10 skipped"
echo "===================="
python Ai_ticket_processor.py --limit 10
echo ""

echo "Press Enter to continue to Test 3..."
read

echo "Test 3: Force reprocess (with --force flag)"
echo "Expected: All 10 tickets reprocessed, tags updated, NO duplicate comments"
echo "===================="
python Ai_ticket_processor.py --limit 10 --force
echo ""

echo "Press Enter to continue to Test 4..."
read

echo "Test 4: Process with --all flag"
echo "Expected: Fetches all tickets but skips already processed ones"
echo "===================="
python Ai_ticket_processor.py --limit 20 --all
echo ""

echo "=========================================="
echo "TESTS COMPLETE!"
echo "=========================================="
echo ""
echo "Verification checklist:"
echo "  ✓ Test 1: All tickets processed with new comments"
echo "  ✓ Test 2: No tickets processed (or message: 'No unprocessed tickets found')"
echo "  ✓ Test 3: Tickets reprocessed, tags updated, NO new duplicate comments"
echo "  ✓ Test 4: Already processed tickets skipped"
echo ""
echo "Check Zendesk UI to verify:"
echo "  ✓ Each ticket has only ONE AI analysis comment"
echo "  ✓ Tags are updated correctly"
echo "  ✓ No duplicate comments exist"
