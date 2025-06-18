#!/usr/bin/env python3
"""
📄 extract.py — Extract code files into a structured Markdown document with syntax highlighting.

This script recursively scans target folders and exports the contents of selected file types
into a single markdown file with section headers and a folder-based table of contents (TOC).

🚀 Features:
- Includes only specific file types (default: .py, .toml)
- Excludes common folders like virtual environments and caches
- Organizes output by folder
- Generates syntax-highlighted code blocks in markdown
- Adds a clickable TOC to quickly navigate files
- Supports multiple target folders in a single command

🧠 Hardcoded settings:
- Allowed extensions: [".py", ".toml", ".md", ".txt", ".sh", ".dockerfile", ".yml", ".yaml", ".sql"]
- Excluded folders: ["venv", ".streamlit", "__pycache__", "site-packages", "bin"]
- Output file: files_content.md

🛠️ Usage:
Run the script from your terminal:

    python extract.py

To specify a particular project folder:

    python extract.py -f path/to/project

To specify multiple project folders:

    python extract.py -f folder1/ folder2/ folder3/

Output will be saved to:
    files_content.md (in the same folder where the script is run)

✅ Example:

    python extract.py -f alkemi/ tools/ src/

This will include only files with allowed extensions from the specified directories,
while skipping folders like `venv`, `.streamlit`, and others.
"""

import os
import argparse
from collections import defaultdict
import sys


# Hardcoded folders to always exclude
DEFAULT_EXCLUDE_FOLDERS = {"venv", ".streamlit", "__pycache__", "site-packages", "bin", ".git", "logs","alembic","output"}

# Add this set for git-specific files
GIT_SPECIFIC_FILES = {".gitignore", ".gitattributes", ".gitmodules"}


def should_exclude_path(path_parts, exclude_folders):
    return any(part in exclude_folders for part in path_parts)


def build_tree_structure(base_folder, exclude_folders, allowed_extensions, docker_files):
    tree = defaultdict(list)
    for root, dirs, files in os.walk(base_folder):
        path_parts = root.split(os.sep)
        if should_exclude_path(path_parts, exclude_folders):
            dirs[:] = []
            continue

        rel_root = os.path.relpath(root, base_folder)
        for f in sorted(files):
            # Check for both extension and specific Docker/entrypoint filenames
            if any(f.lower().endswith(ext) for ext in allowed_extensions) or f in docker_files:
                tree[rel_root].append(f)
    return tree


def generate_toc(tree):
    lines = ["# 📂 Project File Contents\n"]
    for folder in sorted(tree.keys()):
        indent_level = folder.count(os.sep)
        folder_name = os.path.basename(folder) if folder != "." else "."
        lines.append(f"{'  ' * indent_level}- 📁 **{folder_name}**")
        for filename in tree[folder]:
            rel_path = os.path.normpath(os.path.join(folder, filename))
            anchor = rel_path.replace(os.sep, "-").replace(".", "").lower()
            lines.append(f"{'  ' * (indent_level + 1)}- [`{filename}`](#{anchor})")
    lines.append("\n---\n")
    return "\n".join(lines)


def ensure_output_dir(output_dir):
    """Ensure the output directory exists, create if not."""
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"❌ Failed to create output directory '{output_dir}': {e}")
        sys.exit(1)


def validate_target_folders(target_folders):
    """Validate that all target folders exist and are directories."""
    for folder in target_folders:
        if not os.path.isdir(folder):
            print(f"❌ Target folder does not exist or is not a directory: {folder}")
            sys.exit(1)


def write_markdown_file(output_path, md_lines):
    """Write the markdown lines to the output file."""
    try:
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(md_lines))
    except Exception as e:
        print(f"❌ Failed to write output file '{output_path}': {e}")
        sys.exit(1)


def process_target_folder(target_folder, folder_name, exclude_folders, allowed_extensions, docker_files, venv_indicators, script_path, output_path, md_lines):
    """Process a single target folder and append its content to md_lines."""
    for root, dirs, files in os.walk(target_folder):
        found_venv = any(dir_name in venv_indicators for dir_name in dirs)
        path_parts = root.split(os.sep)
        if should_exclude_path(path_parts, exclude_folders):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        rel_root = os.path.relpath(root, target_folder)
        folder_path = rel_root if rel_root != "." else folder_name
        md_lines.append(f"## Folder: {folder_path}\n")
        if found_venv:
            md_lines.append(
                "> ℹ️ *Note: Contains a virtual environment folder (e.g., `venv`, `.venv`). Contents are excluded.*\n"
            )
        for filename in sorted(files):
            file_path = os.path.join(root, filename)
            abs_file_path = os.path.abspath(file_path)
            if abs_file_path in {script_path, output_path} or filename in GIT_SPECIFIC_FILES or filename == "output.md":
                print(f"[SKIP] {file_path} (script/output/git-specific)")
                continue
            if not (any(filename.lower().endswith(ext) for ext in allowed_extensions) or filename in docker_files):
                print(f"[SKIP] {file_path} (extension not allowed)")
                continue
            rel_file_path = os.path.join(folder_name, os.path.relpath(file_path, target_folder))
            anchor = rel_file_path.replace(os.sep, "-").replace(".", "").lower()
            md_lines.append(f'### File: `{rel_file_path}`\n<a name="{anchor}"></a>')
            ext = os.path.splitext(filename)[1].lower()
            code_lang = {
                ".py": "python",
                ".toml": "toml",
                ".md": "markdown",
                ".sh": "bash",
                ".dockerfile": "dockerfile",
                ".yml": "yaml",
                ".yaml": "yaml",
                ".sql": "sql",
                ".txt": "text",
            }.get(ext, "")
            if filename == "Dockerfile":
                code_lang = "dockerfile"
            elif filename in ["docker-compose.yml", "docker-compose.yaml"]:
                code_lang = "yaml"
            elif filename == "entrypoint.sh":
                code_lang = "bash"
            elif filename.endswith(".env.docker"):
                code_lang = "properties"
            md_lines.append(f"```{code_lang}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    md_lines.append(file.read())
            except Exception as e:
                md_lines.append(f"Error reading file: {e}")
                print(f"[ERROR] Could not read {file_path}: {e}")
            md_lines.append("```\n")


def main():
    """Main entry point for the script."""
    allowed_extensions = [".py", ".toml", ".md", ".txt", ".sh", ".dockerfile", ".yml", ".yaml", ".sql"]
    docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "entrypoint.sh", ".env.docker"]
    default_output_filename = "files_content.md"
    venv_indicators = {"venv", ".venv"}
    output_dir = "output"  # Hardcoded output directory

    parser = argparse.ArgumentParser(description="Extract code and structure into markdown.")
    parser.add_argument(
        "--target-folder",
        "-f",
        type=str,
        nargs="+",
        default=[os.getcwd()],
        help="Target folder(s) to extract from. Default is current directory. Can specify multiple folders.",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=default_output_filename,
        help="Output markdown file name. Default is 'files_content.md'.",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help="Additional folder names to exclude. Can be specified multiple times.",
    )
    args = parser.parse_args()

    target_folders = [os.path.abspath(folder) for folder in args.target_folder]
    validate_target_folders(target_folders)

    ensure_output_dir(output_dir)
    output_filename = args.output_file
    output_path = os.path.join(output_dir, output_filename)
    exclude_folders = DEFAULT_EXCLUDE_FOLDERS.union(set(args.exclude))
    script_path = os.path.abspath(__file__)

    combined_tree = defaultdict(list)
    for target_folder in target_folders:
        tree = build_tree_structure(target_folder, exclude_folders, allowed_extensions, docker_files)
        folder_name = os.path.basename(target_folder)
        for folder, files in tree.items():
            if folder == ".":
                folder_path = folder_name
            else:
                folder_path = os.path.join(folder_name, folder)
            combined_tree[folder_path].extend(files)

    md_lines = [generate_toc(combined_tree)]
    for target_folder in target_folders:
        folder_name = os.path.basename(target_folder)
        md_lines.append(f"# Target Folder: {folder_name}\n")
        process_target_folder(
            target_folder,
            folder_name,
            exclude_folders,
            allowed_extensions,
            docker_files,
            venv_indicators,
            script_path,
            output_path,
            md_lines,
        )
    write_markdown_file(output_path, md_lines)
    print(f"✅ Markdown file generated: {output_path}")
    if len(target_folders) > 1:
        print(
            f"   Included {len(target_folders)} folders: {', '.join(os.path.basename(folder) for folder in target_folders)}"
        )


if __name__ == "__main__":
    main()