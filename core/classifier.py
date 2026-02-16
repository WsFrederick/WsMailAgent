#classifier.py
import ollama
import json
import re

class MailClassifier:
    def __init__(self, model='llama3.1'):
        self.model = model

    def _clean_body(self, body_text):
        text = " ".join(body_text.split())
        return text[:2000]

    def classify(self, msg):
        try:
            subject = msg.subject if msg.subject else "Kein Betreff"
            sender = msg.sender.address if msg.sender else "Unknown"
            body = self._clean_body(msg.get_body_text() if hasattr(msg, 'get_body_text') else msg.body_preview)
            
            # 1. Hard Rules Scoring
            invoice_score = 0
            sub_low = subject.lower()
            is_reply = any(sub_low.startswith(pre) for pre in ['re:', 'aw:', 'fw:', 'wg:', 'antw:'])
            
            if any(x in sub_low for x in ['rechnung', 'invoice', 'beleg', 'quittung']):
                invoice_score += 70
            if is_reply:
                invoice_score -= 40

            # 2. Erweiterte KI Analyse
            prompt = f"""
            Analysiere diese Mail und gib NUR JSON zurück.
            Betreff: {subject}
            Absender: {sender}
            Inhalt: {body}
            Anhang: {msg.has_attachments}

            Kategorien-Definition:
            - INVOICE: Rechnungen, Quittungen, Belege (nur Dokumente!).
            - SYSTEM: Automatische Benachrichtigungen (Backups, Admin-Mails, Account-Updates, Alerts).
            - NEWSLETTER: Marketing, Werbung, regelmäßige Info-Mails.
            - PROJECT: Kommunikation mit Menschen (Kunden, Partner) zu Projekten.

            Format:
            {{
                "category": "KATEGORIE",
                "summary": "Ein Satz Zusammenfassung des Inhalts",
                "intent": "Was ist die konkrete Absicht?",
                "is_discussion": true/false
            }}
            """

            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0}
            )

            ai_res = json.loads(response['message']['content'])
            
            # --- FUSION LOGIK ---
            ai_cat = ai_res.get('category', 'UNKNOWN').upper()
            ai_summary = ai_res.get('summary', 'Keine Zusammenfassung')
            
            final_category = ai_cat
            final_reason = f"KI-Check: {ai_res.get('intent')}" # Standard-Grund

            # Korrektur-Logik
            if invoice_score > 50:
                if ai_res.get('is_discussion') or not msg.has_attachments:
                    final_category = "PROJECT"
                    final_reason = "Betreff erwähnt Rechnung, aber Inhalt ist Rückfrage/Diskussion."
                else:
                    final_category = "INVOICE"
                    final_reason = "Eindeutige Rechnung (Keyword + KI Match)."
            
            # Spezieller Check für System-Mails (z.B. Microsoft-Abo)
            if "microsoft" in sender.lower() and "abonn" in subject.lower():
                final_category = "SYSTEM"
                final_reason = "Administratives Account-Update von Microsoft."

            return {
                "category": final_category,
                "confidence": 0.9,
                "reason": final_reason,
                "summary": ai_summary
            }

        except Exception as e:
            return {"category": "ERROR", "confidence": 0, "reason": f"Fehler: {str(e)}", "summary": ""}