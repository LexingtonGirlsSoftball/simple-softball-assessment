import csv
import os
import argparse


def make_players(contacts_csv='Users_Details_gmail_contacts_no_unauthorized.csv', output_csv='Players_Import_from_contacts.csv', default_birthdate='01/01/2000', default_gender='', default_player_first_name='EmailOnly'):
    # Template header
    header = [
        'Player First Name*', 'Player Last Name*', 'Player Birthdate', 'Player Gender', 'Division', 'Team Name',
        'Primary Contact 1 First Name*', 'Primary Contact 1 Last Name*', 'Primary Contact 1 Email*', 'Primary Contact 1 Phone',
        'Primary Contact 2 First Name', 'Primary Contact 2 Last Name', 'Primary Contact 2 Email', 'Primary Contact 2 Phone'
    ]

    # prefer no-unauthorized contacts file; fall back to full export
    if not os.path.exists(contacts_csv):
        contacts_csv = 'Users_Details_gmail_contacts.csv'

    rows_out = []
    with open(contacts_csv, encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for r in reader:
            given = (r.get('Given Name') or '').strip()
            family = (r.get('Family Name') or '').strip()
            name = (r.get('Name') or '').strip()
            email = (r.get('E-mail 1 - Value') or '').strip()

            if not (given or family) and name:
                parts = name.split(None, 1)
                given = parts[0]
                family = parts[1] if len(parts) > 1 else ''

            # Ensure family name exists: fallback to given (or default)
            if not family:
                family = given or default_player_first_name

            # Force player first name to the configured default for all players
            player_first = default_player_first_name
            # Primary contact first name remains the given name (or default if missing)
            contact_first = given or default_player_first_name

            if not email:
                continue

            row = {
                'Player First Name*': player_first,
                'Player Last Name*': family or '',
                'Player Birthdate': default_birthdate,
                'Player Gender': default_gender,
                'Division': '',
                'Team Name': '',
                'Primary Contact 1 First Name*': contact_first,
                'Primary Contact 1 Last Name*': family or '',
                'Primary Contact 1 Email*': email,
                'Primary Contact 1 Phone': '',
                'Primary Contact 2 First Name': '',
                'Primary Contact 2 Last Name': '',
                'Primary Contact 2 Email': '',
                'Primary Contact 2 Phone': ''
            }
            rows_out.append(row)

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f'Wrote {len(rows_out)} player rows to {output_csv}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Map contacts to Players import template')
    parser.add_argument('--input', '-i', default='Users_Details_gmail_contacts_no_unauthorized.csv')
    parser.add_argument('--output', '-o', default='Players_Import_from_contacts.csv')
    parser.add_argument('--birthdate', '-b', default='01/01/2000', help='Default birthdate to use (required by template)')
    parser.add_argument('--gender', '-g', default='', help='Default gender (M/F) or empty')
    parser.add_argument('--player-first-name', '-p', default='EmailOnly', help='Default player first name to apply to all players')
    args = parser.parse_args()
    make_players(contacts_csv=args.input, output_csv=args.output, default_birthdate=args.birthdate, default_gender=args.gender, default_player_first_name=args.player_first_name)
