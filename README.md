# TAPAS Tools

This repository contains the shared build, configuration, quality, debugging,
and development tools used by TAPAS and projects built on top of it.

## Tools

| Tool | Purpose |
| --- | --- |
| `bsp-parser.py` | Generate TAPAS BSP configuration sources from a board description. |
| `config-parser.py` | Generate a scoped `autoconf.h` from a Kconfig `.config` file. |
| `crc32-gen.py` | Append the firmware CRC during final image generation. |
| `format-code.sh` | Apply clang-format to project-owned C and header files. |
| `qebab.py` | Provide an interactive hexadecimal TCP terminal for emulator communication. |
| `system-parser.py` | Generate application configuration sources from a system description. |
| `time-converter.py` | Convert TAPAS CUC/TAI timestamps and generate a time-setting telecommand. |
| `update-doc.sh` | Generate and validate Doxygen documentation. |

Device-description files used by the debugger are stored under `svd/`.

The scripts operate on paths supplied by their caller or on the caller's
working directory. Consumers can therefore mount this repository directly as
their `tools/` Git submodule without wrapper scripts.

## License

TOLOSAT-developed code is licensed under the Apache License 2.0. See
[`LICENSE`](LICENSE) for details. The SVD files remain subject to their
respective licenses; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
