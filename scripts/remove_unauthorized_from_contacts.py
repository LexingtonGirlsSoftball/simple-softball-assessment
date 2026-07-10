import csv
import os


def load_unauthorized_emails(users_csv='Users_Details.csv'):
    emails = set()
    with open(users_csv, encoding='utf-8') as f:
        r = csv.reader(f)
        header = next(r)
        try:
            auth_idx = [h.strip().lower() for h in header].index('authorization status')
        except ValueError:
            return emails
        # assume email is column 'Email Address'
        try:
            email_idx = [h.strip().lower() for h in header].index('email address')
        except ValueError:
            email_idx = 2
        for row in r:
            val = row[auth_idx] if auth_idx < len(row) else ''
            if val and val.strip().lower() == 'unauthorized':
                email = row[email_idx] if email_idx < len(row) else ''
                if email:
                    emails.add(email.strip())
    return emails


def filter_contacts(contacts_csv='Users_Details_gmail_contacts.csv', output_csv='Users_Details_gmail_contacts_no_unauthorized.csv', users_csv='Users_Details.csv'):
    unauthorized = load_unauthorized_emails(users_csv)
    print(f'Unauthorized emails to remove: {len(unauthorized)}')
    if unauthorized:
        for e in list(unauthorized)[:20]:
            print(' -', e)

    kept = 0
    removed = 0

    with open(contacts_csv, encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)
        fieldnames = reader.fieldnames

    out_rows = []
    for r in rows:
        email = (r.get('E-mail 1 - Value') or '').strip()
        if email and email in unauthorized:
            removed += 1
            continue
        out_rows.append(r)
        kept += 1

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f'Kept: {kept}, Removed: {removed}. Wrote: {output_csv}')


if __name__ == '__main__':
    filter_contacts()
