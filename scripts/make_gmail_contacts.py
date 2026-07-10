import csv
import os
import argparse


def build_gmail_contacts(input_csv, output_csv, group_name='LGS_Cleaned'):
    with open(input_csv, encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    out_fields = ['Name', 'Given Name', 'Family Name', 'E-mail 1 - Value', 'E-mail 1 - Type', 'Group Membership']
    out_rows = []

    for r in rows:
        email = (r.get('Email Address') or r.get('Additional Email Address') or '').strip()
        if not email:
            continue
        first = (r.get('User First Name') or '').strip()
        last = (r.get('User Last Name') or '').strip()
        if not first and not last:
            name = email.split('@', 1)[0]
        else:
            name = (first + ' ' + last).strip()

        out_rows.append({
            'Name': name,
            'Given Name': first,
            'Family Name': last,
            'E-mail 1 - Value': email,
            'E-mail 1 - Type': 'Home',
            'Group Membership': f'Group: {group_name}'
        })

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f'Wrote {len(out_rows)} contacts to {output_csv}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Gmail contacts CSV from cleaned users CSV')
    parser.add_argument('--input', '-i', default='Users_Details_cleaned.csv', help='Input cleaned CSV')
    parser.add_argument('--output', '-o', default='Users_Details_gmail_contacts.csv', help='Output contacts CSV')
    parser.add_argument('--group', '-g', default='LGS_Cleaned', help='Group/label name to set for contacts')
    args = parser.parse_args()

    in_csv = os.path.abspath(args.input)
    out_csv = os.path.abspath(args.output)
    build_gmail_contacts(in_csv, out_csv, group_name=args.group)
