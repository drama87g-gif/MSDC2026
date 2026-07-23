Local Print Agent Instructions
------------------------------
Purpose:
- Provide direct access to local printers (card printers) from the web app.
- Accept PDF files via HTTP and send them to a named OS printer.

Suggested Implementation:
- Small Node.js Express app or Electron app.
- Endpoint: POST /print with form-data: { file: PDF, printerName: string }
- The agent uses OS printing utilities:
  - Windows: use 'node-printer' or spawn 'print' command or use 'pdf-to-printer' package.
  - Linux: use 'lp' or 'lpr' commands.
- Security:
  - Bind to localhost only.
  - Optionally require a shared secret header.

Sample curl:
curl -X POST -F "file=@patient_1_card.pdf" -F "printerName=CardPrinter1" http://localhost:9100/print

Mapping printers:
- Admin UI can store printerName for templates (e.g., patient_card -> CardPrinter1).
- When user clicks print, frontend sends PDF to agent endpoint.

Notes:
- The agent is optional. Browser printing works for A4/A5 receipts.
- For card printers requiring special drivers, install vendor drivers on the workstation and use the agent to call the OS print API.