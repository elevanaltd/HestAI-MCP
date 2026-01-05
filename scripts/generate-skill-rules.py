#!/usr/bin/env python3
"""
Generate skill-rules.json from SKILL.md files in src/hestai_mcp/_bundled_hub/library/skills/

This script:
1. Scans src/hestai_mcp/_bundled_hub/library/skills/ for SKILL.md files
2. Parses YAML frontmatter to extract metadata
3. Generates .claude/hooks/skill-rules.json with proper structure
"""

import json
import re
from pathlib import Path
from typing import Any


def parse_yaml_frontmatter(content: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from markdown file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    yaml_content = match.group(1)
    metadata = {}

    # Parse simple YAML fields (name, description)
    for line in yaml_content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')

            # Handle triggers array
            if key == "triggers":
                # Parse array: triggers: ["item1", "item2", ...]
                array_match = re.search(r"\[(.*?)\]", value)
                if array_match:
                    items = array_match.group(1)
                    metadata[key] = [
                        item.strip().strip('"').strip("'")
                        for item in items.split(",")
                        if item.strip()
                    ]
            else:
                metadata[key] = value

    return metadata


def generate_skill_rules(skills_dir: Path, output_path: Path) -> None:
    """Generate skill-rules.json from SKILL.md files."""
    skills = {}

    # Find all SKILL.md files
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))

    for skill_file in skill_files:
        skill_name = skill_file.parent.name
        content = skill_file.read_text()

        # Parse frontmatter
        metadata = parse_yaml_frontmatter(content)
        if not metadata:
            print(f"Warning: No frontmatter found in {skill_file}")
            continue

        # Extract required fields
        description = metadata.get("description", "")
        triggers = metadata.get("triggers", [])

        if not triggers:
            print(f"Warning: No triggers found for {skill_name}")
            continue

        # Determine if skill should auto-inject
        # Auto-inject for critical skills that should always be available
        auto_inject = skill_name in {
            "test-coverage",  # Critical for Python testing
            "octave-literacy",  # Essential for reading OCTAVE docs
        }

        # Set injection order (higher = later)
        injection_order = 50  # Default

        # Create skill entry
        skills[skill_name] = {
            "type": "domain",
            "description": description,
            "autoInject": auto_inject,
            "injectionOrder": injection_order,
            "promptTriggers": {"keywords": triggers},
        }

        print(f"✓ Added skill: {skill_name} ({len(triggers)} triggers)")

    # Generate output
    output = {"version": "1.0.0", "skills": skills}

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")

    print(f"\n✓ Generated {output_path} with {len(skills)} skills")


def main() -> None:
    """Main entry point."""
    # Determine paths
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / "src" / "hestai_mcp" / "_bundled_hub" / "library" / "skills"
    output_path = repo_root / ".claude" / "hooks" / "skill-rules.json"

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return

    print(f"Scanning skills in: {skills_dir}")
    print(f"Output: {output_path}\n")

    generate_skill_rules(skills_dir, output_path)


if __name__ == "__main__":
    main()
