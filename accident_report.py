import pandas as pd
import matplotlib.pyplot as plt

# Load the data and the file path
df = pd.read_csv("FINAL PROJECT\Metro_Manila_Traffic_Incidents_2025.csv")

null_counts = df.isnull().sum().reset_index()
null_counts.columns = ['Column Name', "Null Count"]

# row to display the number of duplicates
duplicate_count = df.duplicated().sum()
duplicate_display = pd.DataFrame({'Column Name': ['DUPLICATE ROWS (TOTAL)'], 'Null Count': [duplicate_count]})
null_counts = pd.concat([null_counts, duplicate_display], ignore_index=True)

# create the table visualization
fig, ax = plt.subplots(figsize=(8,8))
ax.axis('tight')
ax.axis('off')

# create the table
table_display = ax.table (
    cellText=null_counts.values,
    colLabels=null_counts.columns,
    cellLoc = 'center',
    loc='center'
)

# formatting
table_display.auto_set_font_size(False)
table_display.set_fontsize(11)
table_display.scale(1.2, 1.5)

plt.title('Data Quality Report (Nulls & Duplicates)', fontsize=14, pad=20, fontweight='bold')
plt.show()
