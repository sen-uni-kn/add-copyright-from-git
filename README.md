<!--
SPDX-FileCopyrightText: 2025 Raffael Senn <raffael.senn@uni-konstanz.de>

SPDX-License-Identifier: MIT
-->

# add-copyright-from-git

[![REUSE status](https://api.reuse.software/badge/github.com/sen-uni-kn/add-copyright-from-git)](https://api.reuse.software/info/github.com/sen-uni-kn/add-copyright-from-git)

Add missing copyright headers to files based on git author information.
Helps to make your project [reuse](https://reuse.software/) compliant.

The script scans the current working directory for files that do not
contain a copyright header. It ignores files that would not be covered
by `reuse lint`. If a file is missing a copyright header, all authors
that are present in the `git blame` output (or `git shortlog` if the
`--use-shortlog` flag is set) are added to the header.

## Installation

You can install this script using pip (requires Python 3.12+):

```sh
pip install .
```

Furthermore git is required to be installed and available in the PATH,
as the script uses git commands to determine authorship information.

## Usage

We recommend to commit (or stash) your changes before running the script,
as it will modify files in the current working directory. After running
the script, you can then review the changes and modify them as needed
before committing.

Run the script from the command line:

```sh
add-copyright-from-git [--use-shortlog]
```

The script analyzes the current working directory and adds missing
copyright headers to files based on git blame information. Use the
`--use-shortlog` flag to use git shortlog instead of git blame for
author detection.

The script will not modify files that already contain a copyright header.

## Dependencies

- Python 3.12 or newer
- [reuse](https://github.com/fsfe/reuse-tool) python package
- [git](https://git-scm.com/) command line tool
