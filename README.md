# Tesla Fault Triage – Urgency Model

## About the Project

I built this project to define how Tesla fault reports should be classified by urgency and assigned to the right service path.

The main idea is simple: a missing vehicle alert code does not always mean there is no safety issue. The customer's description also matters.

This project uses Python and Pydantic to define the data structure and validate the results.

## Urgency Levels

| Tag | Meaning |
|---|---|
| `safety_urgent` | A potential safety issue that needs immediate attention |
| `soon` | A problem that needs priority service |
| `routine` | A non-urgent issue that can be handled through regular service |

## Repair Paths

| Path | When to use it |
|---|---|
| `roadside_assistance_towing` | When the vehicle is not safe to drive |
| `priority_service_center` | When the vehicle needs inspection or workshop repair |
| `mobile_service` | For minor physical repairs at the customer's location |
| `remote_support` | For software, app, or connectivity issues |

### Allowed Combinations

| Urgency | Available repair paths |
|---|---|
| `safety_urgent` | `roadside_assistance_towing`, `priority_service_center` |
| `soon` | `priority_service_center` |
| `routine` | `mobile_service`, `remote_support` |

## Safety Considerations

One important point in this project is that the alert code should not be the only factor in deciding urgency.

For example:
- A brake or steering complaint can be safety-related even when the alert code is `NONE`.
- No warning light does not automatically mean the vehicle is safe.
- A customer saying "no rush" should not lower the priority of a potential safety issue.

These are important rules for the triage process. The current model includes a specific validation rule for selected steering-related complaints.

## Data Model

The main model is `TriageResult`, defined in `src/models.py`.

It contains:

| Field | Purpose |
|---|---|
| `message_id` | Identifies the original report |
| `urgency_tag` | Stores the urgency level |
| `fix_paths` | Lists the selected repair paths |
| `vehicle_alert_code` | Stores the vehicle alert code |
| `customer_message_text` | Keeps the customer's original message |

Pydantic checks the field types, required values, and whether the selected repair paths match the urgency level.

## Key Prompt

The following was the main instruction I used to create the model:

> Create a Python repository with a Pydantic model for Tesla fault triage. Use three urgency tags: `safety_urgent`, `soon`, and `routine`.
>
> Define four repair paths: `roadside_assistance_towing`, `priority_service_center`, `mobile_service`, and `remote_support`.
>
> Make sure each urgency level only allows its assigned repair paths. Treat brake, steering, and wheel-related complaints as potential safety issues, even when the vehicle alert code is `NONE`. Missing warning lights or polite language such as "no rush" must not reduce urgency.
>
> Include validation and tests for valid and invalid combinations. Do not build the full triage application.

## My Additional Change

After running the initial tests, I added one more test for steering complaints.

The test checks that a report describing heavy or unstable steering cannot be saved as `routine` when the alert code is `NONE`, even if the customer says there is no warning light or that there is no rush.

I also added a validation rule in `models.py` for the steering-related phrases used in this test.

I made this change because our analysis of the November 16 fault messages showed that some safety-related complaints had no vehicle alert code. I wanted to make sure this type of case would not be accepted as routine without further attention.

## Running the Tests

To run the tests locally:

```bash
python3 -m pytest -v
```

Current result: **8 tests passed.**

## Tools Used

- Python
- Pydantic
- pytest

## Project Structure

```text
Tesla-Triage/
├── data/
│   └── Overnight Fault Message Batch (16 November 2026).csv
├── src/
│   └── models.py
├── tests/
│   └── test_models.py
├── README.md
└── requirements.txt
```