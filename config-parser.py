#!/usr/bin/env python3
# Copyright (c) TOLOSAT 2026
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import re
import tempfile


CONFIG_DECLARATION = re.compile(r"^\s*(?:menu)?config\s+([A-Za-z0-9_]+)\s*$")


def write_generated_file(filename, content):
    """Atomically publish generated content without changing unchanged files."""
    try:
        with open(filename, "r", encoding="utf-8") as existing_file:
            if existing_file.read() == content:
                return
        mode = os.stat(filename).st_mode & 0o777
    except FileNotFoundError:
        mode = 0o644

    output_directory = os.path.dirname(filename) or "."
    descriptor, temporary_filename = tempfile.mkstemp(
        prefix=f".{os.path.basename(filename)}.", dir=output_directory, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as output_file:
            output_file.write(content)
        os.chmod(temporary_filename, mode)
        os.replace(temporary_filename, filename)
    finally:
        if os.path.exists(temporary_filename):
            os.unlink(temporary_filename)


def parse_kconfig_symbols(kconfig_files):
    """Return the symbols owned by the supplied Kconfig descriptions."""
    symbols = set()
    for filename in kconfig_files:
        with open(filename, "r", encoding="utf-8") as kconfig_file:
            for line in kconfig_file:
                match = CONFIG_DECLARATION.match(line)
                if match:
                    symbols.add(match.group(1))
    return symbols


def is_owned_option(option, owned_symbols):
    return option.startswith("CONFIG_") and option[7:] in owned_symbols


def parse_config(config_file, output_dir, owned_symbols):
    # Define the output header file
    output_file = os.path.join(output_dir, 'autoconf.h')

    content = [f"""/**
 * @file    autoconf.h
 * @brief   Header file for buffer configuration
 * @author  Auto-generated
 *
 * @copyright Copyright (c) TOLOSAT 2026
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef AUTOCONF_H
#define AUTOCONF_H

"""]

    with open(config_file, 'r', encoding='utf-8') as config:
        for line in config:
            line = line.strip()

            # Ignore empty lines
            if not line:
                continue

            # Ignore comments in the .config file
            if line.startswith("#"):
                if "is not set" in line:
                    # Handle disabled config options
                    option = line.split()[1]
                    if is_owned_option(option, owned_symbols):
                        content.append(f"// {option} is not set\n")
                continue

            # Handle config options that are set
            if "=" in line:
                option, value = line.split("=", 1)
                option = option.strip()
                value = value.strip()

                if not is_owned_option(option, owned_symbols):
                    continue

                if value == "y":
                    content.append(f"#define {option} y\n")
                elif value == "n":
                    content.append(f"// {option} is not set\n")
                else:
                    content.append(f"#define {option} {value}\n")

    content.append("\n#endif /* AUTOCONF_H */\n")
    write_generated_file(output_file, "".join(content))


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate autoconf.h from a .config file.")
    parser.add_argument('-i', '--input', required=True, help="Path to the input .config file")
    parser.add_argument('-o', '--output', required=True, help="Path to the output directory")
    parser.add_argument(
        '-k',
        '--kconfig',
        action='append',
        required=True,
        help="Kconfig file declaring symbols to include (repeatable)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Call the parsing function
    parse_config(args.input, args.output, parse_kconfig_symbols(args.kconfig))


if __name__ == "__main__":
    main()
