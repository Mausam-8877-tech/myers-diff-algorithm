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


def add_position(ranges, pos):
    # Add one highlighted position; merge with the last range if they touch
    if ranges and ranges[-1][1] == pos:
        ranges[-1][1] = pos + 1
    else:
        ranges.append([pos, pos + 1])


def format_ranges(ranges):
    # [[3, 6], [9, 10]] -> "3-6,9-10";  [] -> "."
    if not ranges:
        return "."
    return ",".join(f"{start}-{end}" for start, end in ranges)


def char_ranges(old_line, new_line):
    # Part B: Myers again, on the characters (code points) of one line pair
    old = old_line.decode("utf-8")
    new = new_line.decode("utf-8")
    edits = myers_diff(list(old), list(new))

    old_ranges = []
    new_ranges = []
    i = 0   # position in old line
    j = 0   # position in new line
    for op, _ in edits:
        if op == b" ":          # same character in both
            i += 1
            j += 1
        elif op == b"-":        # only in old line -> highlight in old
            add_position(old_ranges, i)
            i += 1
        else:                   # only in new line -> highlight in new
            add_position(new_ranges, j)
            j += 1
    return format_ranges(old_ranges), format_ranges(new_ranges)


def build_output(edits, highlight):
    out = []
    i = 0
    while i < len(edits):
        op, line = edits[i]
        if op == b" ":
            out.append(b" " + line + b"\n")
            i += 1
            continue

        # Collect one change block: consecutive '-' and '+' lines
        dels = []
        ins = []
        while i < len(edits) and edits[i][0] != b" ":
            if edits[i][0] == b"-":
                dels.append(edits[i][1])
            else:
                ins.append(edits[i][1])
            i += 1

        # Delete-first rule: all '-' lines, then all '+' lines
        for d_line in dels:
            out.append(b"-" + d_line + b"\n")
        for idx, i_line in enumerate(ins):
            out.append(b"+" + i_line + b"\n")
            # Pair the idx-th '+' with the idx-th '-' (if it exists)
            if highlight and idx < len(dels):
                old_r, new_r = char_ranges(dels[idx], i_line)
                out.append(f"? {old_r} | {new_r}\n".encode())

    return b"".join(out)




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
    sys.stdout.buffer.write(build_output(edits, command == "highlight"))
    return 0



raise SystemExit(main())
