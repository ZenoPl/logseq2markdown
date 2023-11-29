"""
Parse Logseq Markdown files to create proper Markdown with (or without) frontmatter.
"""
import os
import re
from typing import Optional

from rich import print as rprint


def get_list_of_files_from_dir(
    dirname: str, ext: Optional[list[str]] = None
) -> tuple[list[str], list[str]]:
    """Returns tuple of lists: files and subdirectories. Starting at dirname and going recursively.

    Modified from stackoverflow answer:
    https://stackoverflow.com/questions/18394147/how-to-do-a-recursive-sub-folder-search-and-return-files-in-a-list#59803793

    Args:
        dirname (str): path do directory we want a file list of, recursively
        ext (Optional[list[str]], optional): List of file extensions we're looking for.
            Extensions should be provided without leading '.', i.e ["json"] NOT [".json"].
            Defaults to None.

    Returns:
        tuple[list[str], list[str]]: touple of: list of all files with full paths that were
        found in and under dirname (recursively).
        If ext list is set list contains only files with extensions provided
        AND
        list of all subfolders that were found under dirname (not including dirname)
    """
    subdirectories: list[str] = []
    files: list[str] = []

    for f in os.scandir(path=dirname):
        if f.is_dir():
            subdirectories.append(f.path)

        if f.is_file():
            if not ext:
                files.append(f.path)
            elif os.path.splitext(p=f.name)[1].lower()[1:] in ext:
                files.append(f.path)

    for d in subdirectories:
        f, sd = get_list_of_files_from_dir(dirname=d, ext=ext)
        subdirectories.extend(sd)
        files.extend(f)
    return files, subdirectories


def logseq2markdown(filename: str, encoding: str = "utf-8") -> str:
    """_summary_

    Args:
        filename (str): _description_
        encoding (str, optional): _description_. Defaults to "utf-8".

    Returns:
        str: _description_
    """
    logseq_lines: list[str] = []
    with open(filename, "rt", encoding=encoding) as fh:
        logseq_lines.extend(fh.readlines())

    logseq_lines_no: int = len(logseq_lines)

    mk_frontmatter: str = "---\n"
    mk_content: list[str] = []
    mk_inlist: bool = False
    for line_index in range(
        0, logseq_lines_no
    ):  # !!! I'm getting index of list for purpose here !!!
        line: str = logseq_lines[line_index]

        # Sanitizing lines before interpreting:
        ## skipping empty lines
        if line.startswith(("-\n", "\n")):
            mk_inlist = False
            continue

        ## removing logseq imposed list openings or "  " from each line that have it
        if line.startswith(("- ", "  ")):
            line = line[2:]

        line = line.rstrip()

        # Parsing lines with special meaning:
        ## checking for title
        if line.startswith("# "):
            mk_frontmatter += "title: " + line[2:] + "\n"
            mk_inlist = False
            continue

        ## checking if line is "logseq.order-list-type:: <...>"
        pattern = re.compile(r"logseq.[A-Za-z0-9-]+:: number")
        results1 = pattern.findall(line)
        if results1:
            mk_content.pop()
            prev_line = mk_content.pop().replace("\t", "  ")
            mk_content.append(f"{prev_line}1. {logseq_lines[line_index - 1][2:]}")
            continue

        ## checking if line is an attribute
        pattern = re.compile(r"[A-Za-z0-9-]+::\s")
        results2 = pattern.findall(line)
        if results2:
            mk_frontmatter += line.replace(results2[0], results2[0][0:-2] + " ") + "\n"
            mk_inlist = False
            continue

        ## we're in list
        # pattern = re.compile(r"\t+- ")
        # results3 = pattern.findall(line)
        # if results3:
        #     if mk_inlist:
        #         prev_line = mk_content.pop().replace("\t", "  ")
        #         mk_content.append(f"{prev_line}{line.replace("\t", "  ")}\n")
        #     else:
        #         mk_content.append(line.replace("\t", "  ") + "\n")
        #         mk_inlist = True

        #     continue

        mk_inlist = False

        ## replacing tabs with double spaces
        line = line.replace("\t", " ")

        ## line is a paragraph
        mk_content.append(line + "\n")

    mk_frontmatter += "---\n\n"
    return mk_frontmatter + "\n".join(mk_content)


if __name__ == "__main__":
    rprint(logseq2markdown("data/Homepage.md"))
