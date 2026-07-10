import csv
from datetime import datetime


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


def inspect(input_path):
    dates = []
    unparsable = 0
    with open(input_path, encoding='utf-8') as f:
        r = csv.reader(f)
        header = next(r)
        try:
            idx = [x.strip().lower() for x in header].index('last login date')
        except ValueError:
            print('No Last Login Date column')
            return
        for row in r:
            val = row[idx] if idx < len(row) else ''
            dt = parse_date(val)
            if dt is None:
                unparsable += 1
            else:
                dates.append(dt)
    if dates:
        print('Min date:', min(dates))
        print('Max date:', max(dates))
    print('Unparsable count:', unparsable)


if __name__ == '__main__':
    inspect('Users_Details.csv')
