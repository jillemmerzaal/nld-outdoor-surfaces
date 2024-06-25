import os
from pathlib import Path
from typing import List, Tuple
from support_functions.engine import engine


def extract_filestruct(fld: str) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """
    Extracts file structure up to 5 levels deep from the given root folder.

    Args:
    - fld: Root folder to operate on.

    Returns:
    - level1: 1st level of sorting in file tree.
    - level2: 2nd level of sorting in file tree.
    - level3: 3rd level of sorting in file tree.
    - level4: 4th level of sorting in file tree.
    - level5: 5th level of sorting in file tree.
    """

    fl = engine(path=fld, extension=".zoo")

    # Determine levels
    level1, level2, level3, level4, level5 = [], [], [], [], []

    subdirs = get_subdirectories(fld)
    indxfld = len(Path(fld).parts)

    for subdir in subdirs:
        parts = Path(subdir).parts
        if len(parts) == indxfld + 1:
            level1.append(parts[-1])
        elif len(parts) == indxfld + 2:
            level2.append(parts[-1])
        elif len(parts) == indxfld + 3:
            level3.append(parts[-1])
        elif len(parts) == indxfld + 4:
            level4.append(parts[-1])
        elif len(parts) == indxfld + 5:
            level5.append(parts[-1])

    # Remove duplicates and sort levels
    level1 = sorted(set(level1))
    level2 = sorted(set(level2))
    level3 = sorted(set(level3))
    level4 = sorted(set(level4))
    level5 = sorted(set(level5))

    return level1, level2, level3, level4, level5


def get_subdirectories(root_dir: str) -> Tuple[List[str], List[str]]:
    """
    Lists all subfolders and files under the given folder recursively.

    Args:
    - root_dir: Path to the root directory.

    Returns:
    - subdirs: List of paths of each subfolder.
    - files: List of paths of each file.
    """
    subdirs = []
    files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            subdirs.append(os.path.join(dirpath, dirname))
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    return subdirs, files



