#!/usr/bin/env python3
"""
Demo skript pre Email Auto-Labeling Agent
Spustite: python demo.py
"""

import os
from dotenv import load_dotenv
from agents.email_auto_labeling.agent import EmailAutoLabelingAgent
from models.email import Email

# Načítaj environment variables
load_dotenv()

def demo():
    """Demonštrácia agenta s ukážkovými emailmi."""

    print("=" * 60)
    print("📧 Email Auto-Labeling Agent - Demo")
    print("=" * 60)

    # Skontroluj API kľúč
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY nie je nastavený!")
        print("Nastavte ho v .env súbore:\n")
        print("1. cp .env.example .env")
        print("2. Upravte .env a pridajte váš API kľúč")
        return

    # Inicializuj agenta
    print("\n🤖 Inicializujem agenta...")
    agent = EmailAutoLabelingAgent(api_key=api_key)
    print("✅ Agent pripravený!\n")

    # Ukážkové emaily
    demo_emails = [
        Email(
            sender="boss@company.com",
            subject="URGENT: Project deadline tomorrow",
            body="We need to finish the project by tomorrow. Please prioritize this task.",
            received_at="2025-11-28T10:00:00Z"
        ),
        Email(
            sender="newsletter@techcrunch.com",
            subject="TechCrunch Daily: Latest tech news",
            body="Here are today's top stories... Unsubscribe here if you want.",
            received_at="2025-11-28T09:00:00Z"
        ),
        Email(
            sender="accounting@company.com",
            subject="Faktúra #12345",
            body="V prílohe nájdete faktúru za november. Prosím zaplaťte do 30 dní.",
            received_at="2025-11-28T11:00:00Z"
        ),
        Email(
            sender="friend@gmail.com",
            subject="Ahoj, ako sa máš?",
            body="Dávno sme sa nevideli, poďme niekedy na kávu!",
            received_at="2025-11-28T12:00:00Z"
        ),
    ]

    print("📨 Štítkujem emaily...\n")

    # Spracuj každý email
    for i, email in enumerate(demo_emails, 1):
        print(f"{i}. Email od: {email.sender}")
        print(f"   Predmet: {email.subject}")

        # Označ email
        response = agent.label_email(email)

        # Vypíš výsledky
        if response.labels:
            print(f"   🏷️  Štítky: {', '.join(response.get_label_names())}")
            print(f"   ⭐ Primárny: {response.primary_label.name if response.primary_label else 'N/A'}")
            print(f"   {'🤖' if response.used_ai else '📋'} Použitá AI: {'Áno' if response.used_ai else 'Nie (len pravidlá)'}")
            print(f"   ⚡ Čas: {response.processing_time:.3f}s")
        else:
            print("   ⚠️  Žiadne štítky")
        print()

    print("=" * 60)
    print("✅ Demo dokončené!")
    print("=" * 60)
    print("\n💡 Ďalšie kroky:")
    print("   - Upravte pravidlá v agents/email_auto_labeling/config.py")
    print("   - Pozrite si príklady v examples/basic_usage.py")
    print("   - Integrujte s vašim email klientom (Gmail, Outlook, atď.)")
    print()

if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n👋 Ukončené používateľom")
    except Exception as e:
        print(f"\n❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
