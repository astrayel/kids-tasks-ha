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
class TaskChildStatus:
    """Represents the status of a task for a specific child."""
    child_id: str
    status: str = TASK_STATUS_TODO
    completed_at: datetime | None = None
    validated_at: datetime | None = None
    penalty_applied_at: datetime | None = None
    penalty_applied: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "child_id": self.child_id,
            "status": self.status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "penalty_applied_at": self.penalty_applied_at.isoformat() if self.penalty_applied_at else None,
            "penalty_applied": self.penalty_applied,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskChildStatus:
        """Create from dictionary."""
        return cls(
            child_id=data["child_id"],
            status=data.get("status", TASK_STATUS_TODO),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            validated_at=datetime.fromisoformat(data["validated_at"]) if data.get("validated_at") else None,
            penalty_applied_at=datetime.fromisoformat(data["penalty_applied_at"]) if data.get("penalty_applied_at") else None,
            penalty_applied=data.get("penalty_applied", False),
        )


@dataclass
class Child:
    """Represents a child."""
    id: str
    name: str
    points: int = 0
    level: int = 1
    avatar: str | None = None
    person_entity_id: str | None = None  # ID de l'entité personne HA (optionnel)
    avatar_type: str = "emoji"  # "emoji", "url", "inline", "person_entity"
    avatar_data: str | None = None  # Données selon le type (URL, base64, etc.)
    card_gradient_start: str | None = None  # Couleur début dégradé
    card_gradient_end: str | None = None    # Couleur fin dégradé
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        return (self.level * 100) - self.points
    
    def add_points(self, points: int) -> bool:
        """Add points and check for level up."""
        old_level = self.level
        self.points += points
        # Corrected level calculation: level 1 = 0-99 points, level 2 = 100-199 points, etc.
        self.level = (self.points // 100) + 1
        return self.level > old_level

    def get_effective_avatar(self, hass=None) -> str:
        """Get the effective avatar based on avatar_type."""
        if self.avatar_type == "emoji":
            return self.avatar or "👶"
        elif self.avatar_type == "url" and self.avatar_data:
            return self.avatar_data
        elif self.avatar_type == "inline" and self.avatar_data:
            return f"data:image/png;base64,{self.avatar_data}"
        elif self.avatar_type == "person_entity" and self.person_entity_id and hass:
            person_entity = hass.states.get(self.person_entity_id)
            if person_entity and 'entity_picture' in person_entity.attributes:
                return person_entity.attributes.get('entity_picture', self.avatar or "👶")
        return self.avatar or "👶"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "points": self.points,
            "level": self.level,
            "avatar": self.avatar,
            "person_entity_id": self.person_entity_id,
            "avatar_type": self.avatar_type,
            "avatar_data": self.avatar_data,
            "card_gradient_start": self.card_gradient_start,
            "card_gradient_end": self.card_gradient_end,
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
            person_entity_id=data.get("person_entity_id"),
            avatar_type=data.get("avatar_type", "emoji"),
            avatar_data=data.get("avatar_data"),
            card_gradient_start=data.get("card_gradient_start"),
            card_gradient_end=data.get("card_gradient_end"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )


@dataclass
class Task:
    """Represents a task."""
    id: str
    name: str
    description: str = ""
    category: str = "other"
    icon: str | None = None  # Icône personnalisée (emoji ou caractère)
    points: int = 10
    frequency: str = FREQUENCY_DAILY
    status: str = TASK_STATUS_TODO  # Statut global pour compatibilité (sera calculé automatiquement)
    assigned_child_ids: list[str] = field(default_factory=list)  # Liste des IDs d'enfants assignés
    child_statuses: dict[str, TaskChildStatus] = field(default_factory=dict)  # Statuts par enfant
    created_at: datetime = field(default_factory=datetime.now)
    last_completed_at: datetime | None = None
    due_date: datetime | None = None
    validation_required: bool = True
    active: bool = True
    weekly_days: list[str] | None = None  # Jours de la semaine pour fréquence daily: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    deadline_time: str | None = None  # Heure limite au format "HH:MM" (ex: "18:00")
    penalty_points: int = 0  # Points déduits si la tâche n'est pas faite à l'heure limite
    deadline_passed: bool = False  # Indique si l'heure limite est dépassée
    completed_by_child_id: str | None = None  # ID de l'enfant qui a complété la tâche (pour compatibilité)
    
    def complete_for_child(self, child_id: str, validation_required: bool = None) -> str:
        """Mark task as completed for a specific child."""
        if validation_required is None:
            validation_required = self.validation_required
        
        # Initialize child status if not exists
        if child_id not in self.child_statuses:
            self.child_statuses[child_id] = TaskChildStatus(child_id=child_id)
        
        child_status = self.child_statuses[child_id]
        
        if validation_required:
            child_status.status = "pending_validation"
            child_status.completed_at = datetime.now()
        else:
            child_status.status = "validated"
            child_status.completed_at = datetime.now()
            child_status.validated_at = datetime.now()
        
        # Update global status and compatibility fields
        self.completed_by_child_id = child_id
        self._update_global_status()
        
        return child_status.status
    
    def validate_for_child(self, child_id: str) -> bool:
        """Validate a completed task for a specific child."""
        if child_id not in self.child_statuses:
            return False
        
        child_status = self.child_statuses[child_id]
        if child_status.status == "pending_validation":
            child_status.status = "validated"
            child_status.validated_at = datetime.now()
            self._update_global_status()
            return True
        return False
    
    def get_status_for_child(self, child_id: str) -> str:
        """Get status for a specific child."""
        if child_id not in self.child_statuses:
            return TASK_STATUS_TODO
        return self.child_statuses[child_id].status
    
    def _update_global_status(self) -> None:
        """Update global status based on individual child statuses."""
        if not self.child_statuses:
            self.status = TASK_STATUS_TODO
            return
        
        # Count statuses
        statuses = [cs.status for cs in self.child_statuses.values()]
        
        # If any child has pending validation, task is pending validation
        if "pending_validation" in statuses:
            self.status = "pending_validation"
        # If all assigned children are validated, task is validated
        elif all(cs.status == "validated" for cs in self.child_statuses.values() if cs.child_id in self.assigned_child_ids):
            self.status = "validated"
            # Update last_completed_at to the latest validation
            latest_validation = max(
                (cs.validated_at for cs in self.child_statuses.values() 
                 if cs.validated_at and cs.child_id in self.assigned_child_ids),
                default=None
            )
            if latest_validation:
                self.last_completed_at = latest_validation
        else:
            self.status = TASK_STATUS_TODO
    
    def complete(self, validation_required: bool = None) -> str:
        """Mark task as completed (legacy method for compatibility)."""
        if validation_required is None:
            validation_required = self.validation_required
            
        if validation_required:
            self.status = "pending_validation"
        else:
            self.status = "validated"
            self.last_completed_at = datetime.now()
        return self.status
    
    def validate(self) -> bool:
        """Validate a completed task (legacy method for compatibility)."""
        if self.status == "pending_validation":
            self.status = "validated"
            self.last_completed_at = datetime.now()
            return True
        return False
    
    def reset(self) -> None:
        """Reset task to todo status for all children."""
        self.status = TASK_STATUS_TODO
        self.deadline_passed = False  # Reset deadline flag
        self.completed_by_child_id = None  # Reset completion info
        # Reset all child statuses
        for child_status in self.child_statuses.values():
            child_status.status = TASK_STATUS_TODO
            child_status.completed_at = None
            child_status.validated_at = None
            child_status.penalty_applied_at = None
            child_status.penalty_applied = False
    
    def get_assigned_child_ids(self) -> list[str]:
        """Get list of assigned child IDs."""
        return self.assigned_child_ids
    
    def set_assigned_child_ids(self, child_ids: list[str]) -> None:
        """Set assigned child IDs."""
        self.assigned_child_ids = child_ids
    
    def check_deadline(self) -> bool:
        """Check if deadline has passed and update deadline_passed flag."""
        if not self.deadline_time or self.status != TASK_STATUS_TODO:
            return False
            
        from datetime import datetime, time
        now = datetime.now()
        today = now.date()
        
        # Parse deadline time (format "HH:MM")
        try:
            deadline_hour, deadline_minute = map(int, self.deadline_time.split(':'))
            deadline_datetime = datetime.combine(today, time(deadline_hour, deadline_minute))
            
            # Si l'heure limite est dépassée et que la tâche n'est pas encore marquée comme dépassée
            if now > deadline_datetime and not self.deadline_passed:
                self.deadline_passed = True
                return True  # Deadline vient d'être dépassée
                
        except (ValueError, AttributeError):
            # Format d'heure invalide
            return False
            
        return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "icon": self.icon,
            "points": self.points,
            "frequency": self.frequency,
            "status": self.status,
            "assigned_child_ids": self.assigned_child_ids,
            "child_statuses": {child_id: status.to_dict() for child_id, status in self.child_statuses.items()},
            "created_at": self.created_at.isoformat(),
            "last_completed_at": self.last_completed_at.isoformat() if self.last_completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "validation_required": self.validation_required,
            "active": self.active,
            "weekly_days": self.weekly_days,
            "deadline_time": self.deadline_time,
            "penalty_points": self.penalty_points,
            "deadline_passed": self.deadline_passed,
            "completed_by_child_id": self.completed_by_child_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Create from dictionary."""
        # Parse child statuses
        child_statuses = {}
        if "child_statuses" in data:
            for child_id, status_data in data["child_statuses"].items():
                child_statuses[child_id] = TaskChildStatus.from_dict(status_data)
        
        task = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "other"),
            icon=data.get("icon"),
            points=data.get("points", 10),
            frequency=data.get("frequency", FREQUENCY_DAILY),
            status=data.get("status", TASK_STATUS_TODO),
            assigned_child_ids=data.get("assigned_child_ids", []),
            child_statuses=child_statuses,
            created_at=datetime.fromisoformat(data["created_at"]),
            last_completed_at=datetime.fromisoformat(data["last_completed_at"]) if data.get("last_completed_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            validation_required=data.get("validation_required", True),
            active=data.get("active", True),
            weekly_days=data.get("weekly_days"),
            deadline_time=data.get("deadline_time"),
            penalty_points=data.get("penalty_points", 0),
            deadline_passed=data.get("deadline_passed", False),
            completed_by_child_id=data.get("completed_by_child_id"),
        )
        
        return task


@dataclass
class Reward:
    """Represents a reward."""
    id: str
    name: str
    description: str = ""
    cost: int = 50
    category: str = "fun"
    icon: str | None = None  # Icône personnalisée (emoji ou caractère)
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
            "icon": self.icon,
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
            icon=data.get("icon"),
            active=data.get("active", True),
            limited_quantity=data.get("limited_quantity"),
            remaining_quantity=data.get("remaining_quantity"),
        )