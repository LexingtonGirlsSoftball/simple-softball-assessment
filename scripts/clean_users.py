import csv
from datetime import datetime, timedelta
import os


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    formats = [
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def clean_csv(input_path, output_path, years=3):
    total = 0
    removed = 0
    kept = 0

    cutoff = datetime.now() - timedelta(days=365 * years)
    print(f"Cutoff datetime (older than this will be removed): {cutoff}")

    with open(input_path, newline='', encoding='utf-8') as f_in:
        reader = csv.reader(f_in)
        rows = list(reader)

    if not rows:
        print("Input CSV is empty")
        return

    header = rows[0]
    # find Last Login Date column index (case-insensitive)
    col = None
    for i, h in enumerate(header):
        if h and h.strip().lower() == 'last login date':
            col = i
            break
    if col is None:
        print("Could not find 'Last Login Date' column in header.")
        return

    out_rows = [header]

    for r in rows[1:]:
        total += 1
        last_login = r[col] if col < len(r) else ''
        dt = parse_date(last_login)
        # treat missing/unparsable as old (remove)
        if dt is None or dt < cutoff:
            removed += 1
            continue
        out_rows.append(r)
        kept += 1

    # ensure output dir exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerows(out_rows)

    print(f"Total rows checked: {total}")
    print(f"Rows kept: {kept}")
    print(f"Rows removed: {removed}")
    print(f"Cleaned file written to: {output_path}")


if __name__ == '__main__':
    in_path = os.path.abspath(r"Users_Details.csv")
    out_path = os.path.abspath(r"Users_Details_cleaned.csv")
    clean_csv(in_path, out_path, years=3)
