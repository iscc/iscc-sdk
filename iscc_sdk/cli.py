import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Iterator, Optional, Tuple
from loguru import logger as log
import typer
from pathlib import Path
import iscc_core as ic
import iscc_sdk as idk
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    DownloadColumn,
)

console = Console()
app = typer.Typer(add_completion=False, no_args_is_help=True)


def _log_formatter(record: dict) -> str:  # pragma: no cover
    """Log message formatter"""
    color_map = {
        "TRACE": "blue",
        "DEBUG": "cyan",
        "INFO": "bold",
        "SUCCESS": "bold green",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }
    lvl_color = color_map.get(record["level"].name, "cyan")
    return (
        "[not bold green]{time:YYYY/MM/DD HH:mm:ss}[/not bold green] | {module:<12} | {line:<3} | {level.icon}"
        + f"  - [{lvl_color}]{{message}}[/{lvl_color}]"
    )


log.add(console.print, level="DEBUG", format=_log_formatter, colorize=True)


def iter_unprocessed(path, root_path=None):
    # type: (str|Path, Optional[str|Path]) -> Iterator[Tuple[Path, int]]
    """
    Walk directory tree recursively with deterministic ordering and yield tuples of file metadata.

    Metadata = (relpath, size)

    - path: pathlib.Path object
    - size: integer file size in number of bytes

    File-entries are yielded in reproducible and deterministic order (bottom-up). Symlink and
    processed files are ignored silently.

    Implementation Note: We use os.scandir to reduce the number of syscalls for metadata collection.
    """
    root_path = Path(root_path or path)
    with os.scandir(path) as entries:
        # Sort the entries
        sorted_entries = sorted(entries, key=lambda e: e.name)

        # Separate directories and files
        dirs = [entry for entry in sorted_entries if entry.is_dir()]
        files = [entry for entry in sorted_entries if entry.is_file()]

        # Recursively process directories first (bottom-up traversal)
        for dir_entry in dirs:
            yield from iter_unprocessed(Path(dir_entry.path), root_path=root_path)

        # Process files in the current directory
        for file_entry in files:
            file_path = Path(file_entry)
            # Ignore result files
            if file_path.name.endswith(".iscc.json") or file_path.name.endswith(".iscc.mp7sig"):
                continue
            # Ignore files that have results
            if Path(file_path.as_posix() + ".iscc.json").exists():
                continue
            file_size = file_entry.stat().st_size
            yield file_path, file_size


def process_file(fp: Path):
    idk.sdk_opts.video_store_mp7sig = True
    try:
        return fp, idk.code_iscc(fp.as_posix())
    except Exception as e:
        return fp, e


@app.command()
def create(file: Path):
    """Create ISCC-CODE for single FILE."""
    log.remove()
    if file.is_file() and file.exists():
        result = idk.code_iscc(file.as_posix())
        typer.echo(result.json(indent=2))
    else:
        typer.echo(f"Invalid file path {file}")
        raise typer.Exit(code=1)


@app.command()
def batch(folder: Path, workers: int = os.cpu_count()):  # pragma: no cover
    """Create ISCC-CODEs for files in FOLDER (parallel & recursive)."""
    if not folder.is_dir() or not folder.exists():
        typer.echo(f"Invalid folder {folder}")
        raise typer.Exit(1)

    file_paths = []
    file_sizes = []
    for path, size in iter_unprocessed(folder):
        file_paths.append(path)
        file_sizes.append(size)

    file_sizes_dict = {path: size for path, size in zip(file_paths, file_sizes)}
    total_size = sum(file_sizes)
    progress = Progress(
        TextColumn("[bold blue]Processing {task.fields[dirname]}", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        task_id = progress.add_task("Processing", dirname=folder.name, total=total_size)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_file, fp) for fp in file_paths]
            for future in as_completed(futures):
                fp, iscc_meta = future.result()
                if isinstance(iscc_meta, idk.IsccMeta):
                    out_path = Path(fp.as_posix() + ".iscc.json")
                    with out_path.open(mode="wt", encoding="utf-8") as outf:
                        outf.write(iscc_meta.json(indent=2))
                    log.info(f"Finished {fp.name}")
                else:
                    log.error(f"Failed {fp.name}: {iscc_meta}")
                progress.update(task_id, advance=file_sizes_dict[fp], refresh=True)


@app.command()
def install():
    """Install content processing tools."""
    idk.install()


@app.command()
def selftest():
    """Run conformance tests."""
    ic.conformance_selftest()


if __name__ == "__main__":  # pragma: no cover
    app()
