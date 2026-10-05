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


def myers_distance(a, b):
    """Forward pass of Myers' algorithm.
    Returns D = the minimum number of deletions + insertions
    needed to turn sequence a into sequence b."""
    n = len(a)
    m = len(b)
    max_d = n + m
    offset = max_d
    # V[offset + k] = furthest x reached on diagonal k
    v = [0] * (2 * max_d + 2)

    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            # Choose: come DOWN from diagonal k+1, or RIGHT from diagonal k-1
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                x = v[offset + k + 1]          # down  = insert b[y]
            else:
                x = v[offset + k - 1] + 1      # right = delete a[x]
            y = x - k

            # Snake: follow free diagonal moves while lines match
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[offset + k] = x

            # Reached the bottom-right corner?
            if x >= n and y >= m:
                return d

    return max_d  # never reached: D is at most n + m



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
    d = myers_distance(a, b)
    print(f"D = {d}", file=sys.stderr)
    return 0



raise SystemExit(main())
