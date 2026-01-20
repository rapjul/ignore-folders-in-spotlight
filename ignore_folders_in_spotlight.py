#!/usr/bin/env python3
"""
Usage:

    sudo python3 ignore_folders_in_spotlight.py [PATH]

This script will tell Spotlight to ignore any folder in/under PATH
that's named "node_modules" or "target".

If PATH is omitted, it uses the current working directory.

Original script written by Alex Chan.
See https://alexwlchan.net/2021/08/ignore-lots-of-folders-in-spotlight/

"""

import argparse
import datetime
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# The list of directory names that should be ignored
IGNORE_DIRECTORIES = {
    "node_modules",  # Node.js dependencies
    "target",  # Rust, Maven build output
    "build",  # Generic build output
    "dist",  # Distribution/build output
    "venv",  # Python virtual environments
    ".venv",  # Python virtual environments (hidden)
    "vendor",  # Go, PHP, Ruby dependencies
    "__pycache__",  # Python bytecode cache
    ".gradle",  # Gradle build artifacts (Java/Android)
    ".next",  # Next.js build output
    "coverage",  # Test coverage reports
    "Pods",  # CocoaPods dependencies (iOS/macOS)
}

# Path to the Spotlight plist on Catalina
SPOTLIGHT_PLIST_PATH = "/System/Volumes/Data/.Spotlight-V100/VolumeConfiguration.plist"


def get_dir_paths_under(root: Path):
    """
    Generates the paths of every directory under ``root``.

    Args:
        root: The root directory to search under.

    Returns:
        A list of Path objects for every directory under root.
    """
    root = Path(root).resolve()
    for item in root.rglob("*"):
        if item.is_dir():
            yield item


def create_backup_of_spotlight_plist():
    """
    Save a backup of the Spotlight configuration to the Desktop before
    we start.

    This gives us a way to rollback, and also is a nondestructive check
    that we have the right permissions to modify the Spotlight config.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
    home = Path.home()
    backup_path = home / "Desktop" / f"Spotlight-V100.VolumeConfiguration.{now}.plist"

    try:
        subprocess.check_call(["cp", SPOTLIGHT_PLIST_PATH, str(backup_path)])
    except subprocess.CalledProcessError:
        print("Could not create backup of Spotlight configuration", file=sys.stderr)
        print("You need to run this script with 'sudo'", file=sys.stderr)
        sys.exit(1)

    print("Created backup of Spotlight configuration", file=sys.stderr)
    print("If this script goes wrong or you want to revert, run:", file=sys.stderr)
    print("***", file=sys.stderr)
    print(f"    sudo cp {backup_path} {SPOTLIGHT_PLIST_PATH}", file=sys.stderr)
    print("    sudo launchctl stop com.apple.metadata.mds", file=sys.stderr)
    print("    sudo launchctl start com.apple.metadata.mds", file=sys.stderr)
    print("***", file=sys.stderr)


def get_paths_to_ignore(root: Path, ignore_dirs: set[str]):
    """
    Generates a list of paths to ignore in Spotlight.

    Args:
        root: The root directory to search under.
        ignore_dirs: Set of directory names to ignore.

    Yields:
        Path objects for directories that should be ignored in Spotlight.
    """
    root = Path(root).resolve()
    for path in get_dir_paths_under(root):
        if path.name in ignore_dirs:
            # Check this path isn't going to be ignored by a parent path.
            #
            # e.g. consider the path
            #
            #       ./dotorg/node_modules/koa/node_modules
            #
            # We're also going to ignore the path
            #
            #       ./dotorg/node_modules
            #
            # so adding an ignore for this deeper path is unnecessary.
            try:
                relative_path = path.relative_to(root)
            except ValueError:
                # Path is not relative to root, skip it
                continue

            relative_parts = relative_path.parts

            if any(parent_dir in ignore_dirs for parent_dir in relative_parts[:-1]):
                continue

            yield path


def get_current_ignores():
    """
    Returns a list of paths currently ignored by Spotlight.

    Returns:
        A set of path strings currently excluded from Spotlight indexing.

    Raises:
        SystemExit: If unable to read the Spotlight configuration.
    """
    try:
        output = subprocess.check_output(
            [
                "plutil",
                # Get the value of the "Exclusions" key as XML
                "-extract",
                "Exclusions",
                "xml1",
                # Send the result to stdout
                "-o",
                "-",
                SPOTLIGHT_PLIST_PATH,
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print("Failed to read Spotlight configuration", file=sys.stderr)
        print(f"Error: {e.stderr.decode() if e.stderr else str(e)}", file=sys.stderr)
        print("You may need to run this script with 'sudo'", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("'plutil' command not found", file=sys.stderr)
        print("This script requires macOS", file=sys.stderr)
        sys.exit(1)

    # The result of this call will look something like:
    #
    #
    #     <?xml version="1.0" encoding="UTF-8"?>
    #     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    #     <plist version="1.0">
    #     	<array>
    #     		<string>/Users/alexwlchan/repos/pipeline/target</string>
    #     		<string>/Users/alexwlchan/repos/pipeline/node_modules</string>
    #     	</array>
    #     </plist>
    #
    try:
        return {s.text for s in ET.fromstring(output).iter("string") if s.text}
    except ET.ParseError as e:
        print("Failed to parse Spotlight configuration XML", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def ignore_path_in_spotlight(path: Path, dry_run: bool = False):
    """
    Ignore a path in Spotlight, if it's not already ignored.

    Args:
        path: The path to ignore in Spotlight.
        dry_run: If True, don't actually modify the Spotlight configuration.

    Raises:
        SystemExit: If unable to update the Spotlight configuration.
    """
    already_ignored = get_current_ignores()

    path_str = str(path.resolve())
    if path_str in already_ignored:
        return

    if dry_run:
        return

    try:
        subprocess.check_call(
            [
                "plutil",
                # Insert at the end of the Exclusions list
                "-insert",
                f"Exclusions.{len(already_ignored)}",
                # The path to exclude
                "-string",
                path_str,
                # Path to the Spotlight plist on Catalina
                SPOTLIGHT_PLIST_PATH,
            ],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to add '{path_str}' to Spotlight exclusions", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        print("Continuing with remaining paths...", file=sys.stderr)


def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description=(
            "This script will tell Spotlight to ignore any folder in/under PATH "
            "that's named 'node_modules' or 'target'. "
            "Note: This script requires sudo privileges."
        ),
        epilog=(
            "Written by Alex Chan. "
            "See https://alexwlchan.net/2021/08/ignore-lots-of-folders-in-spotlight/"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="Root path to search for directories to ignore (default: current directory)",
    )
    parser.add_argument(
        "--also-ignore",
        "-a",
        nargs="+",
        metavar="DIR",
        help="Additional directory names to ignore beyond the defaults (e.g., --also-ignore .vscode .idea)",
    )
    parser.add_argument(
        "--skip-defaults",
        action="store_true",
        help="Skip the built-in default ignore directories",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be ignored without making changes",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List directories currently ignored by Spotlight",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s 1.0.0",
        help="Show script version",
    )

    args = parser.parse_args()

    # Check if running with sudo/root privileges
    # (Done after parsing to allow --help to work without sudo)
    if os.geteuid() != 0:
        print("Error: This script must be run with sudo privileges", file=sys.stderr)
        print("Please run:", file=sys.stderr)
        print(f"    sudo python3 {sys.argv[0]} {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print("Currently ignored directories:")
        try:
            current_ignores = get_current_ignores()
        except FileNotFoundError:
            # Fallback if plutil missing, though checked in get_current_ignores
            sys.exit(1)

        if not current_ignores:
            print("  (None)")
        else:
            for path in sorted(current_ignores):
                print(f"  {path}")
        return

    root = args.path.resolve()

    # Build the set of directories to ignore based on flags
    ignore_dirs: set[str] = set()
    if not args.skip_defaults:
        ignore_dirs.update(IGNORE_DIRECTORIES)
    if args.also_ignore:
        ignore_dirs.update(args.also_ignore)

    if not ignore_dirs:
        print(
            "Error: No directories to ignore. Use --also-ignore or remove --skip-defaults.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Ignoring directories: {', '.join(sorted(ignore_dirs))}")
    if args.dry_run:
        print("(Dry run: No changes will be made)")
    print()

    if not args.dry_run:
        create_backup_of_spotlight_plist()

    print("The following paths will be ignored by Spotlight")
    paths_added = 0
    for path in get_paths_to_ignore(root=root, ignore_dirs=ignore_dirs):
        ignore_path_in_spotlight(path, dry_run=args.dry_run)
        print(path)
        paths_added += 1

    if paths_added == 0:
        print("No new paths found to ignore")
        return

    print(f"\nAdded {paths_added} path(s) to Spotlight exclusions")

    if args.dry_run:
        return

    print("Restarting Spotlight indexing service...")

    # Restart the Spotlight metadata server to apply changes
    try:
        subprocess.check_call(
            ["launchctl", "stop", "com.apple.metadata.mds"],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print("Warning: Failed to stop Spotlight service", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        print("You may need to restart manually", file=sys.stderr)
    except FileNotFoundError:
        print("Warning: 'launchctl' command not found", file=sys.stderr)
        print("This script requires macOS", file=sys.stderr)

    try:
        subprocess.check_call(
            ["launchctl", "start", "com.apple.metadata.mds"],
            stderr=subprocess.PIPE,
        )
        print("Spotlight service restarted successfully")
    except subprocess.CalledProcessError as e:
        print("Warning: Failed to start Spotlight service", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        print("You may need to restart manually", file=sys.stderr)
    except FileNotFoundError:
        print("Warning: 'launchctl' command not found", file=sys.stderr)
        print("This script requires macOS", file=sys.stderr)


if __name__ == "__main__":
    main()
