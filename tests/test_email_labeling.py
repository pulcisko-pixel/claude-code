"""
Testy pre Email Auto-Labeling Agent.
"""

import pytest
from models.email import Email
from models.label import Label, LabelRule, LabelCategory
from agents.email_auto_labeling.config import LabelConfig
from agents.email_auto_labeling.labeler import EmailLabeler
from agents.email_auto_labeling.utils import (
    parse_claude_response,
    extract_labels_from_response,
    merge_labels
)


class TestEmailModel:
    """Testy pre Email model."""

    def test_email_creation(self):
        email = Email(
            sender="test@example.com",
            subject="Test",
            body="Test body",
            received_at="2025-11-28T10:00:00Z"
        )
        assert email.sender == "test@example.com"
        assert email.subject == "Test"

    def test_email_preview(self):
        email = Email(
            sender="test@example.com",
            subject="Test",
            body="A" * 200,
            received_at="2025-11-28T10:00:00Z"
        )
        preview = email.get_preview(50)
        assert len(preview) <= 53  # 50 + "..."

    def test_has_attachments(self):
        email_with = Email(
            sender="test@example.com",
            subject="Test",
            body="Test",
            received_at="2025-11-28T10:00:00Z",
            attachments=["file.pdf"]
        )
        email_without = Email(
            sender="test@example.com",
            subject="Test",
            body="Test",
            received_at="2025-11-28T10:00:00Z"
        )
        assert email_with.has_attachments() is True
        assert email_without.has_attachments() is False


class TestLabelModel:
    """Testy pre Label model."""

    def test_label_creation(self):
        label = Label(
            name="Pracovné",
            confidence=0.95
        )
        assert label.name == "Pracovné"
        assert label.confidence == 0.95

    def test_label_string_representation(self):
        label = Label(name="Test", confidence=0.85)
        assert "Test" in str(label)
        assert "85%" in str(label)


class TestLabelConfig:
    """Testy pre LabelConfig."""

    def test_default_rules_exist(self):
        config = LabelConfig()
        rules = config.get_all_rules()
        assert len(rules) > 0

    def test_add_custom_rule(self):
        config = LabelConfig()
        initial_count = len(config.get_all_rules())

        custom_rule = LabelRule(
            label=LabelCategory.PRACOVNE,
            keywords=["test"],
            priority=5
        )
        config.add_custom_rule(custom_rule)

        assert len(config.get_all_rules()) == initial_count + 1

    def test_confidence_threshold(self):
        config = LabelConfig()
        config.set_confidence_threshold(0.7)
        assert config.min_confidence_threshold == 0.7

    def test_invalid_threshold_raises_error(self):
        config = LabelConfig()
        with pytest.raises(ValueError):
            config.set_confidence_threshold(1.5)


class TestEmailLabeler:
    """Testy pre EmailLabeler."""

    def test_urgent_email_labeling(self):
        config = LabelConfig()
        labeler = EmailLabeler(config)

        email = Email(
            sender="test@example.com",
            subject="URGENT: Critical issue",
            body="This is urgent!",
            received_at="2025-11-28T10:00:00Z"
        )

        labels = labeler.apply_rules(email)
        label_names = [l.name for l in labels]
        assert "Urgentné" in label_names

    def test_newsletter_labeling(self):
        config = LabelConfig()
        labeler = EmailLabeler(config)

        email = Email(
            sender="newsletter@example.com",
            subject="Weekly Newsletter",
            body="Unsubscribe here...",
            received_at="2025-11-28T10:00:00Z"
        )

        labels = labeler.apply_rules(email)
        label_names = [l.name for l in labels]
        assert "Newsletter" in label_names

    def test_work_email_labeling(self):
        config = LabelConfig()
        labeler = EmailLabeler(config)

        email = Email(
            sender="colleague@company.com",
            subject="RE: Project meeting",
            body="Let's schedule a meeting to discuss the project deadline...",
            received_at="2025-11-28T10:00:00Z"
        )

        labels = labeler.apply_rules(email)
        label_names = [l.name for l in labels]
        assert "Pracovné" in label_names or "Follow-up" in label_names

    def test_invoice_labeling(self):
        config = LabelConfig()
        labeler = EmailLabeler(config)

        email = Email(
            sender="billing@company.com",
            subject="Faktúra #12345",
            body="Príloha obsahuje faktúru za november...",
            received_at="2025-11-28T10:00:00Z"
        )

        labels = labeler.apply_rules(email)
        label_names = [l.name for l in labels]
        assert "Faktúry" in label_names

    def test_needs_ai_analysis(self):
        config = LabelConfig()
        labeler = EmailLabeler(config)

        # Žiadne štítky - potrebuje AI
        assert labeler.needs_ai_analysis([]) is True

        # Nízka istota - potrebuje AI
        low_confidence_labels = [Label(name="Test", confidence=0.5)]
        assert labeler.needs_ai_analysis(low_confidence_labels) is True

        # Vysoká istota - nepotrebuje AI
        high_confidence_labels = [Label(name="Test", confidence=0.9)]
        assert labeler.needs_ai_analysis(high_confidence_labels) is False


class TestUtils:
    """Testy pre utility funkcie."""

    def test_parse_claude_response_valid_json(self):
        response = '{"labels": [{"name": "Test", "confidence": 0.9}], "primary_label": "Test"}'
        result = parse_claude_response(response)
        assert "labels" in result
        assert "primary_label" in result

    def test_parse_claude_response_with_text(self):
        response = 'Here is the analysis: {"labels": [{"name": "Test", "confidence": 0.9}]}'
        result = parse_claude_response(response)
        assert "labels" in result

    def test_extract_labels_from_response(self):
        response_data = {
            "labels": [
                {"name": "Pracovné", "confidence": 0.95, "reason": "Work email"},
                {"name": "Urgentné", "confidence": 0.80}
            ]
        }
        labels = extract_labels_from_response(response_data)
        assert len(labels) == 2
        assert labels[0].name == "Pracovné"
        assert labels[0].confidence == 0.95

    def test_merge_labels(self):
        rule_labels = [
            Label(name="Pracovné", confidence=0.7),
            Label(name="Urgentné", confidence=0.6)
        ]
        ai_labels = [
            Label(name="Pracovné", confidence=0.9),
            Label(name="Follow-up", confidence=0.8)
        ]

        merged = merge_labels(rule_labels, ai_labels, max_labels=3)

        # Pracovné by malo mať vyššiu istotu z AI
        pracovne = next(l for l in merged if l.name == "Pracovné")
        assert pracovne.confidence == 0.9

        # Mali by byť 3 štítky
        assert len(merged) <= 3


class TestLabelRule:
    """Testy pre LabelRule."""

    def test_label_rule_creation(self):
        rule = LabelRule(
            label=LabelCategory.PRACOVNE,
            keywords=["projekt", "meeting"],
            sender_domains=["company.com"],
            priority=5
        )
        assert rule.label == LabelCategory.PRACOVNE
        assert len(rule.keywords) == 2
        assert rule.priority == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
