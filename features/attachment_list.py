import email
import base64
from email.header import decode_header

def list_attachments(msg):
    """Liste alle Anhänge auf."""

    # Anhänge explizit vom Server laden, falls noch nicht geschehen
    if not msg.attachments:
        msg.attachments.download_attachments()

    if not msg.has_attachments or len(msg.attachments) == 0:
        print("Keine Anhänge")
        return

    print("Anhänge:")
    for att in msg.attachments:
        if att.name.lower() == 'smime.p7m':
            print(f"  📦 S/MIME Container gefunden ({att.name})")
            
            # 1. Daten holen und Base64 korrigieren
            content = att.content
            p7m_bytes = base64.b64decode(content) if isinstance(content, str) else content
            smime_msg = email.message_from_bytes(p7m_bytes)
            
            count_displayed = 0
            count_filtered = 0
            
            # 2. Durch den Container loopen
            for part in smime_msg.walk():
                raw_filename = part.get_filename()
                if not raw_filename:
                    continue
                
                # Header dekodieren (für Sonderzeichen)
                decoded = decode_header(raw_filename)
                clean_name = "".join(
                    [str(c.decode(e or 'utf-8', errors='replace') if isinstance(c, bytes) else c) 
                     for c, e in decoded]
                )

                # Filter-Logik
                name_low = clean_name.lower()
                is_junk = any(x in name_low for x in ['image00', '.html', '.htm', 'smime.p7s'])
                
                if is_junk:
                    count_filtered += 1
                else:
                    print(f"     -> 📄 {clean_name}")
                    count_displayed += 1
            
            # 3. Status-Meldung am Ende des Containers
            if count_displayed == 0 and count_filtered == 0:
                print("     [!] Container leer oder verschlüsselt.")
            else:
                print(f"     ℹ️  Es wurden {count_filtered} Dateien gefiltert.")
        
        else:
            # Behandlung für normale Anhänge (außerhalb S/MIME)
            name_low = att.name.lower()
            if not any(x in name_low for x in ['image00', '.html']):
                print(f"  - {att.name} ({round(att.size / 1024 / 1024, 2)} MB)")
            else:
                print(f"  - (1 Datei gefiltert)")
