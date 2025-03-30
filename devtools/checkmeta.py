"""
Try to extract and display metadata for all files in a directory.

Usage:
    python checkmeta.py /path/to/directory
"""

import sys
from pathlib import Path
import iscc_sdk as idk
from rich.console import Console
from rich.panel import Panel


def check_metadata(directory):
    # type: (str|Path) -> None
    """Process all files in directory and try to extract metadata."""
    console = Console()
    path = Path(directory)

    if not path.exists():
        console.print(f"[red]Directory not found: {path}[/red]")
        return

    for file in path.glob("*"):
        if file.is_file():
            console.rule(f"[blue]{file.name}")
            try:
                meta = idk.image_meta_extract(str(file))
                if meta:
                    console.print(
                        Panel.fit(f"[green]{meta}", title="Metadata found", border_style="green")
                    )
                else:
                    console.print("[yellow]No metadata found[/yellow]")
            except Exception as e:
                console.print(f"[red]Error processing file: {e}[/red]")
            console.print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python checkmeta.py /path/to/directory")
        sys.exit(1)
    check_metadata(sys.argv[1])
