"""
Základné príklady použitia Email Auto-Labeling Agenta.
"""

import os
from dotenv import load_dotenv
from agents.email_auto_labeling.agent import EmailAutoLabelingAgent
from models.email import Email
from models.label import LabelRule, LabelCategory

# Načítaj premenné prostredia
load_dotenv()


def example_1_basic_labeling():
    """Príklad 1: Základné štítkovanie jedného emailu."""
    print("\n=== Príklad 1: Základné štítkovanie ===\n")

    # Inicializuj agenta
    agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Vytvor email
    email = Email(
        sender="boss@company.com",
        subject="URGENT: Project deadline tomorrow",
        body="We need to finish the project by tomorrow. Please prioritize this task.",
        received_at="2025-11-28T10:00:00Z"
    )

    # Označ email
    response = agent.label_email(email)

    # Vypíš výsledky
    print(f"Email: {email.subject}")
    print(f"Odosielateľ: {email.sender}")
    print(f"\nPriradené štítky:")
    for label in response.labels:
        print(f"  - {label.name} (istota: {label.confidence:.0%})")
    print(f"\nPrimárny štítok: {response.primary_label.name if response.primary_label else 'Žiadny'}")
    print(f"Čas spracovania: {response.processing_time:.3f}s")
    print(f"Použitá AI: {'Áno' if response.used_ai else 'Nie'}")


def example_2_batch_labeling():
    """Príklad 2: Hromadné štítkovanie viacerých emailov."""
    print("\n=== Príklad 2: Hromadné štítkovanie ===\n")

    agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Vytvor viacero emailov
    emails = [
        Email(
            sender="newsletter@techcrunch.com",
            subject="TechCrunch Daily: Latest tech news",
            body="Here are today's top stories...",
            received_at="2025-11-28T09:00:00Z"
        ),
        Email(
            sender="accounting@company.com",
            subject="Faktúra #12345",
            body="Príloha obsahuje faktúru za november...",
            received_at="2025-11-28T09:30:00Z",
            attachments=["invoice_12345.pdf"]
        ),
        Email(
            sender="friend@gmail.com",
            subject="Ahoj, ako sa máš?",
            body="Dávno sme sa nevideli, poďme niekedy na kávu...",
            received_at="2025-11-28T10:00:00Z"
        ),
    ]

    # Označ všetky emaily
    responses = agent.label_emails_batch(emails)

    # Vypíš výsledky
    for i, response in enumerate(responses, 1):
        print(f"\n{i}. {response.email.subject}")
        print(f"   Štítky: {', '.join(response.get_label_names())}")

    # Zobraz statistiky
    print("\n=== Statistiky ===")
    stats = agent.get_statistics(responses)
    print(f"Celkom emailov: {stats['total_emails']}")
    print(f"Použitá AI: {stats['used_ai']}x")
    print(f"Len pravidlá: {stats['used_rules_only']}x")
    print(f"Priemerný čas: {stats['avg_processing_time']}s")
    print(f"Priemerný počet štítkov: {stats['avg_labels_per_email']}")
    print(f"\nRozdelenie štítkov:")
    for label, count in stats['label_distribution'].items():
        print(f"  {label}: {count}x")


def example_3_custom_rules():
    """Príklad 3: Vlastné pravidlá štítkovania."""
    print("\n=== Príklad 3: Vlastné pravidlá ===\n")

    agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Pridaj vlastné pravidlo
    custom_rule = LabelRule(
        label=LabelCategory.PRACOVNE,
        keywords=["klient", "zákazník", "objednávka"],
        sender_domains=["clients.company.com"],
        priority=8
    )
    agent.add_custom_rule(custom_rule)

    # Otestuj s emailom, ktorý vyhovuje vlastnému pravidlu
    email = Email(
        sender="john@clients.company.com",
        subject="Nová objednávka od klienta",
        body="Klient John Smith vytvoril novú objednávku #789...",
        received_at="2025-11-28T11:00:00Z"
    )

    response = agent.label_email(email)

    print(f"Email: {email.subject}")
    print(f"Štítky: {', '.join(response.get_label_names())}")
    print(f"Použité vlastné pravidlo: Áno")


def example_4_force_ai():
    """Príklad 4: Vynútenie AI analýzy."""
    print("\n=== Príklad 4: AI analýza ===\n")

    agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    email = Email(
        sender="unknown@example.com",
        subject="Meeting next week",
        body="Can we schedule a meeting to discuss the project status?",
        received_at="2025-11-28T12:00:00Z"
    )

    # Bez AI (len pravidlá)
    response_rules = agent.label_email(email, force_ai=False)
    print("Bez AI:")
    print(f"  Štítky: {', '.join(response_rules.get_label_names())}")
    print(f"  Použitá AI: {response_rules.used_ai}")

    # S AI
    response_ai = agent.label_email(email, force_ai=True)
    print("\nS AI:")
    print(f"  Štítky: {', '.join(response_ai.get_label_names())}")
    print(f"  Použitá AI: {response_ai.used_ai}")


def example_5_confidence_threshold():
    """Príklad 5: Nastavenie hranice istoty."""
    print("\n=== Príklad 5: Hranica istoty ===\n")

    agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

    email = Email(
        sender="someone@example.com",
        subject="Hello",
        body="Just wanted to say hi...",
        received_at="2025-11-28T13:00:00Z"
    )

    # Nízka hranica (0.3)
    agent.set_confidence_threshold(0.3)
    response_low = agent.label_email(email)
    print(f"Nízka hranica (0.3): {len(response_low.labels)} štítkov")

    # Vysoká hranica (0.8)
    agent.set_confidence_threshold(0.8)
    response_high = agent.label_email(email)
    print(f"Vysoká hranica (0.8): {len(response_high.labels)} štítkov")


if __name__ == "__main__":
    print("=" * 60)
    print("Email Auto-Labeling Agent - Príklady použitia")
    print("=" * 60)

    # Skontroluj API kľúč
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  ANTHROPIC_API_KEY nie je nastavený!")
        print("Nastavte ho v .env súbore alebo exportujte ako premennú prostredia.")
        exit(1)

    # Spusti príklady
    try:
        example_1_basic_labeling()
        example_2_batch_labeling()
        example_3_custom_rules()
        example_4_force_ai()
        example_5_confidence_threshold()
    except Exception as e:
        print(f"\n❌ Chyba: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Hotovo!")
    print("=" * 60)
