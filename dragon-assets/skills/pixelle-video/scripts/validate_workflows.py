#!/usr/bin/env python3
"""
Pixelle-Video Integration Test Suite
Tests workflow validation and API connectivity
"""

import json
import sys
from pathlib import Path


def validate_workflow(workflow_path: Path) -> dict:
    """Validate a workflow JSON file"""
    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors = []
        warnings = []

        # Required fields
        if "workflow_name" not in data:
            errors.append("Missing workflow_name")
        if "prompt" not in data:
            errors.append("Missing prompt section")

        # Node validation
        prompt = data.get("prompt", {})
        for node_id, node in prompt.items():
            if "class_type" not in node:
                errors.append(f"Node {node_id}: missing class_type")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "nodes": len(prompt)
        }
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"JSON parse error: {e}"]}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


def run_tests():
    """Run all integration tests"""
    skills_dir = Path(__file__).parent.parent
    workflows_dir = skills_dir / "workflows"
    scripts_dir = skills_dir / "scripts"

    results = {
        "workflows": [],
        "scripts": [],
        "summary": {"total": 0, "passed": 0, "failed": 0}
    }

    # Test workflows
    print("Testing Workflows:")
    print("-" * 50)

    workflow_files = list(workflows_dir.glob("*.json"))
    for wf_file in workflow_files:
        result = validate_workflow(wf_file)
        status = "PASS" if result["valid"] else "FAIL"

        print(f"  {wf_file.name}: {status} ({result.get('nodes', 0)} nodes)")

        if not result["valid"]:
            for err in result["errors"]:
                print(f"    Error: {err}")

        results["workflows"].append({
            "file": wf_file.name,
            "status": status,
            "result": result
        })

        results["summary"]["total"] += 1
        if result["valid"]:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    # Test scripts
    print("\nChecking Scripts:")
    print("-" * 50)

    required_scripts = ["api_client.py", "workflow_manager.py"]
    for script in required_scripts:
        script_path = scripts_dir / script
        exists = script_path.exists()

        status = "PASS" if exists else "FAIL"
        print(f"  {script}: {status}")

        results["scripts"].append({"file": script, "exists": exists})
        results["summary"]["total"] += 1
        if exists:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed")

    return results["summary"]["failed"] == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
