import json
from typing import Dict, Any, List
from models.label import Label


def parse_claude_response(response_text: str) -> Dict[str, Any]:
    """Parsuje odpoveď z Claude a extrahuje štítky."""
    try:
        # Pokus o priamy JSON parse
        data = json.loads(response_text)
        return data
    except json.JSONDecodeError:
        # Pokus o extrakciu JSON z textu
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data
            except json.JSONDecodeError:
                pass

        # Fallback: pokus o manuálne parsovanie
        return {"labels": [], "primary_label": None}


def extract_labels_from_response(response_data: Dict[str, Any]) -> List[Label]:
    """Extrahuje Label objekty z odpovede."""
    labels = []

    if "labels" in response_data and isinstance(response_data["labels"], list):
        for label_data in response_data["labels"]:
            if isinstance(label_data, dict) and "name" in label_data:
                label = Label(
                    name=label_data.get("name", "Unknown"),
                    confidence=float(label_data.get("confidence", 0.5)),
                    reason=label_data.get("reason", "AI analysis")
                )
                labels.append(label)

    return labels


def format_email_for_analysis(email) -> str:
    """Formátuje email pre analýzu Claude."""
    return f"""Email na analýzu:

Odosielateľ: {email.sender}
Predmet: {email.subject}
Čas prijatia: {email.received_at}

Obsah:
{email.body[:1000]}{"..." if len(email.body) > 1000 else ""}

{"Má prílohy: Áno" if email.has_attachments() else "Bez príloh"}
{"Je to odpoveď: Áno" if email.is_reply else "Nie je odpoveď"}
"""


def merge_labels(rule_labels: List[Label], ai_labels: List[Label], max_labels: int = 3) -> List[Label]:
    """Zlúči štítky z pravidiel a AI, odstráni duplikáty."""
    all_labels = {}

    # Pridaj štítky z pravidiel
    for label in rule_labels:
        all_labels[label.name] = label

    # Pridaj alebo aktualizuj AI štítky
    for label in ai_labels:
        if label.name in all_labels:
            # Zachovaj vyššiu istotu
            if label.confidence > all_labels[label.name].confidence:
                all_labels[label.name] = label
        else:
            all_labels[label.name] = label

    # Zober top N podľa istoty
    sorted_labels = sorted(all_labels.values(), key=lambda x: x.confidence, reverse=True)
    return sorted_labels[:max_labels]
