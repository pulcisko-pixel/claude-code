import time
from typing import List, Optional, Tuple
from anthropic import Anthropic
from models.email import Email
from models.label import Label
from models.response import LabelingResponse
from .config import LabelConfig, LABELING_SYSTEM_PROMPT
from .labeler import EmailLabeler
from .utils import (
    parse_claude_response,
    extract_labels_from_response,
    format_email_for_analysis,
    merge_labels
)


class EmailAutoLabelingAgent:
    """Agent pre automatické štítkovanie emailov pomocou Claude AI."""

    def __init__(
        self,
        api_key: str,
        config: Optional[LabelConfig] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Inicializuje agenta.

        Args:
            api_key: Anthropic API kľúč
            config: Konfigurácia pravidiel (voliteľné)
            model: Claude model na použitie
        """
        self.client = Anthropic(api_key=api_key)
        self.config = config or LabelConfig()
        self.model = model
        self.labeler = EmailLabeler(self.config)

    def label_email(self, email: Email, force_ai: bool = False) -> LabelingResponse:
        """
        Označí email štítkami.

        Args:
            email: Email na označenie
            force_ai: Vynútiť použitie AI aj pri vysokej istote z pravidiel

        Returns:
            LabelingResponse s pridelenými štítkami
        """
        start_time = time.time()
        used_ai = False

        # 1. Aplikuj pravidlá
        rule_labels = self.labeler.apply_rules(email)

        # 2. Rozhodnutie o použití AI
        needs_ai = force_ai or self.labeler.needs_ai_analysis(rule_labels)

        if needs_ai and self.config.use_ai_for_ambiguous:
            # 3. Použij Claude pre analýzu
            ai_labels = self._analyze_with_claude(email)
            used_ai = True

            # 4. Zlúč štítky
            final_labels = merge_labels(
                rule_labels,
                ai_labels,
                self.config.max_labels_per_email
            )
        else:
            final_labels = rule_labels

        # 5. Určiť primárny štítok
        primary_label = final_labels[0] if final_labels else None

        processing_time = time.time() - start_time

        return LabelingResponse(
            email=email,
            labels=final_labels,
            primary_label=primary_label,
            processing_time=processing_time,
            used_ai=used_ai
        )

    def label_emails_batch(
        self,
        emails: List[Email],
        force_ai: bool = False
    ) -> List[LabelingResponse]:
        """
        Označí viacero emailov naraz.

        Args:
            emails: Zoznam emailov
            force_ai: Vynútiť AI pre všetky emaily

        Returns:
            Zoznam LabelingResponse objektov
        """
        results = []
        for email in emails:
            try:
                response = self.label_email(email, force_ai=force_ai)
                results.append(response)
            except Exception as e:
                # V prípade chyby pridaj prázdnu odpoveď
                results.append(LabelingResponse(
                    email=email,
                    labels=[],
                    primary_label=None,
                    processing_time=0.0,
                    used_ai=False
                ))

        return results

    def _analyze_with_claude(self, email: Email) -> List[Label]:
        """
        Analyzuje email pomocou Claude AI.

        Args:
            email: Email na analýzu

        Returns:
            Zoznam štítkov z AI analýzy
        """
        try:
            # Formátuj email pre analýzu
            email_text = format_email_for_analysis(email)

            # Vytvor správu pre Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=LABELING_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": email_text
                    }
                ]
            )

            # Extrahuj odpoveď
            response_text = message.content[0].text

            # Parsuj odpoveď
            response_data = parse_claude_response(response_text)
            labels = extract_labels_from_response(response_data)

            return labels

        except Exception as e:
            print(f"Chyba pri AI analýze: {e}")
            return []

    def get_statistics(self, responses: List[LabelingResponse]) -> dict:
        """
        Vráti statistiky o označovaní.

        Args:
            responses: Zoznam LabelingResponse objektov

        Returns:
            Slovník so statistikami
        """
        total = len(responses)
        used_ai = sum(1 for r in responses if r.used_ai)
        avg_time = sum(r.processing_time for r in responses) / total if total > 0 else 0
        avg_labels = sum(len(r.labels) for r in responses) / total if total > 0 else 0

        # Počet štítkov podľa kategórie
        label_counts = {}
        for response in responses:
            for label in response.labels:
                label_counts[label.name] = label_counts.get(label.name, 0) + 1

        return {
            "total_emails": total,
            "used_ai": used_ai,
            "used_rules_only": total - used_ai,
            "avg_processing_time": round(avg_time, 3),
            "avg_labels_per_email": round(avg_labels, 2),
            "label_distribution": label_counts
        }

    def add_custom_rule(self, rule) -> None:
        """
        Pridá vlastné pravidlo.

        Args:
            rule: LabelRule objekt
        """
        self.config.add_custom_rule(rule)

    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Nastaví minimálnu hranicu istoty.

        Args:
            threshold: Nová hranica (0.0 - 1.0)
        """
        self.config.set_confidence_threshold(threshold)
