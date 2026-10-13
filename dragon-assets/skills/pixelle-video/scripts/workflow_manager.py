#!/usr/bin/env python3
"""
Pixelle-Video Workflow Manager
Workflow lifecycle management and validation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class WorkflowManager:
    """Manage Pixelle-Video workflows"""

    def __init__(self, workflows_dir: str = None):
        if workflows_dir is None:
            workflows_dir = os.path.join(
                os.path.dirname(__file__), "..", "workflows"
            )
        self.workflows_dir = Path(workflows_dir)

    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows"""
        workflows = []
        for wf_file in self.workflows_dir.glob("*.json"):
            with open(wf_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                workflows.append({
                    "name": data.get("workflow_name", wf_file.stem),
                    "description": data.get("workflow_description", ""),
                    "version": data.get("comfyui_version", "unknown"),
                    "file": wf_file.name
                })
        return workflows

    def validate_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Validate a workflow JSON structure"""
        wf_path = self.workflows_dir / f"{workflow_name}.json"
        if not wf_path.exists():
            return {"valid": False, "error": f"Workflow not found: {workflow_name}"}

        try:
            with open(wf_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            errors = []
            warnings = []

            # Check required fields
            if "workflow_name" not in data:
                errors.append("Missing workflow_name")
            if "prompt" not in data:
                errors.append("Missing prompt section")

            # Check prompt nodes
            prompt = data.get("prompt", {})
            if not prompt:
                errors.append("Empty prompt section")
            else:
                for node_id, node in prompt.items():
                    if "class_type" not in node:
                        errors.append(f"Node {node_id}: missing class_type")
                    if "inputs" not in node:
                        warnings.append(f"Node {node_id}: missing inputs")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "node_count": len(prompt),
                "nodes": list(prompt.keys())
            }
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {e}"}

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """Get detailed workflow information"""
        wf_path = self.workflows_dir / f"{workflow_name}.json"
        if not wf_path.exists():
            return {"error": f"Workflow not found: {workflow_name}"}

        with open(wf_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "name": data.get("workflow_name", ""),
            "description": data.get("workflow_description", ""),
            "version": data.get("comfyui_version", ""),
            "created": data.get("created", ""),
            "pipeline": data.get("pipeline", []),
            "node_count": len(data.get("prompt", {})),
            "nodes": [
                {
                    "id": node_id,
                    "type": node.get("class_type", ""),
                    "inputs": list(node.get("inputs", {}).keys())
                }
                for node_id, node in data.get("prompt", {}).items()
            ]
        }

    def export_workflow(self, workflow_name: str, output_path: str) -> bool:
        """Export workflow to specified path"""
        wf_path = self.workflows_dir / f"{workflow_name}.json"
        if not wf_path.exists():
            return False

        import shutil
        shutil.copy(wf_path, output_path)
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pixelle-Video Workflow Manager")
    parser.add_argument("--list", action="store_true", help="List all workflows")
    parser.add_argument("--validate", metavar="NAME", help="Validate workflow")
    parser.add_argument("--info", metavar="NAME", help="Show workflow info")
    parser.add_argument("--workflows-dir", help="Workflows directory")

    args = parser.parse_args()
    manager = WorkflowManager(args.workflows_dir)

    if args.list:
        print("Available Workflows:")
        print("-" * 60)
        for wf in manager.list_workflows():
            print(f"  {wf['name']}")
            print(f"    {wf['description']}")
            print(f"    Version: {wf['version']}")
            print()

    elif args.validate:
        result = manager.validate_workflow(args.validate)
        print(f"Validation: {'PASS' if result['valid'] else 'FAIL'}")
        if result.get('errors'):
            print("Errors:")
            for e in result['errors']:
                print(f"  - {e}")
        if result.get('warnings'):
            print("Warnings:")
            for w in result['warnings']:
                print(f"  - {w}")

    elif args.info:
        info = manager.get_workflow_info(args.info)
        if "error" in info:
            print(f"Error: {info['error']}")
            return
        print(f"Workflow: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Version: {info['version']}")
        print(f"Created: {info['created']}")
        print(f"\nPipeline:")
        for step in info['pipeline']:
            print(f"  {step}")
        print(f"\nNodes ({info['node_count']}):")
        for node in info['nodes']:
            print(f"  [{node['id']}] {node['type']}")
            for inp in node['inputs']:
                print(f"      - {inp}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
