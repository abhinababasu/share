
import io
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

import subprocess


print("Ensure you are running from the git repository you are trying to analyze.")
print("Getting commits and parsing")
# Run the git command and capture the output
result = subprocess.run(
    ['git', 'log', '--pretty=%an %ad', '--date=format:%Y-%m', '--since=6 months ago'],
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
commit_data = defaultdict(lambda: defaultdict(int))

for line in commit_logs.splitlines():
    author, date = line.rsplit(" ", 1)
    commit_data[date.strip()][author.strip()] += 1

# Convert to DataFrame
data = []
for month, authors in commit_data.items():
    for author, count in authors.items():
        data.append([month, author, count])

df = pd.DataFrame(data, columns=["Month", "Author", "Commits"])
df = df.sort_values(by=["Month", "Commits"], ascending=[True, False])

print("Pivot and generating data")

# Pivot to trend over time
pivot_df = df.pivot(index="Month", columns="Author", values="Commits").fillna(0)

# Plot trend
# Pivot to have authors as rows and months as columns
pivot_df = df.pivot(index="Author", columns="Month", values="Commits").fillna(0)

# Save to CSV
print("Saving to csv")
filename = "commit_trends_by_author.csv"
pivot_df.to_csv(filename)   

print (f"Commit trends saved to {filename}")
