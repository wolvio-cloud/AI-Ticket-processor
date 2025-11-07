@echo off
REM AI Ticket Processor - Automated Runner
REM This file runs the AI ticket processor automatically

echo ========================================
echo AI TICKET PROCESSOR - AUTOMATED RUN
echo Started at: %date% %time%
echo ========================================
echo.

REM Change to the script directory
cd /d "C:\Users\MadhanKarthickMailsa\Documents\Wolvio\DTAI\2025 Strategy\Product Roadmap - 2025\Ai ticket processor"

REM Run the Python script with limit of 50 tickets
python ai_ticket_processor.py --limit 50

echo.
echo ========================================
echo Completed at: %date% %time%
echo ========================================
echo.

REM Optional: Keep window open for 5 seconds to see results
timeout /t 5 /nobreak > nul
