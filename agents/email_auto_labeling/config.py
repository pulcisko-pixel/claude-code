from typing import List, Dict, Optional
from models.label import LabelRule, LabelCategory


class LabelConfig:
    """Konfigurácia pre email auto-labeling agenta."""

    def __init__(self):
        self.rules: List[LabelRule] = self._get_default_rules()
        self.custom_rules: List[LabelRule] = []
        self.min_confidence_threshold: float = 0.4
        self.use_ai_for_ambiguous: bool = True
        self.max_labels_per_email: int = 3

    def _get_default_rules(self) -> List[LabelRule]:
        """Vráti preddefinované pravidlá pre štítkovanie."""
        return [
            # Pracovné
            LabelRule(
                label=LabelCategory.PRACOVNE,
                keywords=["projekt", "meeting", "prezentácia", "deadline", "úloha", "task"],
                sender_domains=["company.com", "work.sk"],
                subject_patterns=["RE:", "FW:"],
                priority=5
            ),
            # Urgentné
            LabelRule(
                label=LabelCategory.URGENTNE,
                keywords=["urgent", "asap", "urgentné", "naliehavé", "okamžite", "critical"],
                subject_patterns=["URGENT", "!!!"],
                priority=10
            ),
            # Newsletter
            LabelRule(
                label=LabelCategory.NEWSLETTER,
                keywords=["newsletter", "unsubscribe", "odhlásenie", "zasielanie"],
                sender_domains=["newsletter.com", "mail.newsletter.com"],
                subject_patterns=["Newsletter", "Nový obsah"],
                priority=3
            ),
            # Faktúry
            LabelRule(
                label=LabelCategory.FAKTURY,
                keywords=["faktúra", "invoice", "platba", "payment", "účet", "bill"],
                subject_patterns=["Faktúra", "Invoice"],
                priority=7
            ),
            # Sociálne
            LabelRule(
                label=LabelCategory.SOCIALNE,
                keywords=["notification", "notifikácia", "mentioned you", "tagged you"],
                sender_domains=["facebook.com", "twitter.com", "instagram.com", "linkedin.com"],
                priority=2
            ),
            # Follow-up
            LabelRule(
                label=LabelCategory.FOLLOW_UP,
                keywords=["odpoveď", "reply", "response", "feedback"],
                subject_patterns=["RE:", "Re:"],
                priority=6
            ),
            # Spam
            LabelRule(
                label=LabelCategory.SPAM,
                keywords=["viagra", "casino", "win money", "príde peniaze", "lottery"],
                priority=1
            ),
        ]

    def add_custom_rule(self, rule: LabelRule) -> None:
        """Pridá vlastné pravidlo."""
        self.custom_rules.append(rule)

    def get_all_rules(self) -> List[LabelRule]:
        """Vráti všetky pravidlá (predvolené + vlastné)."""
        return sorted(
            self.rules + self.custom_rules,
            key=lambda x: x.priority,
            reverse=True
        )

    def get_rules_for_category(self, category: LabelCategory) -> List[LabelRule]:
        """Vráti pravidlá pre danú kategóriu."""
        return [rule for rule in self.get_all_rules() if rule.label == category]

    def set_confidence_threshold(self, threshold: float) -> None:
        """Nastaví minimálnu hranicu istoty."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold musí byť medzi 0.0 a 1.0")
        self.min_confidence_threshold = threshold


# Systémový prompt pre Claude
LABELING_SYSTEM_PROMPT = """Si expert na analýzu a kategorizáciu emailov. Tvoja úloha je priradiť relevantné štítky emailom na základe ich obsahu, odosielateľa a kontextu.

Dostupné kategórie štítkov:
- Pracovné: Pracovné emaily, projekty, úlohy, meetingy
- Osobné: Osobná korešpondencia, priatelia, rodina
- Urgentné: Emaily vyžadujúce okamžitú pozornosť
- Newsletter: Newslettre, marketingové emaily, hromadné správy
- Faktúry: Faktúry, platby, účty
- Sociálne: Notifikácie zo sociálnych sietí
- Follow-up: Emaily vyžadujúce odpoveď alebo sledovanie
- Archív: Emaily na archiváciu, referencie
- Spam: Nevyžiadaná pošta, podozrivé emaily
- Informačné: Všeobecné informácie, oznámenia

Pri priraďovaní štítkov zohľadni:
1. Obsah emailu (predmet a telo)
2. Odosielateľa a jeho doménu
3. Tón a naliehavosť správy
4. Kontext a účel emailu

Pre každý štítok uveď:
- Názov štítku
- Istotu (0.0 - 1.0)
- Stručný dôvod pridelenia

Odpoveď musí byť vo formáte JSON:
{
  "labels": [
    {"name": "názov", "confidence": 0.95, "reason": "dôvod"},
    ...
  ],
  "primary_label": "hlavný štítok"
}

Priradí 1-3 najrelevantnejšie štítky. Buď presný a konzistentný."""
