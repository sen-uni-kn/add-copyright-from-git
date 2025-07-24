# SPDX-FileCopyrightText: 2025 Raffael Senn <raffael.senn@uni-konstanz.de>
#
# SPDX-License-Identifier: MIT

import argparse
import datetime
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable
from reuse.project import Project
from reuse.report import ProjectReport
from reuse.cli import annotate
from reuse import ReuseInfo, _annotate, copyright

SHORTLOG_NAME_EMAIL = r"^\s*\d*\s+(.*? <.*?>)$"
BLAME_NAME_EMAIL = r"^author (.*?)\s*\nauthor-mail (<.*?>)\s*\n"

parser = argparse.ArgumentParser(
    description="Add missing copyright headers to files based on git blame information.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "-s",
    "--use-shortlog",
    action="store_true",
    help="Use git shortlog to get author names instead of git blame.",
)


def main():
    """
    Scans the current project directory for source files missing copyright headers,
    generates appropriate copyright lines using Git history (either via blame or shortlog),
    and inserts standardized copyright headers into those files.

    The function:
    - Parses command-line arguments to determine whether to use 'git blame' or 'git shortlog' for copyright attribution.
    - Loads the project with cwd as root.
    - Iterates over files missing copyright headers.
    - For each file, generates copyright headers based on git commit information.

    Outputs the result of header insertion to stdout.
    """

    args = parser.parse_args()
    use_shortlog = args.use_shortlog

    get_copyright = (
        get_copyright_with_blame if not use_shortlog else get_copyright_with_shortlog
    )

    add_copyright_to_missing_files(Path.cwd(), get_copyright)


def add_copyright_to_missing_files(
    root: Path, get_copyright_func: Callable[[Path, str], set[str]]
) -> None:
    """
    Add copyright headers to files in the project root based on git history.

    :param root: The root directory of the project.
    :param get_copyright_func: Function to get copyright lines from git history.
    """
    project = Project.from_directory(root)
    template, commented = annotate.get_template(template_str=None, project=project)
    year = str(datetime.date.today().year)

    report = ProjectReport.generate(project)
    for file in report.files_without_copyright:
        copyright_lines = get_copyright_func(file, year)

        reuse_info = ReuseInfo(
            spdx_expressions=set(),
            copyright_lines=copyright_lines,
            contributor_lines=set(),
        )

        # This function prints the file name to stdout
        # and adds the copyright header to the file.
        _annotate.add_header_to_file(
            file,
            reuse_info=reuse_info,
            template=template,
            template_is_commented=commented,
            style=None,
            force_multi=False,
            skip_existing=False,
            merge_copyrights=False,
            replace=True,
            out=sys.stdout,
        )


def get_copyright_with_blame(file: Path, year: str) -> set[str]:
    """Get copyright lines from git blame for a given file.
    Args:
        file (Path): The file to analyze.
        year (str): The current year for the copyright header.
    Returns:
        set[str]: A set of copyright lines.
    """
    res = subprocess.run(
        ["git", "blame", str(file), "--incremental"],
        check=True,
        capture_output=True,
    )
    output = res.stdout.decode()
    authors = set(re.findall(BLAME_NAME_EMAIL, output, re.MULTILINE))
    return set(
        copyright.make_copyright_line(f"{name} {email}", year)
        for name, email in authors
    )


def get_copyright_with_shortlog(file: Path, year: str) -> set[str]:
    """Get copyright lines from git shortlog for a given file.

    Args:
        file (Path): The file to analyze.
        year (str): The current year for the copyright header.

    Raises:
        RuntimeError: If a line cannot be parsed correctly.

    Returns:
        set[str]: A set of copyright lines.
    """
    res = subprocess.run(
        ["git", "shortlog", "-e", "-n", str(file)],
        check=True,
        capture_output=True,
    )
    lines = res.stdout.decode().splitlines()
    copyright_lines: set[str] = set()
    for line in lines:
        match = re.match(SHORTLOG_NAME_EMAIL, line)
        if not match:
            raise RuntimeError(f"Could not parse copyright line: {line}")
        copyright_holder = match.group(1)
        copyright_lines.add(copyright.make_copyright_line(copyright_holder, year))
    return copyright_lines


if __name__ == "__main__":
    main()
