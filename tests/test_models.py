
import pytest
from pydantic import ValidationError

from src.models import TriageResult, UrgencyTag, FixPath


def test_safety_urgent_allows_two_paths():
    result = TriageResult(
        message_id="MSG-10001",
        urgency_tag=UrgencyTag.SAFETY_URGENT,
        fix_paths=[
            FixPath.ROADSIDE_ASSISTANCE_TOWING,
            FixPath.PRIORITY_SERVICE_CENTER,
        ],
        vehicle_alert_code="BRK_a001",
        customer_message_text="Brake pedal feels soft.",
    )

    assert result.urgency_tag == UrgencyTag.SAFETY_URGENT


def test_soon_allows_priority_service_center():
    result = TriageResult(
        message_id="MSG-10002",
        urgency_tag="soon",
        fix_paths=["priority_service_center"],
        vehicle_alert_code="EPAS_w202",
        customer_message_text="Steering feels unusual.",
    )

    assert result.fix_paths == [FixPath.PRIORITY_SERVICE_CENTER]


def test_routine_allows_mobile_and_remote_support():
    result = TriageResult(
        message_id="MSG-10003",
        urgency_tag="routine",
        fix_paths=["mobile_service", "remote_support"],
        vehicle_alert_code="UI_a004",
        customer_message_text="The touchscreen restarts.",
    )

    assert result.urgency_tag == UrgencyTag.ROUTINE


def test_safety_urgent_rejects_mobile_service():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="MSG-10004",
            urgency_tag="safety_urgent",
            fix_paths=["mobile_service"],
            vehicle_alert_code="NONE",
            customer_message_text="Brake pedal feels soft.",
        )


def test_soon_rejects_remote_support():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="MSG-10005",
            urgency_tag="soon",
            fix_paths=["remote_support"],
            vehicle_alert_code="NONE",
            customer_message_text="Steering feels unstable.",
        )


def test_empty_fix_paths_are_rejected():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="MSG-10006",
            urgency_tag="routine",
            fix_paths=[],
            vehicle_alert_code="UI_a004",
            customer_message_text="The screen is slow.",
        )


def test_duplicate_fix_paths_are_rejected():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="MSG-10007",
            urgency_tag="routine",
            fix_paths=["mobile_service", "mobile_service"],
            vehicle_alert_code="NONE",
            customer_message_text="Minor interior issue.",
        )


def test_steering_complaint_with_none_code_is_not_routine():
    """
    Regression test: A steering safety complaint must not be classified
    as routine just because the vehicle alert code is NONE.
    """
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="MSG-10008",
            urgency_tag="routine",
            fix_paths=["mobile_service"],
            vehicle_alert_code="NONE",
            customer_message_text=(
                "The steering feels heavy and unstable. "
                "No warning light is showing, and there is no rush."
            ),
        )
