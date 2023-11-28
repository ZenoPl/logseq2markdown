"""
Parse Logseq Markdown files to create proper Markdown with (or without) frontmatter.
"""
import os
from typing import Optional

# from rich import print as rprint


def get_list_of_files_from_dir(
    dirname: str, ext: Optional[list[str]] = None
) -> tuple[list[str], list[str]]:
    """Returns list of files and subdirectories as tuple starting at dirname and going recursively.
    If ext is supplied it returns only files with extension(s) provided in param.

    Modified from stackoverflow answer:
    https://stackoverflow.com/questions/18394147/how-to-do-a-recursive-sub-folder-search-and-return-files-in-a-list#59803793

    Args:
        dirname (str): _description_
        ext (Optional[list[str]], optional): List of file extensions this function is looking for.
            Extensions should be provided without leading '.', i.e ["json"] NOT [".json"].
            Defaults to None.

    Returns:
        tuple[list[str], list[str]]: _description_
    """
    subdirectories: list[str] = []
    files: list[str] = []

    for f in os.scandir(dirname):
        if f.is_dir():
            subdirectories.append(f.path)

        if f.is_file():
            if not ext:
                files.append(f.path)
            elif os.path.splitext(f.name)[1].lower()[1:] in ext:
                files.append(f.path)

    for d in subdirectories:
        f, sd = get_list_of_files_from_dir(d, ext)
        subdirectories.extend(sd)
        files.extend(f)
    return files, subdirectories


if __name__ == "__main__":
    pass
