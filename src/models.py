
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


class UrgencyTag(str, Enum):
    SAFETY_URGENT = "safety_urgent"
    SOON = "soon"
    ROUTINE = "routine"


class FixPath(str, Enum):
    ROADSIDE_ASSISTANCE_TOWING = "roadside_assistance_towing"
    PRIORITY_SERVICE_CENTER = "priority_service_center"
    MOBILE_SERVICE = "mobile_service"
    REMOTE_SUPPORT = "remote_support"


ALLOWED_FIX_PATHS = {
    UrgencyTag.SAFETY_URGENT: {
        FixPath.ROADSIDE_ASSISTANCE_TOWING,
        FixPath.PRIORITY_SERVICE_CENTER,
    },
    UrgencyTag.SOON: {
        FixPath.PRIORITY_SERVICE_CENTER,
    },
    UrgencyTag.ROUTINE: {
        FixPath.MOBILE_SERVICE,
        FixPath.REMOTE_SUPPORT,
    },
}


# Steering complaints that require safety escalation
STEERING_SAFETY_TERMS = (
    "heavy steering",
    "unstable steering",
    "steering feels heavy",
    "steering feels unstable",
    "steering is heavy",
    "steering is unstable",
)


class TriageResult(BaseModel):
    message_id: str = Field(min_length=1)
    urgency_tag: UrgencyTag
    fix_paths: list[FixPath] = Field(min_length=1)
    vehicle_alert_code: str = Field(min_length=1)
    customer_message_text: str = Field(min_length=1)

    @field_validator("fix_paths")
    @classmethod
    def paths_must_be_unique(cls, paths):
        if len(paths) != len(set(paths)):
            raise ValueError("Duplicate fix paths are not allowed")
        return paths

    @model_validator(mode="after")
    def validate_fix_paths_for_urgency(self):
        allowed = ALLOWED_FIX_PATHS[self.urgency_tag]

        invalid_paths = set(self.fix_paths) - allowed

        if invalid_paths:
            raise ValueError(
                f"Fix paths {invalid_paths} are not allowed "
                f"for urgency tag '{self.urgency_tag.value}'"
            )

        message = self.customer_message_text.lower()

        if any(term in message for term in STEERING_SAFETY_TERMS):
            if self.urgency_tag == UrgencyTag.ROUTINE:
                raise ValueError(
                    "Potential steering safety complaints cannot be routine"
                )

        return self
