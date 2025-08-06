
import io
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

import subprocess


print("Ensure you are running from the git repository you are trying to analyze.")
print("Getting commits and parsing")
# Run the git command and capture the output (name|email|date)
result = subprocess.run(
    ['git', 'log', '--pretty=%an|%ae|%ad', '--date=format:%Y-%m', '--since=6 months ago'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Load the output into a buffer
buffer = io.StringIO(result.stdout)

# Example: Read the buffer content
commit_logs = buffer.getvalue()

print("Loading data")

# Load commit data
# Map user identity to a canonical form (name, email)
commit_data = defaultdict(lambda: defaultdict(int))
user_map = dict()  # key: canonical_id, value: (name, email)

for line in commit_logs.splitlines():
    # Expect format: name|email|date
    try:
        author_name, author_email, date = line.split("|")
    except ValueError:
        continue  # skip malformed lines
    # Normalize name by removing company info in parentheses
    import re
    name = author_name.strip()
    base_name = re.sub(r"\s*\(.*\)$", "", name)
    email = author_email.strip().lower()
    date = date.strip()
    # Use email as canonical id if available, else base_name
    canonical_id = email if email else base_name
    user_map[canonical_id] = (base_name, email)
    commit_data[date][canonical_id] += 1

# Convert to DataFrame
data = []
for month, authors in commit_data.items():
    for author, count in authors.items():
        data.append([month, author, count])

df = pd.DataFrame(data, columns=["Month", "Author", "Commits"])
df = df.sort_values(by=["Month", "Commits"], ascending=[True, False])

print("Pivot and generating data")

# Only one row per user (by canonical id)
data = []
for month, users in commit_data.items():
    for canonical_id, count in users.items():
        name, email = user_map[canonical_id]
        data.append([month, name, email, count])

df = pd.DataFrame(data, columns=["Month", "Name", "Email", "Commits"])
df = df.sort_values(by=["Month", "Commits"], ascending=[True, False])

# Pivot to trend over time

# Aggregate commit counts for users with the same base name
agg_df = df.groupby(["Name", "Month"]).agg({"Commits": "sum", "Email": "first"}).reset_index()
pivot_df = agg_df.pivot(index="Name", columns="Month", values="Commits").fillna(0)

# Save to CSV
print("Saving to csv")
filename = "commit_trends_by_user.csv"
pivot_df.to_csv(filename)

print (f"Commit trends saved to {filename}")
