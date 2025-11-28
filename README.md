# Email Auto-Labeling Agent

Agent pre automatické štítkovanie emailov pomocou Claude AI. Agent analyzuje obsah emailov a priraďuje im relevantné štítky podľa kontextu, odosielateľa a obsahu.

## Funkcie

- 🏷️ **Automatické štítkovanie** - Agent automaticky kategorizuje emaily
- 🤖 **AI-powered** - Využíva Claude na inteligentnú analýzu emailov
- ⚡ **Hybridný prístup** - Kombinuje pravidlá a AI pre rýchle a presné štítkovanie
- 📊 **Konfigurovateľné kategórie** - Prispôsobiteľné štítky podľa vašich potrieb

## Podporované štítky

- **Pracovné** - Pracovné emaily, projekty, úlohy
- **Osobné** - Osobná korešpondencia
- **Urgentné** - Emaily vyžadujúce okamžitú pozornosť
- **Newsletter** - Newslettre, marketingové emaily
- **Faktúry** - Faktúry a finančné dokumenty
- **Sociálne** - Notifikácie zo sociálnych sietí
- **Follow-up** - Emaily vyžadujúce odpoveď
- **Archív** - Emaily na archiváciu

## Inštalácia

```bash
# Klonujte repozitár
git clone <repository-url>
cd claude-code

# Nainštalujte závislosti
pip install -r requirements.txt

# Nastavte premenné prostredia
cp .env.example .env
# Upravte .env a pridajte váš ANTHROPIC_API_KEY
```

## Použitie

### Základné použitie

```python
from agents.email_auto_labeling.agent import EmailAutoLabelingAgent
from models.email import Email
import os

# Inicializujte agenta
agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Vytvorte email objekt
email = Email(
    sender="boss@company.com",
    subject="URGENT: Project deadline tomorrow",
    body="We need to finish the project by tomorrow...",
    received_at="2025-11-28T10:00:00Z"
)

# Automaticky označte email
labels = agent.label_email(email)
print(f"Priradené štítky: {labels}")
# Výstup: ['Pracovné', 'Urgentné', 'Follow-up']
```

### Batch spracovanie

```python
# Spracujte viacero emailov naraz
emails = [email1, email2, email3]
results = agent.label_emails_batch(emails)

for email, labels in results:
    print(f"{email.subject}: {labels}")
```

### Vlastné kategórie

```python
from agents.email_auto_labeling.config import LabelConfig

# Pridajte vlastné štítky
config = LabelConfig()
config.add_custom_label(
    name="Klienti",
    keywords=["klient", "zákazník", "objednávka"],
    priority=2
)

agent = EmailAutoLabelingAgent(config=config)
```

## Architektúra

```
agents/email_auto_labeling/
├── agent.py          # Hlavný agent s Claude integráciou
├── labeler.py        # Logika štítkovania
├── config.py         # Konfigurácia a pravidlá
└── utils.py          # Pomocné funkcie

models/
├── email.py          # Email dátové modely
├── label.py          # Label modely
└── response.py       # Response štruktúry
```

## Konfigurácia

Agent používa hybridný prístup:
1. **Rule-based matching** - Rýchle pravidlá pre jasné prípady
2. **Claude AI** - Inteligentná analýza pre nejednoznačné emaily

Pravidlá môžete upraviť v `agents/email_auto_labeling/config.py`.

## Príklady

Pozrite si `examples/basic_usage.py` pre komplexné príklady použitia.

## Licencia

MIT
