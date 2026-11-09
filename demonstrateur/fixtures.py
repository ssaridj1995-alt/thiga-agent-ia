"""Synthetic phase-A fixture v1. No Open WebUI account is represented here."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    job_title: str
    team: str
    tenant: str
    manager_id: str | None
    leave_days: int
    is_manager: bool = False


EMPLOYEES = {
    e.employee_id: e for e in [
        Employee("marc", "Marc", "Exemple", "Manager produit", "produit", "A", None, 17, True),
        Employee("alice", "Alice", "Exemple", "Product manager", "produit", "A", "marc", 12),
        Employee("lea", "Léa", "Exemple", "Product designer", "produit", "A", "marc", 8),
        Employee("claire", "Claire", "Exemple", "Analyste finance", "finance", "A", None, 15),
        Employee("bob", "Bob", "Exemple", "Consultant", "produit", "B", None, 21),
    ]
}
# Deliberately test-client IDs, never alleged real WebUI IDs.
TEST_IDENTITIES = {f"phase-a-client-{name}": name for name in EMPLOYEES}


def normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


DIRECTORY_FIELDS = ("employee_id", "first_name", "last_name", "job_title", "team")


def search(actor: Employee, query: str) -> list[dict]:
    needle = normalize(query)
    visible = []
    for employee in sorted(EMPLOYEES.values(), key=lambda e: e.employee_id):
        keys = (employee.employee_id, employee.first_name, employee.last_name,
                f"{employee.first_name} {employee.last_name}")
        if employee.tenant == actor.tenant and needle in {normalize(k) for k in keys}:
            visible.append({key: getattr(employee, key) for key in DIRECTORY_FIELDS})
    return visible[:5]


def balance(actor: Employee, employee_id: str) -> tuple[dict | str, str]:
    target = EMPLOYEES.get(employee_id)
    if target is None:
        return "unavailable", "target_unknown"
    if target.tenant != actor.tenant:
        return "unavailable", "tenant_denied"
    if target.employee_id != actor.employee_id and not (
        actor.is_manager and target.manager_id == actor.employee_id
    ):
        return "unavailable", "relationship_denied"
    return {"employee_id": target.employee_id, "leave_days": target.leave_days}, "allowed"
