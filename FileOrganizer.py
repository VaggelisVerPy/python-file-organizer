from pathlib import Path
import shutil
import argparse
from collections import defaultdict

EXT_MAP = {
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".tiff": "Images", ".svg": "Images",

    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".odt": "Documents", ".rtf": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".ppt": "Documents", ".pptx": "Documents",
    
    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio", ".flac": "Audio", ".ogg": "Audio",
    
    ".mp4": "Video", ".mkv": "Video", ".mov": "Video", ".avi": "Video", ".wmv": "Video",
    
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives", ".tar": "Archives", ".gz": "Archives",
    
    ".py": "Code", ".js": "Code", ".java": "Code", ".c": "Code", ".cpp": "Code", ".html": "Code", ".css": "Code", ".sh": "Code",
}

MULTI_EXTENSIONS = {".tar.gz", "tar.bz2"}

def get_extension_lower(path: Path) -> str:
    name = path.name.lower()
    for type in MULTI_EXTENSIONS:
        if name.endswith(type):
            return type
    return path.suffix.lower()

def resolve_category(ext: str) -> str:
    return EXT_MAP.get(ext, "Others")

def make_unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    i = 1
    
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def organize_iterative(root: Path, dry_run: bool = True, include_hidden: bool = True, follow_symlinks: bool = True):
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Path does not exist or is not a directory: {root}")
    
    stack = [root]
    summary = defaultdict(int)
    errors = []
    processed = 0

    while stack:
        current = stack.pop()
        try:
            for entry in current.iterdir():
                if not include_hidden and entry.name.startswith("."):
                    continue

                if entry.is_symlink() and not follow_symlinks:
                    continue

                if entry.is_dir():
                    if entry.name in set(EXT_MAP.values()) | {"Others"}:
                        continue
                    stack.append(entry)
                elif entry.is_file():
                    processed += 1
                    ext = get_extension_lower(entry)
                    category = resolve_category(ext)
                    target_dir = root / category
                    target_dir.mkdir(parents = True, exist_ok = True)
                    target_path = target_dir / entry.name

                    if dry_run:
                        print(f"[DRY] Would Move: {entry} -> {target_path}")
                        summary[category] += 1
                    else:
                        try:
                            unique_target = make_unique_target(target_path)
                            shutil.move(str(entry), str(unique_target))
                            print(f"Moved: {entry} -> {unique_target}")
                            summary[category] += 1
                        except Exception as e:
                            errors.append((entry, str(e)))
                            print(f"Error moving {entry}: {e}")
                else:
                    continue
        
        except PermissionError as pe:
            errors.append((current, f"PermissionError: {pe}"))
            print(f"PermissionError accessing {current}: {pe}")
        except Exception as e:
            errors.append((current, str(e)))
            print(f"Error reading {current}: {e}")

    print("\n--- SUMMARY ---")
    print(f"Root scanned: {root}")
    print(f"Total files inspected: {processed}")
    for cat, count in summary.items():
        print(f"{cat}: {count}")
    print(f"Errors: {len(errors)}")
    if errors:
        print("Some errors occured (first 10 shown):")
        for e in errors[:10]:
            print("-", e[0], "->", e[1])

def parse_args():
    p = argparse.ArgumentParser(description = "Organize files into category folders recursively.")
    p.add_argument("path", help = "Root folder path to organize")
    p.add_argument("--no-dry", dest = "dry_run", action = "store_false", help = "Perform moves (default is dry-run)")
    p.add_argument("--include-hidden", action = "store_true", help = "Include hidden files and folders")
    p.add_argument("--follow-symlinks", action = "store_true", help = "Follow symbolic links (use with caution)")
    return p.parse_args()

def main():
    root = Path("D:/Program Test").expanduser().resolve()
    dry_run = False
    include_hidden = True
    follow_symlinks = True

    print(f"Root folder: {root}")
    print("Dry-run mode:" if dry_run else "Executing moves:")
    
    organize_iterative(root, dry_run=dry_run, include_hidden = include_hidden, follow_symlinks=follow_symlinks)

if __name__ == "__main__":
    main()