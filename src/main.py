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


def myers_diff(a, b):
    """Myers' O(ND) diff.
    Returns the edit script as a list of (op, item) pairs:
      op = b" " keep, b"-" delete (only in a), b"+" insert (only in b)."""
    n = len(a)
    m = len(b)
    max_d = n + m
    offset = max_d
    v = [0] * (2 * max_d + 2)   # V[offset + k] = furthest x on diagonal k
    trace = []                  # trace[d] = V for diagonals -d..d after round d
    final_d = 0
    found = False

    # ---------- Forward pass (same as Step 5) ----------
    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                x = v[offset + k + 1]          # down  = insert
            else:
                x = v[offset + k - 1] + 1      # right = delete
            y = x - k
            while x < n and y < m and a[x] == b[y]:   # snake
                x += 1
                y += 1
            v[offset + k] = x
            if x >= n and y >= m:
                final_d = d
                found = True
                break
        if found:
            break
        # Save only diagonals -d..d (not the whole array)
        trace.append(v[offset - d: offset + d + 1])

    # ---------- Backtracking: walk from (n, m) back to (0, 0) ----------
    edits = []
    x = n
    y = m
    for d in range(final_d, 0, -1):
        prev = trace[d - 1]   # V after round d-1
        base = d - 1          # prev[base + k] is V[k]
        k = x - y

        # Same rule as the forward pass: which diagonal did we come from?
        if k == -d or (k != d and prev[base + k - 1] < prev[base + k + 1]):
            prev_k = k + 1    # came DOWN  (insert)
        else:
            prev_k = k - 1    # came RIGHT (delete)

        prev_x = prev[base + prev_k]
        prev_y = prev_x - prev_k

        # Point right after the paid move (where the snake started)
        if prev_k == k + 1:
            mid_x, mid_y = prev_x, prev_y + 1
        else:
            mid_x, mid_y = prev_x + 1, prev_y

        # Walk back along the snake: each diagonal step is a keep
        while x > mid_x and y > mid_y:
            x -= 1
            y -= 1
            edits.append((b" ", a[x]))

        # Record the one paid move
        if prev_k == k + 1:
            edits.append((b"+", b[prev_y]))
        else:
            edits.append((b"-", a[prev_x]))

        x = prev_x
        y = prev_y

    # Snake at d = 0 (lines equal at the very start): all keeps
    while x > 0 and y > 0:
        x -= 1
        y -= 1
        edits.append((b" ", a[x]))

    edits.reverse()   # we collected backwards; reverse once (never insert(0, ...))
    return edits



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
    edits = myers_diff(a, b)

    # Write bytes directly (keeps \r and non-UTF-8 bytes exactly)
    out = []
    for op, line in edits:
        out.append(op + line + b"\n")
    sys.stdout.buffer.write(b"".join(out))
    return 0



raise SystemExit(main())
