from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1] / "marianne/skills/conducting"

def test_maintenance_has_separate_optional_route():
    taskmap = (ROOT / "TASK-MAP.md").read_text().lower()
    owner = ROOT / "references/venue-maintenance.md"
    assert owner.is_file()
    assert "references/venue-maintenance.md" in taskmap
    assert "venue" in taskmap and "owner" in taskmap
    assert "first complete the mandatory" not in taskmap

def test_missing_native_enforcement_is_not_conductor_implementation():
    text = (ROOT / "references/marianne-operations.md").read_text()
    assert "Missing native enforcement stays an explicit conductor obligation" not in text
    assert "makes its enforcement the conductor's explicit responsibility" not in text
    assert "install-package" not in text
    assert "bind-score-routes" not in text

def test_ordinary_interface_retains_lifecycle_and_integrity():
    main = (ROOT / "SKILL.md").read_text().lower()
    assert "venue" in main and "owner" in main
    assert "full lifecycle" in main or "full rich lifecycle" in main
    assert "integrity" in main
    assert "semantic" in main
    assert "custody" in main

def test_role_boundary_scenarios_cover_ordinary_and_exceptional_work():
    scenarios = yaml.safe_load((ROOT / "evals/scenarios.yaml").read_text())["scenarios"]
    wanted = {"ordinary-stock-engagement", "venue-enforcement-gap", "dual-role-explicit"}
    assert wanted <= {row["id"] for row in scenarios}
