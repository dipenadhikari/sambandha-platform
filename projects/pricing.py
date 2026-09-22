from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class ServiceDefinition:
    key: str
    name: str
    unit: str
    prices: dict[str, int]
    default_quantity: int
    max_quantity: int


SERVICES = (
    ServiceDefinition(
        "modular_kitchen",
        "Modular kitchen",
        "unit",
        {"basic": 650_000, "medium": 825_000, "premium": 1_000_000},
        1,
        5,
    ),
    ServiceDefinition(
        "living_tv_wall",
        "Living room & TV wall",
        "unit",
        {"basic": 280_000, "medium": 350_000, "premium": 420_000},
        1,
        8,
    ),
    ServiceDefinition(
        "bathroom_upgrade",
        "Bathroom upgrade",
        "unit",
        {"basic": 300_000, "medium": 370_000, "premium": 440_000},
        1,
        10,
    ),
    ServiceDefinition(
        "false_ceiling",
        "False ceiling",
        "sq. ft.",
        {"basic": 300, "medium": 360, "premium": 430},
        500,
        20_000,
    ),
    ServiceDefinition(
        "flooring",
        "Flooring",
        "sq. ft.",
        {"basic": 300, "medium": 380, "premium": 480},
        500,
        20_000,
    ),
    ServiceDefinition(
        "interior_painting",
        "Interior painting",
        "sq. ft.",
        {"basic": 55, "medium": 70, "premium": 85},
        1_000,
        50_000,
    ),
    ServiceDefinition(
        "facade_finishing",
        "Facade finishing",
        "sq. ft.",
        {"basic": 420, "medium": 520, "premium": 650},
        500,
        20_000,
    ),
    ServiceDefinition(
        "exterior_painting",
        "Exterior painting",
        "sq. ft.",
        {"basic": 60, "medium": 75, "premium": 95},
        1_000,
        50_000,
    ),
    ServiceDefinition(
        "waterproofing",
        "Waterproofing",
        "sq. ft.",
        {"basic": 120, "medium": 150, "premium": 180},
        500,
        20_000,
    ),
    ServiceDefinition(
        "landscape_package",
        "Landscape package",
        "unit",
        {"basic": 280_000, "medium": 350_000, "premium": 420_000},
        1,
        4,
    ),
    ServiceDefinition(
        "boundary_gate",
        "Boundary gate",
        "unit",
        {"basic": 300_000, "medium": 360_000, "premium": 425_000},
        1,
        4,
    ),
)

SERVICE_MAP = {service.key: service for service in SERVICES}
COORDINATION_RATE = Decimal("0.06")
RANGE_LOW_RATE = Decimal("0.90")
RANGE_HIGH_RATE = Decimal("1.12")


class PricingError(ValueError):
    pass


def _rounded(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_estimate(finish_level: str, quantities: dict[str, int]) -> dict:
    if finish_level not in {"basic", "medium", "premium"}:
        raise PricingError("Unknown finish level.")

    line_items = []
    subtotal = 0

    for key, raw_quantity in quantities.items():
        if key not in SERVICE_MAP:
            raise PricingError(f"Unknown service: {key}")
        service = SERVICE_MAP[key]
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError) as exc:
            raise PricingError(f"Invalid quantity for {service.name}.") from exc
        if quantity < 0 or quantity > service.max_quantity:
            raise PricingError(
                f"{service.name} quantity must be between 0 and {service.max_quantity:,}."
            )
        if quantity == 0:
            continue

        unit_price = service.prices[finish_level]
        total = quantity * unit_price
        subtotal += total
        line_items.append(
            {
                "key": service.key,
                "name": service.name,
                "unit": service.unit,
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total,
            }
        )

    if not line_items:
        raise PricingError("Select at least one service and enter a quantity.")

    coordination_fee = _rounded(Decimal(subtotal) * COORDINATION_RATE)
    planning_midpoint = subtotal + coordination_fee

    return {
        "line_items": line_items,
        "subtotal": subtotal,
        "coordination_fee": coordination_fee,
        "location_adjustment": 0,
        "planning_midpoint": planning_midpoint,
        "estimate_low": _rounded(Decimal(planning_midpoint) * RANGE_LOW_RATE),
        "estimate_high": _rounded(Decimal(planning_midpoint) * RANGE_HIGH_RATE),
    }

