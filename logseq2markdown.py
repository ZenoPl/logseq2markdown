"""
Parse Logseq Markdown file to create a string of standard Markdown with Frontmatter.
Taking into consideration priorities of running the code as being FAST vs being PRECISE
I'm being PRECISE first and FAST later.
That's why this code may parse Logseq file content multiple times.
TODO: #2 Optimize the code when and if it's possible
"""
import re

# Frontmatter consts for start and end of Frontmatter YAML heading in Markdown
FRONTMATTER_START_STR = "---\n"
FRONTMATTER_END_STR = "---\n\n"
FRONTMATTER_PARAM_NAME_REGEXP: str = r"[A-Za-z0-9-_.]+::\s"
LOGSEQ_LIST_REGEXP: str = r"^[\s\t]*- "


def load_logseq_sanitized(file_path: str, encoding: str = "utf-8") -> list[str]:
    """Loads file from `file_path`, converts it to a list of strings and sanitizes each line.\n
    Each line is created by splitting source by newline ("\\n") character.\n
    Each line is processed with rules below:
    - empty lines ("\\n", "- \\n", "-\\n", "- \\n") are removed as it helps with parsing later on;
    - removing ("- ", "  ") from the beginning of each line to
    remove Logseq "everyting is a list" approach
    - first "\\t" removed as it indicates a real Markdown list element that
    should start at the beginning of a line;
    - newline char ("\\n") is removed from the end of each line as it helps with parsing later on;

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
        # we skip empty lines
        if line in ("\n", "- \n", "-\n", "- \n"):
            continue

        # we remove "- " or "  " from the beginning of line as
        # it's Logseq specific "everyghing is a list" approach
        if line.startswith(("- ", "  ")):
            line = line[2:]

        # we remove first occurance of tab character ("\\t") from a line as
        # it's indicating list item
        if line.startswith("\t"):
            line = line.replace("\t", "", 1)

        return_lines.append(line)

    return return_lines


def logseq2markdown(logseq_lines: list[str]) -> str:
    """Goes through list of Logseq sanitized lines (provided by `load_logseq_sanitized()`) and
    translates them to proper Markdown and Frontmatter.

    Args:
        logseq_lines (list[str]): List of sanitized lines from Logseq file loader

    Returns:
        str: String containing Frontmatter header in YML format followed by proper Markdown.
    """
    mk_content: list[str] = []

    # Using dict here as we don't want to have duplicate parameter names in Frontmatter
    # (each should have unique indentifier).
    # TODO: #4 Raise an Exception if already existing frontmatter parameter is overwritten
    mk_frontmatter: dict[str, str] = {}

    param_regex = re.compile(FRONTMATTER_PARAM_NAME_REGEXP)
    logseq_list_regexp = re.compile(LOGSEQ_LIST_REGEXP)

    for line in logseq_lines:
        params_result = param_regex.findall(line)
        logseq_list_result = logseq_list_regexp.findall(line)

        # if line containts "logseq.order-list-type:: number" it should be
        # numbered list and this line should be ommited
        if -1 != line.find("logseq.order-list-type:: number"):
            line = mk_content.pop()
            line = line.lstrip("\n")
            line = line.replace("- ", "1. ", 1)
            line = line.replace("\t", "    ")
            mk_content.append(line)

        # if line containts "logseq.order-list-type:: bulllet" it should be
        # bullet point list and this line should be ommited
        elif -1 != line.find("logseq.order-list-type:: bullet"):
            line = mk_content.pop()
            line = line.lstrip("\n")
            line = line.replace("- ", "* ", 1)
            line = line.replace("\t", "    ")
            mk_content.append(line)

        # if line is proper unordered list we parse it as such
        elif logseq_list_result:
            line = line.lstrip("\n")
            line = line.replace("\t", "    ")
            mk_content.append(line)

        # if line starts with "# " (meaning h1 in html) we parse it as Frontmatter "title:" param
        elif line.startswith("# "):
            mk_frontmatter["title"] = '"' + line[2:].strip() + '"'

        # if line doesn't have any Logseq-specific parameters like numbered or bullet list in it
        # and has Frontmatter param format we add it to Frontmatter header
        elif params_result:
            mk_frontmatter[params_result[0][0:-3]] = line[len(params_result[0]) :]

        # otherwise we add it to content as any other Markdown element
        else:
            mk_content.append("\n" + line)

    return_string: str = ""
    if mk_frontmatter:
        return_string = (
            FRONTMATTER_START_STR
            + "\n".join(
                [
                    f"{fm_item[0]}: {fm_item[1].strip()}"
                    for fm_item in list(mk_frontmatter.items())
                ]
            )
            + "\n"
            + FRONTMATTER_END_STR
        )

    return return_string + "".join(mk_content)


if __name__ == "__main__":
    logseq2markdown(load_logseq_sanitized(file_path="examples/in/Homepage.md"))
