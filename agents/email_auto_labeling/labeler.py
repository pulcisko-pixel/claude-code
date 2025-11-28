from typing import List, Optional, Tuple
from models.email import Email
from models.label import Label, LabelRule, LabelCategory
from .config import LabelConfig
import re


class EmailLabeler:
    """Rule-based email labeler."""

    def __init__(self, config: LabelConfig):
        self.config = config

    def apply_rules(self, email: Email) -> List[Label]:
        """Aplikuje pravidlá na email a vráti štítky."""
        labels = []
        rules = self.config.get_all_rules()

        for rule in rules:
            score = self._calculate_rule_score(email, rule)
            if score > 0:
                confidence = min(score, 1.0)
                if confidence >= self.config.min_confidence_threshold:
                    label = Label(
                        name=rule.label.value,
                        category=rule.label,
                        confidence=confidence,
                        reason=f"Matched rule: {rule.label.value}"
                    )
                    labels.append(label)

        # Odstráň duplikáty a zober len top N
        labels = self._deduplicate_labels(labels)
        labels = sorted(labels, key=lambda x: x.confidence, reverse=True)
        return labels[:self.config.max_labels_per_email]

    def _calculate_rule_score(self, email: Email, rule: LabelRule) -> float:
        """Vypočíta skóre pre pravidlo."""
        score = 0.0
        matches = 0
        total_checks = 0

        # Check keywords
        if rule.keywords:
            total_checks += 1
            keyword_matches = self._check_keywords(email, rule.keywords, rule.require_all_keywords)
            if keyword_matches > 0:
                matches += 1
                score += 0.5 * keyword_matches

        # Check sender domain
        if rule.sender_domains:
            total_checks += 1
            if self._check_sender_domain(email, rule.sender_domains):
                matches += 1
                score += 0.4

        # Check sender email
        if rule.sender_emails:
            total_checks += 1
            if self._check_sender_email(email, rule.sender_emails):
                matches += 1
                score += 0.5

        # Check subject patterns
        if rule.subject_patterns:
            total_checks += 1
            pattern_score = self._check_subject_patterns(email, rule.subject_patterns)
            if pattern_score > 0:
                matches += 1
                score += 0.4 * pattern_score

        # Calculate final score with priority boost
        if matches > 0:
            # Base score from matches
            base_score = score
            # Priority boost (higher priority = higher score)
            priority_multiplier = 0.7 + (rule.priority / 10.0) * 0.3
            final_score = base_score * priority_multiplier
            return min(final_score, 1.0)

        return 0.0

    def _check_keywords(self, email: Email, keywords: List[str], require_all: bool) -> float:
        """Skontroluje kľúčové slová v emaile."""
        text = f"{email.subject} {email.body}".lower()
        matched = sum(1 for keyword in keywords if keyword.lower() in text)

        if require_all:
            return 1.0 if matched == len(keywords) else 0.0

        # Ak matchne aspoň jedno kľúčové slovo, vráť vyššie skóre
        # Používame logaritmickú škálu pre lepšie výsledky
        if matched == 0:
            return 0.0
        elif matched == 1:
            return 0.7  # Jedno kľúčové slovo = 70% istota
        elif matched == 2:
            return 0.85  # Dve kľúčové slová = 85% istota
        else:
            return 1.0  # Tri alebo viac = 100% istota

    def _check_sender_domain(self, email: Email, domains: List[str]) -> bool:
        """Skontroluje doménu odosielateľa."""
        sender_domain = email.sender.split('@')[-1].lower()
        return any(domain.lower() in sender_domain for domain in domains)

    def _check_sender_email(self, email: Email, emails: List[str]) -> bool:
        """Skontroluje konkrétny email odosielateľa."""
        return email.sender.lower() in [e.lower() for e in emails]

    def _check_subject_patterns(self, email: Email, patterns: List[str]) -> float:
        """Skontroluje vzory v predmete."""
        matched = 0
        for pattern in patterns:
            if re.search(re.escape(pattern), email.subject, re.IGNORECASE):
                matched += 1

        return matched / len(patterns) if patterns else 0.0

    def _deduplicate_labels(self, labels: List[Label]) -> List[Label]:
        """Odstráni duplicitné štítky."""
        seen = {}
        for label in labels:
            if label.name not in seen or label.confidence > seen[label.name].confidence:
                seen[label.name] = label

        return list(seen.values())

    def needs_ai_analysis(self, labels: List[Label]) -> bool:
        """Určí, či je potrebná AI analýza."""
        if not labels:
            return True

        # Ak je najvyššia istota nízka, použite AI
        max_confidence = max((label.confidence for label in labels), default=0.0)
        return max_confidence < 0.8
