#ai_summary.py
import ollama

def summarize_mail(msg):

    try:
        body = msg.get_body_text()
        #body = body.strip()
    except Exception:
        body = msg.body_preview or ""
    prompt = f"""

    Fasse den Inhalt dieser Mail zusammen. Beachte dabei, dass es sich auch um einen E-Mail-Verlauf handeln kann,
    bei dem ältere Nachrichten mit im Body auftauchen, die nur noch für den Kontext relevant sind.
    Schreibe auch mögliche Todos auf. Achte nicht so sehr auf triviale Inhalte (z.B. Absender, Signatur oder small-talk).

    {body}
    """

    response = ollama.chat(
        model='llama3.1',
        messages=[
            {
                'role': 'system',
                'content': 'Du bist ein Assistent für Aufgabenmanagement und arbeitest für Frederick Knop, GF von Witchcraft Solutions GmbH aus Dortmund. Antworte bitte auf Deutsch.'
            },
            {'role': 'user', 'content': prompt}
        ]
    )

    return response['message']['content']
