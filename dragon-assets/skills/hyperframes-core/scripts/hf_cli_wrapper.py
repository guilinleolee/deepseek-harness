#!/usr/bin/env python3
"""
Hyperframes CLI Wrapper - Python wrapper for npx hyperframes commands
Provides Pythonic interface for Hyperframes video generation

Usage:
    from hf_cli_wrapper import HyperframesCLI
    cli = HyperframesCLI()
    cli.init("my-video", template="social-media")
    cli.render("output.mp4", props={"HEADLINE": "Hello"})
"""

import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class Template(Enum):
    SOCIAL_MEDIA = "social-media"
    DATA_VIZ = "data-viz"
    PRODUCT_INTRO = "product-intro"
    CUSTOM = "custom"


class VisualStyle(Enum):
    SWISS_PULSE = "swiss-pulse"
    VELVET_STANDARD = "velvet-standard"
    DECONSTRUCTED = "deconstructed"
    MAXIMALIST_TYPE = "maximalist-type"
    DATA_DRIFT = "data-drift"
    SOFT_SIGNAL = "soft-signal"
    FOLK_FREQUENCY = "folk-frequency"
    SHADOW_CUT = "shadow-cut"


@dataclass
class CompositionProps:
    """Properties for a Hyperframes composition"""
    headline: str = ""
    subheadline: str = ""
    cta_text: str = ""
    brand_handle: str = ""
    style: VisualStyle = VisualStyle.SWISS_PULSE
    # Additional props as key-value pairs
    extra: Dict[str, str] = field(default_factory=dict)

    def to_hyperframes_props(self) -> Dict[str, str]:
        """Convert to Hyperframes property format"""
        props = {
            "HEADLINE": self.headline,
            "SUBHEADLINE": self.subheadline,
            "CTA_TEXT": self.cta_text,
            "BRAND_HANDLE": self.brand_handle,
            "STYLE": self.style.value,
        }
        props.update(self.extra)
        return props


@dataclass
class RenderResult:
    """Result of a render operation"""
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class HyperframesCLI:
    """
    Python wrapper for Hyperframes CLI

    Handles:
    - Project initialization
    - Template rendering
    - Property injection
    - Output generation
    """

    def __init__(
        self,
        workspace: Optional[str] = None,
        npx_path: str = "npx",
        verbose: bool = False
    ):
        self.workspace = Path(workspace) if workspace else Path.cwd() / ".hyperframes"
        self.npx_path = npx_path
        self.verbose = verbose
        self._ensure_hyperframes()

    def _ensure_hyperframes(self) -> None:
        """Ensure hyperframes CLI is available"""
        try:
            result = subprocess.run(
                [self.npx_path, "hyperframes", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                if self.verbose:
                    print(f"Hyperframes: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RuntimeError(
                "Hyperframes CLI not found. Install with:\n"
                "  npx hyperframes init\n"
                "Or: npm install -g @hyperframes/cli"
            )

    def _run_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        capture: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a hyperframes command"""
        cmd = [self.npx_path, "hyperframes"] + args
        return subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=cwd or self.workspace,
            timeout=300
        )

    def init(
        self,
        name: str,
        template: str = "social-media",
        output_dir: Optional[str] = None
    ) -> Path:
        """
        Initialize a new Hyperframes project

        Args:
            name: Project name
            template: Template type (social-media, data-viz, product-intro)
            output_dir: Output directory

        Returns:
            Path to the initialized project
        """
        args = ["init", name, "--template", template]
        if output_dir:
            args.extend(["--output", output_dir])

        result = self._run_command(args)

        if result.returncode != 0:
            raise RuntimeError(f"Init failed: {result.stderr}")

        project_dir = self.workspace / name
        if self.verbose:
            print(f"Initialized: {project_dir}")
        return project_dir

    def render(
        self,
        project_path: str,
        output: str,
        props: Optional[Dict[str, str]] = None,
        format: str = "mp4",
        quality: str = "high",
        fps: int = 30
    ) -> RenderResult:
        """
        Render a Hyperframes composition

        Args:
            project_path: Path to the composition HTML
            output: Output file path
            props: Key-value properties to inject
            format: Output format (mp4, webm, gif)
            quality: Quality preset (low, medium, high)
            fps: Frames per second

        Returns:
            RenderResult with success status and metadata
        """
        import time
        start_time = time.time()

        args = [
            "render",
            project_path,
            "--output", output,
            "--format", format,
            "--quality", quality,
            "--fps", str(fps)
        ]

        if props:
            for key, value in props.items():
                args.extend([f"--prop", f"{key}={value}"])

        result = self._run_command(args)

        duration = time.time() - start_time

        if result.returncode == 0:
            return RenderResult(
                success=True,
                output_path=output,
                duration=duration,
                metadata={
                    "format": format,
                    "quality": quality,
                    "fps": fps,
                    "stdout": result.stdout
                }
            )
        else:
            return RenderResult(
                success=False,
                error=result.stderr,
                duration=duration
            )

    def preview(
        self,
        project_path: str,
        port: int = 8080,
        props: Optional[Dict[str, str]] = None
    ) -> subprocess.Popen:
        """
        Start a preview server

        Args:
            project_path: Path to the composition HTML
            port: Server port
            props: Properties to inject

        Returns:
            Popen process handle
        """
        args = ["preview", project_path, "--port", str(port)]

        if props:
            props_file = Path(project_path).parent / "props.json"
            with open(props_file, "w") as f:
                json.dump(props, f, indent=2)
            args.extend(["--props", str(props_file)])

        return subprocess.Popen(
            [self.npx_path, "hyperframes"] + args,
            stdout=subprocess.PIPE if not self.verbose else None,
            stderr=subprocess.PIPE if not self.verbose else None
        )

    def generate_props_file(
        self,
        template: Template,
        props: CompositionProps,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a properties JSON file for a template

        Args:
            template: Template type
            props: Composition properties
            output_path: Output file path

        Returns:
            Path to the generated file
        """
        if output_path is None:
            output_path = self.workspace / f"{template.value}_props.json"

        hyperframes_props = props.to_hyperframes_props()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hyperframes_props, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def list_templates(self) -> List[str]:
        """List available templates"""
        return [
            "social-media",
            "data-viz",
            "product-intro",
            "custom"
        ]


class PipelineComposer:
    """
    High-level pipeline for batch video generation

    Usage:
        composer = PipelineComposer()
        composer.add_scene("intro", props=...)
        composer.add_scene("main", props=...)
        composer.render("output.mp4")
    """

    def __init__(self, cli: Optional[HyperframesCLI] = None):
        self.cli = cli or HyperframesCLI()
        self.scenes: List[Dict[str, Any]] = []

    def add_scene(
        self,
        name: str,
        template: str,
        props: CompositionProps,
        transition: str = "fade"
    ) -> None:
        """Add a scene to the pipeline"""
        self.scenes.append({
            "name": name,
            "template": template,
            "props": props,
            "transition": transition
        })

    def render_all(self, output_dir: str) -> List[RenderResult]:
        """Render all scenes sequentially"""
        results = []
        for scene in self.scenes:
            output_path = f"{output_dir}/{scene['name']}.mp4"
            props = scene["props"].to_hyperframes_props()

            result = self.cli.render(
                project_path=f"compositions/{scene['name']}.html",
                output=output_path,
                props=props
            )
            results.append(result)

        return results


def quick_render(
    template: str,
    output: str,
    **props
) -> RenderResult:
    """
    Quick one-liner render

    Usage:
        result = quick_render(
            "social-media",
            "output.mp4",
            HEADLINE="Hello World",
            SUBHEADLINE="Welcome",
            CTA_TEXT="Click Here",
            BRAND_HANDLE="@mybrand"
        )
    """
    cli = HyperframesCLI()
    project = cli.init(f"quick_{Path(output).stem}")

    # Write composition
    composition_path = project / "composition.html"
    shutil.copy(
        Path(__file__).parent.parent / "templates" / template / "index.html",
        composition_path
    )

    return cli.render(
        str(composition_path),
        output,
        props
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hyperframes CLI Wrapper")
    subparsers = parser.add_subparsers(dest="command")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--template", default="social-media")

    # Render command
    render_parser = subparsers.add_parser("render", help="Render composition")
    render_parser.add_argument("input", help="Input HTML file")
    render_parser.add_argument("output", help="Output file")
    render_parser.add_argument("--props", help="Properties JSON file")

    # List command
    subparsers.add_parser("list", help="List templates")

    args = parser.parse_args()

    if args.command == "init":
        cli = HyperframesCLI(verbose=True)
        cli.init(args.name, args.template)
        print(f"Created: {args.name}")

    elif args.command == "render":
        cli = HyperframesCLI(verbose=True)
        props = None
        if args.props:
            with open(args.props) as f:
                props = json.load(f)
        result = cli.render(args.input, args.output, props)
        if result.success:
            print(f"Rendered: {result.output_path}")
        else:
            print(f"Error: {result.error}")

    elif args.command == "list":
        cli = HyperframesCLI()
        for t in cli.list_templates():
            print(f"  - {t}")

    else:
        parser.print_help()
