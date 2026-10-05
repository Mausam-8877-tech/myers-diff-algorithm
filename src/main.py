# import sys


# def main() -> int:
#     if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
#         print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
#         return 2
#     command, a_path, b_path = sys.argv[1:]
#     # TODO: read both files as raw bytes (brief, Section 2), then print the listing.
#     return 0


# raise SystemExit(main())


import sys


def read_lines(path):
    # Read the whole file as raw bytes (no text decoding, \r is kept)
    with open(path, "rb") as f:
        data = f.read()

    # Split on the newline byte
    lines = data.split(b"\n")

    # A final \n leaves an empty last piece: drop it.
    # This also makes an empty file give [] (no lines).
    if lines[-1] == b"":
        lines.pop()

    return lines


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]

    # Read both files. If either cannot be read, print nothing on stdout,
    # an error on stderr, and exit with code 2.
    try:
        a = read_lines(a_path)
        b = read_lines(b_path)
    except OSError as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        return 2

    # Temporary check (will be removed in Step 7): show line counts on stderr
    print(f"A has {len(a)} lines, B has {len(b)} lines", file=sys.stderr)
    print(a, file=sys.stderr)
    print(b, file=sys.stderr)
    return 0


raise SystemExit(main())
