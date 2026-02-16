📧 MailBot v1.0: AI-gestützte ArbeitsanweisungenDieses Tutorial beschreibt, wie du Microsoft 365 Business Mails automatisiert ausliest und lokal mit Ollama analysierst, um den täglichen Mail-Wahnsinn zu bändigen.🛠 1. Microsoft Entra ID (Azure) SetupDa Business-Accounts kein einfaches Passwort-Login erlauben, müssen wir eine App registrieren.Schritt-für-Schritt Klickpfad:Portal: Öffne das Microsoft Entra ID Portal.Registrierung: Identity > Applications > App registrations > New registration.Name: WsMailBotAccount Type: Accounts in this organizational directory only.Authentifizierung (Der "Redirect" Fix):Gehe zu Authentication > + Add a platform > Web.Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclientGeheimnis (Secret):Gehe zu Certificates & secrets > + New client secret.WICHTIG: Kopiere sofort den Inhalt der Spalte Wert (Value). Die Secret ID ist nutzlos für den Code.Berechtigungen:API Permissions > Add a permission > Microsoft Graph > Delegated permissions.Aktiviere: Mail.Read und offline_access (für dauerhaften Login).Klicke auf "Grant admin consent for [Firmenname]".💻 2. Lokale InstallationStelle sicher, dass Python 3.10+ installiert ist und Ollama im Hintergrund läuft.Bash# Notwendige Libraries
pip install O365 ollama

# KI-Modell herunterladen
ollama pull llama3.1:8b
📄 3. Der Code (main.py)Dieses Snippet verbindet die MS Graph API mit deiner lokalen KI.Pythonimport ollama
from O365 import Account

# --- KONFIGURATION ---
CLIENT_ID = 'DEINE_CLIENT_ID_AUS_AZURE'
SECRET_VALUE = 'DEIN_SECRET_WERT_AUS_AZURE'
TENANT_ID = 'DEINE_MANDANTEN_ID_AUS_AZURE'
TARGET_MAIL = 'DEINE_GESUCHTE_ABSENDER_ADRESSE'

credentials = (CLIENT_ID, SECRET_VALUE)
account = Account(credentials, tenant_id=TENANT_ID)
scopes = ['https://graph.microsoft.com/Mail.Read', 'offline_access']

# --- AUTHENTIFIZIERUNG ---
if not account.is_authenticated:
    # Generiert URL -> Browser Login -> Redirect URL zurück ins Terminal kopieren
    account.authenticate(scopes=scopes)


def process_mails():
    mailbox = account.mailbox()

    # 1. Zeitraum berechnen (Heute minus 3 Tage)
    # Microsoft erwartet das Format: YYYY-MM-DDTHH:MM:SSZ
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')

    # 2. Präziser Filter für die API
    # Wir bauen den Filter dynamisch zusammen
    # Das erzeugt: (from/emailAddress/address eq 'A' or from/emailAddress/address eq 'B')
    email_filter = " or ".join([f"from/emailAddress/address eq '{email}'" for email in TARGET_MAILS])

    # Wir kombinieren Absender UND Datum. 
    # 'ge' steht für 'greater or equal' (größer oder gleich)
    # Kombiniert mit dem Datums-Filter von vorhin
    query = f"({email_filter}) and receivedDateTime ge {three_days_ago}"
    print(f"Suche Mails ab dem {three_days_ago}...")

    # 3. Abruf der Mails 
    messages_generator = mailbox.get_messages(limit=25, query=query)

    # In Liste umwandeln und lokal sortieren (Sicherheitsnetz)
    message_list = list(messages_generator)
    message_list.sort(key=lambda m: m.received, reverse=True)

    if not message_list:
        print("Keine neuen Mails im Zeitraum gefunden.")
        return

    for msg in message_list:
        print(f"\n📩 Analysiere: {msg.subject} ({msg.received.strftime('%d.%m. %H:%M')})")
        
        # Lokale KI-Analyse
        prompt = f"Extrahiere nur die Aufgaben als Liste aus dieser Mail:\n\n{msg.body_preview}"
        
        response = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': 'Du bist ein Assistent für Aufgabenmanagement. Antworte kurz auf Deutsch.'},
            {'role': 'user', 'content': prompt}
        ])
        
        print(f"🤖 KI-Zusammenfassung:\n{response['message']['content']}")

if __name__ == "__main__":
    process_mails()

    
⚠️ 4. Troubleshooting & Snippet-WissenFehlerUrsacheLösungAADSTS7000215Falsches SecretDu hast die Secret ID statt des Values genutzt.AADSTS700025Plattform-MixApp ist als "Public" (Desktop) statt "Web" markiert.Error 400 (Bad Request)Filter-SyntaxDie API braucht eq und einfache Anführungszeichen '.Token ExpiredKein RefreshStelle sicher, dass offline_access in den Scopes steht.