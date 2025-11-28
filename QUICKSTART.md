# 🚀 Quick Start Guide

## Krok 1: Nastavenie API kľúča

```bash
# Skopírujte .env.example do .env
cp .env.example .env

# Otvorte .env a pridajte váš Anthropic API kľúč
# ANTHROPIC_API_KEY=sk-ant-...
```

Získať API kľúč: https://console.anthropic.com/

## Krok 2: Inštalácia

```bash
# Nainštalujte závislosti
pip install -r requirements.txt

# (Voliteľné) Pre development
pip install -r requirements-dev.txt
```

## Krok 3: Spustite Demo

```bash
# Rýchle demo s ukážkovými emailmi
python demo.py
```

## Krok 4: Vyskúšajte príklady

```bash
# Komplexné príklady použitia
python examples/basic_usage.py
```

## 📋 Základné použitie v kóde

```python
from agents import EmailAutoLabelingAgent
from models import Email
import os

# Vytvorte agenta
agent = EmailAutoLabelingAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Vytvorte email
email = Email(
    sender="someone@example.com",
    subject="Meeting tomorrow",
    body="Let's meet at 10am to discuss the project",
    received_at="2025-11-28T10:00:00Z"
)

# Automaticky označte
response = agent.label_email(email)

# Výsledky
print(f"Štítky: {response.get_label_names()}")
print(f"Primárny štítok: {response.primary_label.name}")
print(f"Použitá AI: {response.used_ai}")
```

## 🎨 Prispôsobenie

### Pridanie vlastného pravidla

```python
from models.label import LabelRule, LabelCategory

# Vytvorte vlastné pravidlo
custom_rule = LabelRule(
    label=LabelCategory.PRACOVNE,
    keywords=["klient", "zákazník", "objednávka"],
    sender_domains=["clients.company.com"],
    priority=8
)

# Pridajte do agenta
agent.add_custom_rule(custom_rule)
```

### Zmena confidence thresholdu

```python
# Nižší threshold = viac štítkov (menej prísny)
agent.set_confidence_threshold(0.3)

# Vyšší threshold = menej štítkov (prísnejší)
agent.set_confidence_threshold(0.7)
```

## 🔌 Integrácie

### Gmail
```bash
# Pozrite si examples/gmail_integration.py
# Vyžaduje Gmail API setup
```

### Vlastný email klient
```python
# Načítajte emaily z vášho zdroja
your_emails = fetch_from_your_source()

# Konvertujte na Email objekty
from models import Email

emails = [
    Email(
        sender=e.from_address,
        subject=e.subject,
        body=e.body,
        received_at=e.date.isoformat()
    )
    for e in your_emails
]

# Spracujte batch
results = agent.label_emails_batch(emails)
```

## 🧪 Testovanie

```bash
# Spustite všetky testy
pytest tests/ -v

# Spustite konkrétny test
pytest tests/test_email_labeling.py::TestEmailLabeler -v

# S pokrytím
pytest tests/ --cov=agents --cov=models
```

## 📊 Podporované štítky

1. **Pracovné** - Pracovné emaily, projekty, meetingy
2. **Osobné** - Osobná korešpondencia
3. **Urgentné** - Vyžadujú okamžitú pozornosť
4. **Newsletter** - Marketingové emaily, newslettre
5. **Faktúry** - Faktúry a platby
6. **Sociálne** - Notifikácie zo sociálnych sietí
7. **Follow-up** - Vyžadujú odpoveď
8. **Archív** - Na archiváciu
9. **Spam** - Nevyžiadaná pošta
10. **Informačné** - Všeobecné oznámenia

## 🎯 Použitie v produkcii

### 1. Cronjob (Linux/Mac)
```bash
# Spustite každú hodinu
0 * * * * cd /path/to/claude-code && python your_script.py >> /var/log/email-labeling.log 2>&1
```

### 2. Systemd Service (Linux)
```ini
# /etc/systemd/system/email-labeling.service
[Unit]
Description=Email Auto-Labeling Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/claude-code
ExecStart=/usr/bin/python3 your_script.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "your_script.py"]
```

## 💡 Tipy

1. **Performance**: Batch spracovanie je rýchlejšie pre viacero emailov
2. **Náklady**: Rule-based matching je zadarmo, AI analýza spotrebúva API tokeny
3. **Prispôsobenie**: Upravte pravidlá v `agents/email_auto_labeling/config.py`
4. **Threshold**: Nižší = viac štítkov, vyšší = prísnejšie štítkovanie

## 🆘 Pomoc

- **Problémy?** Skontrolujte logs a error messages
- **API chyby?** Overte API kľúč a kredit v Anthropic konzole
- **Nesprávne štítky?** Upravte pravidlá alebo threshold
- **Otázky?** Pozrite si examples/ a tests/ pre viac príkladov

## 📚 Ďalšie zdroje

- README.md - Kompletná dokumentácia
- examples/ - Príklady použitia
- tests/ - Unit testy ako príklady
