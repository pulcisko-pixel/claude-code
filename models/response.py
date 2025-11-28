from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from .label import Label
from .email import Email


class LabelingResponse(BaseModel):
    """Odpoveď z agenta s pridelenými štítkami."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": {
                    "sender": "boss@company.com",
                    "subject": "Project update",
                    "body": "Here's the status...",
                    "received_at": "2025-11-28T10:00:00Z"
                },
                "labels": [
                    {"name": "Pracovné", "confidence": 0.95},
                    {"name": "Follow-up", "confidence": 0.80}
                ],
                "primary_label": {"name": "Pracovné", "confidence": 0.95},
                "processing_time": 0.25,
                "used_ai": True
            }
        }
    )

    email: Email = Field(..., description="Email, ktorý bol označený")
    labels: List[Label] = Field(..., description="Zoznam priradených štítkov")
    primary_label: Optional[Label] = Field(default=None, description="Primárny štítok")
    processing_time: float = Field(..., description="Čas spracovania v sekundách")
    used_ai: bool = Field(default=False, description="Či bola použitá AI analýza")

    def get_label_names(self) -> List[str]:
        """Vráti zoznam názvov štítkov."""
        return [label.name for label in self.labels]

    def has_label(self, label_name: str) -> bool:
        """Skontroluje, či email má daný štítok."""
        return any(label.name == label_name for label in self.labels)

    def get_highest_confidence_label(self) -> Optional[Label]:
        """Vráti štítok s najvyššou istotou."""
        if not self.labels:
            return None
        return max(self.labels, key=lambda x: x.confidence)
