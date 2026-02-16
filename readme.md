# 📧 WsMailBot

**WsMailBot** ist ein intelligenter E-Mail-Agent für Microsoft 365. Er nutzt lokale Large Language Models (LLMs) via **Ollama**, um eingehende E-Mails zu klassifizieren, Zusammenfassungen zu erstellen und geschäftskritische Dokumente wie Rechnungen automatisch zu erkennen.

---

## 🚀 Features

* **Hybrid-Klassifizierung:** Kombiniert Hard-Rules (Keywords, Regex, Betreff-Analyse) mit KI-Logik für maximale Präzision.
* **Intelligente Kategorien:** * 💰 `INVOICE`: Erkennt echte Rechnungen (mit Anhang-Check).
    * 🚀 `PROJECT`: Identifiziert menschliche Kommunikation und Rückfragen.
    * ⚙️ `SYSTEM`: Filtert automatische Benachrichtigungen und Backups.
    * 📰 `NEWSLETTER`: Markiert Marketing-Mails.
* **Datenschutz:** Die Analyse erfolgt zu 100% lokal über Ollama. Keine Mail-Inhalte verlassen deine Infrastruktur.
* **O365 Integration:** Nahtlose Anbindung an Microsoft Graph API (Business Accounts).

---

## 🛠 Setup & Installation

### 1. Microsoft Entra ID (Azure) App-Registrierung
Damit der Bot auf deine Mails zugreifen kann, musst du im [Entra Portal](https://entra.microsoft.com/) eine App registrieren:
1.  **Platform:** Web
2.  **Redirect URI:** `https://login.microsoftonline.com/common/oauth2/nativeclient`
3.  **Permissions (Delegated):** `Mail.Read`, `Mail.ReadWrite`, `offline_access`
4.  **Credentials:** Erstelle ein *Client Secret* und notiere dir den **Value** (nicht die ID).

### 2. Lokale Vorbereitung
* Stelle sicher, dass [Ollama](https://ollama.ai/) installiert ist und läuft.
* Modell laden: `ollama pull llama3.1`

### 3. Installation

# Repository klonen
git clone git@github.com:WsFrederick/WsMailAgent.git
cd WsMailAgent

# Abhängigkeiten installieren
pip install -r requirements.txt

### 4. Konfiguration
Stelle sicher, dass deine Zugangsdaten in der `settings.py` (oder einer `.env`) liegen. **Wichtig:** Diese Datei niemals ins Git einchecken!

---

## 🖥 Nutzung

Starte den Bot über die Konsole. Über Flags kannst du den Lauf steuern:

# Standard-Lauf (Letzte 3 Tage, nur Analyse)
python main.py --ai

# Nur ungelesene Mails der letzten 24h mit Anhang-Check
python main.py --ai --unread-only --days 1 --attachments

# Spezifische Absender prüfen
python main.py --ai --from-mail info@mocoapp.com support@microsoft.com

### CLI-Optionen:

| Flag | Beschreibung |
| :--- | :--- |
| `--ai` | Aktiviert die KI-Klassifizierung & Summary |
| `--unread-only` | Verarbeitet nur ungelesene Nachrichten |
| `--days X` | Zeitraum der Mails in Tagen (default: 3) |
| `--attachments` | Listet Anhänge auf (Vorbereitung für Export) |
| `--mark-as-read` | Markiert Mails nach der Analyse als gelesen |

---

## 📂 Projektstruktur

* `main.py`: Einstiegspunkt und CLI-Logik.
* `core/`:
    * `mail_client.py`: Handling der O365-Verbindung und Filter-Queries.
    * `classifier.py`: Die Hybrid-Logik (Keywords + Ollama JSON API).
* `features/`:
    * `attachment_list.py`: Utility zum Auslesen von Anhängen.
* `settings.py`: Zentrale Konfiguration (nicht im Git!).

---

## 📝 Lizenz
Privates Projekt von Witchcraft Solutions GmbH.