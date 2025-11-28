from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class Email(BaseModel):
    """Model pre reprezentáciu emailu."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sender": "boss@company.com",
                "subject": "URGENT: Project deadline tomorrow",
                "body": "We need to finish the project by tomorrow...",
                "received_at": "2025-11-28T10:00:00Z",
                "recipients": ["employee@company.com"],
                "is_reply": False
            }
        }
    )

    sender: EmailStr = Field(..., description="Email adresa odosielateľa")
    subject: str = Field(..., description="Predmet emailu")
    body: str = Field(..., description="Telo emailu")
    received_at: str = Field(..., description="Čas prijatia emailu")
    recipients: Optional[List[EmailStr]] = Field(default=None, description="Zoznam príjemcov")
    cc: Optional[List[EmailStr]] = Field(default=None, description="Zoznam CC príjemcov")
    attachments: Optional[List[str]] = Field(default=None, description="Zoznam príloh")
    is_reply: bool = Field(default=False, description="Či je email odpoveďou")
    thread_id: Optional[str] = Field(default=None, description="ID vlákna konverzácie")

    def get_preview(self, max_length: int = 100) -> str:
        """Vráti náhľad tela emailu."""
        if len(self.body) <= max_length:
            return self.body
        return self.body[:max_length] + "..."

    def has_attachments(self) -> bool:
        """Skontroluje, či email má prílohy."""
        return self.attachments is not None and len(self.attachments) > 0
