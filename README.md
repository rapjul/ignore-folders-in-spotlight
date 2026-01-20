# Ignore Folders in Spotlight

A Python script to automatically configure macOS Spotlight to ignore common development directories like `node_modules`, `target`, `build`, `dist`, `.venv`, and more.

## Why Use This?

Development projects often contain thousands of files in dependency directories (like `node_modules` or `vendor`) that you never need to search. Having Spotlight index these directories:

- 📉 Slows down your Mac with unnecessary indexing
- 🔍 Clutters your search results with irrelevant files  
- 💾 Wastes disk space storing indices you'll never use
- 🔋 Drains battery with constant re-indexing when files change

This script saves you from manually adding exclusions for every project by automatically finding and excluding these directories.

## Features

- ✅ Automatically finds and ignores common development directories
- 🎯 Supports multiple programming ecosystems (JavaScript, Python, Rust, Java, Go, PHP, Ruby, iOS, etc.)
- 🔧 Customizable with additional directories
- 💾 Creates automatic backups before making changes
- ⚡ Recursively scans your entire project tree
- 🛡️ Safety checks to avoid redundant exclusions

## Default Ignored Directories

By default, the script ignores these common development directories:

| Directory      | Used By                           |
|----------------|-----------------------------------|
| `node_modules` | Node.js/npm dependencies          |
| `target`       | Rust, Maven build output          |
| `build`        | Generic build output              |
| `dist`         | Distribution/build output         |
| `.venv`/`venv` | Python virtual environments       |
| `vendor`       | Go, PHP, Ruby dependencies        |
| `__pycache__`  | Python bytecode cache             |
| `.gradle`      | Gradle build artifacts (Java)     |
| `.next`        | Next.js build output              |
| `coverage`     | Test coverage reports             |
| `Pods`         | CocoaPods dependencies (iOS/macOS)|

## Quick Run (No Installation)

If you have [uv](https://docs.astral.sh/uv/) installed, you can run the script directly from git without cloning:

```bash
# Run directly from GitHub (replace with actual repository URL)
sudo uvx --from git+https://github.com/rapjul/ignore-folders-in-spotlight.git ignore-folders-in-spotlight ~/Projects

# With additional options
sudo uvx --from git+https://github.com/rapjul/ignore-folders-in-spotlight.git ignore-folders-in-spotlight --also-ignore .idea .vscode ~/Projects
```

## Installation

### Option 1: Traditional Installation

1. **Clone or download this repository:**

   ```bash
   git clone <repository-url>
   cd ignore-folders-in-spotlight
   ```

2. **Ensure Python 3 is installed:**

   ```bash
   python3 --version
   ```

### Option 2: Install with uv

If you have [uv](https://docs.astral.sh/uv/) installed:

```bash
# Install directly from git
uv tool install git+https://github.com/rapjul/ignore-folders-in-spotlight.git

# Run from anywhere
sudo ignore_folders_in_spotlight ~/Projects
```

## Usage

### Basic Usage

To scan the current directory and ignore all default directories:

```bash
sudo python3 ignore_folders_in_spotlight.py
```

### Scan a Specific Directory

```bash
sudo python3 ignore_folders_in_spotlight.py ~/Projects
```

### Add Additional Directories

Use `--also-ignore` (or `-a`) to add custom directories beyond the defaults:

```bash
# Ignore .vscode and .idea folders in addition to defaults
sudo python3 ignore_folders_in_spotlight.py --also-ignore .vscode .idea ~/Projects
```

### Use Only Custom Directories

Use `--skip-defaults` to ignore only your specified directories:

```bash
# Only ignore .git directories
sudo python3 ignore_folders_in_spotlight.py --skip-defaults --also-ignore .git ~/Projects
```

### Combine Options

```bash
# Skip defaults and ignore only cache and tmp directories
sudo python3 ignore_folders_in_spotlight.py --skip-defaults --also-ignore cache tmp ~/Projects
```

## Command-Line Options

| Option                        | Short | Description                                           |
|-------------------------------|-------|-------------------------------------------------------|
| `path`                        |       | Root directory to scan (default: current directory)   |
| `--also-ignore DIR [DIR ...]` | `-a`  | Additional directory names to ignore beyond defaults  |
| `--skip-defaults`             |       | Skip the built-in default ignore directories          |
| `--help`                      | `-h`  | Show help message and exit                            |

## Examples

### Example 1: Clean Up Your Development Folder

```bash
# Ignore all default directories under ~/Development
sudo python3 ignore_folders_in_spotlight.py ~/Development
```

### Example 2: Add IDE Folders

```bash
# Also ignore JetBrains and VS Code folders
sudo python3 ignore_folders_in_spotlight.py -a .idea .vscode ~/Projects
```

### Example 3: Just Git Repositories

```bash
# Only ignore .git folders (no other defaults)
sudo python3 ignore_folders_in_spotlight.py --skip-defaults -a .git ~/Code
```

## How It Works

1. **Scans recursively** through the specified directory
2. **Identifies directories** matching the ignore list
3. **Creates a backup** of your Spotlight configuration
4. **Adds exclusions** to Spotlight's plist file
5. **Restarts Spotlight** to apply changes


The script is smart enough to:

- Skip nested directories (e.g., won't add `/project/node_modules/lib/node_modules` if `/project/node_modules` is already excluded)
- Avoid duplicates (won't add paths already in Spotlight exclusions)
- Provide clear error messages and recovery instructions

## Requirements

- **macOS** (this script modifies macOS Spotlight configuration)
- **Python 3.x**
- **sudo privileges** (required to modify system Spotlight settings)

## Safety & Backups

Every time you run the script, it creates a backup of your Spotlight configuration on your Desktop:

```text
~/Desktop/Spotlight-V100.VolumeConfiguration.YYYY-MM-DD.HH-MM-SS.plist
```

### Restoring from Backup

If something goes wrong, you can restore the backup:

```bash
sudo cp ~/Desktop/Spotlight-V100.VolumeConfiguration.YYYY-MM-DD.HH-MM-SS.plist \
    /System/Volumes/Data/.Spotlight-V100/VolumeConfiguration.plist
sudo launchctl stop com.apple.metadata.mds
sudo launchctl start com.apple.metadata.mds
```

## Troubleshooting

### "This script must be run with sudo privileges"

The script needs elevated permissions to modify Spotlight settings. Run with `sudo`.

### "Could not create backup of Spotlight configuration"

Make sure you have write permissions to your Desktop and are running with `sudo`.

### Changes Not Applied

Try manually restarting Spotlight:

```bash
sudo launchctl stop com.apple.metadata.mds
sudo launchctl start com.apple.metadata.mds
```

## Contributing

Found a common development directory that should be included by default? Open an issue or pull request!

## Credits

Original script by [Alex Chan](https://alexwlchan.net/2021/08/ignore-lots-of-folders-in-spotlight/)

Enhanced with additional features and directory support.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**This script is provided as-is without any warranty or support.** Use at your own risk.

This is an enhanced version of the original script by Alex Chan, with additional features and expanded directory support.
