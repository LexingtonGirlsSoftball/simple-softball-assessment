import csv
import os


def extract_unauthorized(input_csv='Users_Details.csv', output_csv='Users_Details_unauthorized.csv'):
    with open(input_csv, encoding='utf-8') as f_in:
        reader = csv.reader(f_in)
        rows = list(reader)

    if not rows:
        print('Input CSV empty')
        return

    header = rows[0]
    try:
        idx = [h.strip().lower() for h in header].index('authorization status')
    except ValueError:
        print("'Authorization Status' column not found")
        return

    out = [header]
    results = []
    for r in rows[1:]:
        val = r[idx] if idx < len(r) else ''
        if val and val.strip().lower() == 'unauthorized':
            out.append(r)
            # collect name and email for quick display
            first = r[0] if len(r) > 0 else ''
            last = r[1] if len(r) > 1 else ''
            email = r[2] if len(r) > 2 else ''
            results.append((first.strip(), last.strip(), email.strip()))

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerows(out)

    print(f'Unauthorized accounts found: {len(results)}')
    for i, (first, last, email) in enumerate(results[:50], start=1):
        print(f'{i}. {first} {last} <{email}>')
    if len(results) > 50:
        print(f'...and {len(results)-50} more. See {output_csv} for full list.')


if __name__ == '__main__':
    extract_unauthorized()
