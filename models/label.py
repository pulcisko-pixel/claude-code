from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


class LabelCategory(str, Enum):
    """Preddefinované kategórie štítkov."""

    PRACOVNE = "Pracovné"
    OSOBNE = "Osobné"
    URGENTNE = "Urgentné"
    NEWSLETTER = "Newsletter"
    FAKTURY = "Faktúry"
    SOCIALNE = "Sociálne"
    FOLLOW_UP = "Follow-up"
    ARCHIV = "Archív"
    SPAM = "Spam"
    INFORMACNE = "Informačné"


class Label(BaseModel):
    """Model pre štítok/label."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Pracovné",
                "category": "Pracovné",
                "confidence": 0.95,
                "reason": "Email od šéfa o pracovnom projekte"
            }
        }
    )

    name: str = Field(..., description="Názov štítku")
    category: Optional[LabelCategory] = Field(default=None, description="Kategória štítku")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Miera istoty (0-1)")
    reason: Optional[str] = Field(default=None, description="Dôvod pridelenia štítku")

    def __str__(self) -> str:
        return f"{self.name} ({self.confidence:.0%})"

    def __repr__(self) -> str:
        return f"Label(name='{self.name}', confidence={self.confidence})"


class LabelRule(BaseModel):
    """Pravidlo pre automatické pridelenie štítku."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "Pracovné",
                "keywords": ["projekt", "meeting", "deadline"],
                "sender_domains": ["company.com"],
                "priority": 5
            }
        }
    )

    label: LabelCategory
    keywords: List[str] = Field(default_factory=list, description="Kľúčové slová")
    sender_domains: List[str] = Field(default_factory=list, description="Domény odosielateľov")
    sender_emails: List[str] = Field(default_factory=list, description="Konkrétne emaily odosielateľov")
    subject_patterns: List[str] = Field(default_factory=list, description="Vzory v predmete")
    priority: int = Field(default=1, ge=1, le=10, description="Priorita pravidla (1-10)")
    require_all_keywords: bool = Field(default=False, description="Vyžadovať všetky kľúčové slová")
