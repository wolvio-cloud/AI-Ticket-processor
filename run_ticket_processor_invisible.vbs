' AI Ticket Processor - Invisible Runner
' This VBScript runs the batch file completely invisibly (no window flash)

Set WshShell = CreateObject("WScript.Shell")

' Path to the silent batch file
BatchFile = "C:\Users\MadhanKarthickMailsa\Documents\Wolvio\DTAI\2025 Strategy\Product Roadmap - 2025\Ai ticket processor\run_ticket_processor_silent.bat"

' Run completely hidden (0 = hidden window, False = don't wait)
WshShell.Run """" & BatchFile & """", 0, False

Set WshShell = Nothing
