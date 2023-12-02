"""
Parse Logseq Markdown file to create proper Markdown adding params as frontmatter.
Taking into consideration being FAST and/or PRECISE I'm being PRECISE over FAST.
That's why it parses lines of Logseq file multiple times.
TODO: #2 Optimize the code when and if it's plausible
"""
import re

# TODO: #1 Remove `rich` dependency (used for now to help with development)
# Yeah I know: W0622 "redefine built-in print" but I need it for now.
# btw. `pip install rich` to use this to see nice output from Python.
from rich import print as rprint

# Frontmatter consts (without newline as it's added later)
STR_FRONTMATTER_START = "---\n"
STR_FRONTMATTER_END = "---\n\n"


def load_logseqmd_file_sanitized(file_path: str, encoding: str = "utf-8") -> list[str]:
    """Loads file from `file_path` as list of sanitized lines split by newline ("\\n") character.\n
    Each line is processed with rules below:
    - newline ("\\n") removed;\n
    - empty lines ("\\n", "- \\n", "-\\n") removed;\n
    - first "\\t" removed;\n
    - ... any other "\\t" left are replaced by double spaces as it means real list item;\n

    Args:
        file_path (str): Proper path to Logseq *.md file
        encoding (str): Encoding parameter provided to `open` Python function. Defaults to "utf-8".

    Returns:
        list[str]: list of sanitized lines from `file_path` Logseq file
    """
    with open(file_path, "r", encoding=encoding) as f:
        lines: list[str] = f.readlines()

    return_lines: list[str] = []
    for line in lines:
        if line in ("\n", "- \n", "-\n"):
            continue

        if line.startswith("- "):
            line: str = line[2:]

        if line.startswith("\t"):
            line = line.replace("\t", "", 1)

        line = line.replace("\t", "  ")
        line = line.strip("\n")

        return_lines.append(line)

    return return_lines


def logseq_lines_to_markdown(logseq_lines: list[str]) -> str:
    """_summary_

    Args:
        logseq_lines (_type_): _description_

    Returns:
        str: _description_
    """
    mk_frontmatter: str = STR_FRONTMATTER_START
    mk_content: list[str] = []

    for index, line in enumerate(logseq_lines):
        # if line starts with "# " it's frontmatter "title:" parameter
        if line.startswith("# "):
            mk_frontmatter += "title: " + line[2:] + "\n"
            continue

        # if it's frontmatter parameter we add it to frontmatter string
        pattern_attributes = re.compile(r"[A-Za-z0-9-]+::\s")
        results_attributes = pattern_attributes.findall(line)
        if results_attributes:
            mk_frontmatter += (
                line.replace(
                    results_attributes[0], results_attributes[0][0:-2] + " "
                ).strip()
                + "\n"
            )
            continue

        mk_content.append(line)

    return mk_frontmatter + STR_FRONTMATTER_END + "\n\n".join(mk_content)


if __name__ == "__main__":
    rprint(
        logseq_lines_to_markdown(
            load_logseqmd_file_sanitized(file_path="examples/in/Homepage.md")
        )
    )
