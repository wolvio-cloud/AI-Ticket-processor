@echo off
REM AI Ticket Processor - Silent Runner (No Window)
REM This runs in the background without showing any windows

REM Change to the script directory
cd /d "C:\Users\MadhanKarthickMailsa\Documents\Wolvio\DTAI\2025 Strategy\Product Roadmap - 2025\Ai ticket processor"

REM Run Python script silently (output to log file only)
python ai_ticket_processor.py --limit 50 >> logs\automated_runs.log 2>&1

REM Exit silently
exit
