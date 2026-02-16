#mail_client.py
from datetime import datetime, timedelta
import settings

class MailClient:

    def __init__(self, account):
        self.mailbox = account.mailbox().inbox_folder()

    def build_query(self):
        # Basis: Zeit-Filter
        date_filter = (datetime.now() - timedelta(days=settings.DAYS_BACK)) \
            .strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Liste der Query-Teile
        query_parts = [f"receivedDateTime ge {date_filter}"]

        # Optional: Absender-Filter
        if settings.TARGET_MAILS and len(settings.TARGET_MAILS) > 0:
            email_or_parts = [
                f"from/emailAddress/address eq '{email}'"
                for email in settings.TARGET_MAILS
            ]
            # Wichtig: Klammern um die OR-Verknüpfung!
            query_parts.append(f"({' or '.join(email_or_parts)})")

        # Optional: Ungelesen-Filter
        if settings.ONLY_UNREAD:
            query_parts.append("isRead eq false")

        # Alles mit AND verknüpfen
        full_query = " and ".join(query_parts)
        return full_query

    def get_messages(self):
        query = self.build_query()
        # Debugging: Zeigt dir, was wir an Microsoft senden
        # print(f"DEBUG Query: {query}") 

        messages = self.mailbox.get_messages(
            limit=settings.MESSAGE_LIMIT,
            download_attachments=settings.ENABLE_ATTACHMENT_EXPORT,
            query=query
        )

        message_list = list(messages)
        message_list.sort(key=lambda m: m.received, reverse=True)

        return message_list
