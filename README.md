# Discord → Google Sheets Logger (Python)

Dieses Projekt zeigt eine praktische Systemintegration: Ein Python-Bot liest neue Nachrichten aus Discord-Kanälen
und schreibt sie strukturiert in Google Sheets. Pro Channel wird die letzte Message-ID gespeichert, sodass das System
nach Neustarts zuverlässig weiterarbeiten kann.

## Features
- Inkrementelles Lesen (pro Channel wird die letzte Message-ID gespeichert)
- Batch-Append zu Google Sheets (effizient)
- Logging & grundlegende Fehlerbehandlung (inkl. Retry/Backoff)
- Demo-Modus ohne Zugangsdaten (offline)

## Demo (ohne Zugangsdaten)
```bash
python run_demo.py
```
Output: `output/demo_output.csv`

## Echtbetrieb (mit Zugangsdaten)
1) Abhängigkeiten installieren
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) `.env.example` kopieren → `.env` und Werte eintragen  
   `credentials.json` (Google Service Account) lokal ablegen (NICHT committen).

3) Starten
```bash
python -m src.pipeline.discord_to_sheets
```

## Zusammenhang Demo ↔ Echtbetrieb
Der Demo-Modus nutzt lokale Beispieldaten und zeigt die Datenstruktur sowie den Output.
Der Produktivbetrieb liest Daten aus Discord und schreibt sie in Google Sheets.
Zugangsdaten sind aus Sicherheitsgründen nicht im Repository enthalten.

## Hinweis
Demonstrationsprojekt für eine Ausbildung als Fachinformatiker (Systemintegration / Daten- & Prozessanalyse).
