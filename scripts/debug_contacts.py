import csv
import json

path = 'c:/Users/jacdr/OneDrive/Documents/LGS/Users_Details_gmail_contacts_no_unauthorized.csv'
with open(path, encoding='utf-8') as f:
    r = csv.DictReader(f)
    rows = []
    for i, row in enumerate(r):
        if i < 5:
            rows.append(row)
        else:
            break
    print(json.dumps(rows, indent=2))
