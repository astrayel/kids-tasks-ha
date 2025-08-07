# ============================================================================
# models.py
# ============================================================================

"""Data models for Kids Tasks integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .const import TASK_STATUS_TODO, FREQUENCY_DAILY


@dataclass
class Child:
    """Represents a child."""
    id: str
    name: str
    points: int = 0
    level: int = 1
    avatar: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        return (self.level * 100) - self.points
    
    def add_points(self, points: int) -> bool:
        """Add points and check for level up."""
        old_level = self.level
        self.points += points
        self.level = max(1, (self.points // 100) + 1)
        return self.level > old_level
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "points": self.points,
            "level": self.level,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Child:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            points=data.get("points", 0),
            level=data.get("level", 1),
            avatar=data.get("avatar"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )


@dataclass
class Task:
    """Represents a task."""
    id: str
    name: str
    description: str = ""
    category: str = "other"
    points: int = 10
    frequency: str = FREQUENCY_DAILY
    status: str = TASK_STATUS_TODO
    assigned_child_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    last_completed_at: datetime | None = None
    due_date: datetime | None = None
    validation_required: bool = True
    active: bool = True
    
    def complete(self, validation_required: bool = None) -> str:
        """Mark task as completed."""
        if validation_required is None:
            validation_required = self.validation_required
            
        if validation_required:
            self.status = "pending_validation"
        else:
            self.status = "validated"
            self.last_completed_at = datetime.now()
        return self.status
    
    def validate(self) -> bool:
        """Validate a completed task."""
        if self.status == "pending_validation":
            self.status = "validated"
            self.last_completed_at = datetime.now()
            return True
        return False
    
    def reset(self) -> None:
        """Reset task to todo status."""
        self.status = TASK_STATUS_TODO
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "points": self.points,
            "frequency": self.frequency,
            "status": self.status,
            "assigned_child_id": self.assigned_child_id,
            "created_at": self.created_at.isoformat(),
            "last_completed_at": self.last_completed_at.isoformat() if self.last_completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "validation_required": self.validation_required,
            "active": self.active,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "other"),
            points=data.get("points", 10),
            frequency=data.get("frequency", FREQUENCY_DAILY),
            status=data.get("status", TASK_STATUS_TODO),
            assigned_child_id=data.get("assigned_child_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_completed_at=datetime.fromisoformat(data["last_completed_at"]) if data.get("last_completed_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            validation_required=data.get("validation_required", True),
            active=data.get("active", True),
        )


@dataclass
class Reward:
    """Represents a reward."""
    id: str
    name: str
    description: str = ""
    cost: int = 50
    category: str = "fun"
    active: bool = True
    limited_quantity: int | None = None
    remaining_quantity: int | None = None
    
    def can_claim(self, child_points: int) -> bool:
        """Check if reward can be claimed."""
        if not self.active:
            return False
        if child_points < self.cost:
            return False
        if self.remaining_quantity is not None and self.remaining_quantity <= 0:
            return False
        return True
    
    def claim(self) -> bool:
        """Claim the reward."""
        if self.remaining_quantity is not None:
            if self.remaining_quantity > 0:
                self.remaining_quantity -= 1
                return True
            return False
        return True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "category": self.category,
            "active": self.active,
            "limited_quantity": self.limited_quantity,
            "remaining_quantity": self.remaining_quantity,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reward:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            cost=data.get("cost", 50),
            category=data.get("category", "fun"),
            active=data.get("active", True),
            limited_quantity=data.get("limited_quantity"),
            remaining_quantity=data.get("remaining_quantity"),
        )