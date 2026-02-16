#main.py
import argparse
import settings
from auth import get_account
from core.mail_client import MailClient
from core.classifier import MailClassifier
from features.ai_summary import summarize_mail
from features.attachment_list import list_attachments


def parse_args():
    parser = argparse.ArgumentParser(description="WsMailBot")

    parser.add_argument("--unread-only", action="store_true", help="Nur ungelesene Mails verarbeiten")
    parser.add_argument("--mark-as-read", action="store_true", help="Mails nach Verarbeitung als gelesen markieren")
    parser.add_argument("--days", type=int, help="Zeitraum zurück in Tagen")
    parser.add_argument("--limit", type=int, help="Maximale Anzahl Mails")
    parser.add_argument("--ai", action="store_true", help="KI-Zusammenfassung de-/aktivieren")
    parser.add_argument("--attachments", action="store_true", help="Attachments exportieren")
    parser.add_argument("--from-mail", nargs="+", required=False, help="Absender-Mail(s) zum Filtern")

    return parser.parse_args()


def main():
    args = parse_args()

    # --- Runtime Overrides nur, wenn Flags gesetzt ---
    settings.ONLY_UNREAD = args.unread_only if args.unread_only else settings.ONLY_UNREAD
    settings.MARK_AS_READ = args.mark_as_read if args.mark_as_read else settings.MARK_AS_READ
    settings.DAYS_BACK = args.days if args.days else settings.DAYS_BACK
    settings.MESSAGE_LIMIT = args.limit if args.limit else settings.MESSAGE_LIMIT
    settings.ENABLE_AI = args.ai if args.ai else settings.ENABLE_AI
    settings.ENABLE_ATTACHMENT_EXPORT = args.attachments if args.attachments else settings.ENABLE_ATTACHMENT_EXPORT
    settings.TARGET_MAILS = args.from_mail if args.from_mail else settings.TARGET_MAILS

    account = get_account()
    client = MailClient(account)

    messages = client.get_messages()

    classifier = MailClassifier(model='llama3.1') # oder dein Model Name

    if not messages:
        print("Keine Mails gefunden.")
        return

    for msg in messages:
        print(f"\n📩 FROM: {msg.sender}")
        print(f"SUBJECT: {msg.subject}")
        print(f"[Sent: {msg.sent} || Received: {msg.received}]")

        if settings.ENABLE_AI:
            print("   🤔 Analysiere...")
            analysis = classifier.classify(msg)
            
            cat = analysis.get('category', 'UNKNOWN')
            conf = analysis.get('confidence', 0)
            reason = analysis.get('reason', '')
            summary = analysis.get('summary', '') # DAS NEUE FELD
            
            icon_map = {
                'INVOICE': "💰",
                'PROJECT': "🚀",
                'NEWSLETTER': "📰",
                'SPAM': "⛔",
                'SYSTEM': "⚙️"
            }
            icon = icon_map.get(cat, "❓")

            print(f"   {icon} Kategorie: {cat} ({int(conf*100)}%)")
            print(f"   📝 Grund: {reason}")
            print(f"   📖 Summary: {summary}") # Zeigt den Inhalt kurz an

            # Logik basierend auf Entscheidung
            if cat == 'INVOICE':
                print("   -> 💾 Starte Rechnungs-Export Modul...") 
                
            elif cat == 'NEWSLETTER':
                print("   -> 🗑️ (Optional) Könnte archiviert werden.")

            # Anhänge (nicht bei Newslettern)
            if settings.ENABLE_ATTACHMENT_EXPORT and cat != 'NEWSLETTER':
                 list_attachments(msg)

        if settings.ENABLE_ATTACHMENT_EXPORT:
            list_attachments(msg)
            #export_attachments(msg)

        if settings.MARK_AS_READ:
            msg.mark_as_read()


if __name__ == "__main__":
    main()
