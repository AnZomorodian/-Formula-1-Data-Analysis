import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke

# Load the qualifying session for the 2025 Spanish Grand Prix
session = fastf1.get_session(2025, 'Spanish Grand Prix', 'Q')
session.load()

# Get all laps
laps = session.laps

# For each driver, find their best lap
drivers = laps['Driver'].unique()
best_laps = []
for drv in drivers:
    driver_laps = laps.pick_driver(drv)
    fastest_lap = driver_laps.pick_fastest()
    best_laps.append(fastest_lap)

# Convert to DataFrame
best_laps_df = pd.DataFrame(best_laps)

# Sort by overall lap time to get top 10 drivers
top_10 = best_laps_df.nsmallest(10, 'LapTime')

# Create a summary table
summary_table = top_10[['Driver', 'Sector1Time', 'Sector2Time', 'Sector3Time']].copy()

# Format times to seconds with 3 decimal places
def format_timedelta(td):
    if pd.isnull(td):
        return '-'
    total_seconds = td.total_seconds()
    return f"{total_seconds:.3f}"

summary_table['Sector1Time'] = summary_table['Sector1Time'].apply(format_timedelta)
summary_table['Sector2Time'] = summary_table['Sector2Time'].apply(format_timedelta)
summary_table['Sector3Time'] = summary_table['Sector3Time'].apply(format_timedelta)

# Rename columns
summary_table.columns = ['Driver', 'Sector 1', 'Sector 2', 'Sector 3']
summary_table.reset_index(drop=True, inplace=True)

# Convert times back to floats for highlighting best sectors
numeric_sectors = top_10[['Sector1Time', 'Sector2Time', 'Sector3Time']].apply(lambda x: x.dt.total_seconds())
best_sector_times = {
    'Sector 1': numeric_sectors['Sector1Time'].min(),
    'Sector 2': numeric_sectors['Sector2Time'].min(),
    'Sector 3': numeric_sectors['Sector3Time'].min()
}

# --- PLOTTING ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

# Title
plt.title('Top 10 Drivers - Best Sector Times (Qualifying)\n2025 Spanish Grand Prix', 
          fontsize=18, fontweight='bold', color='#2c3e50', pad=20)

# Create the table
table = ax.table(
    cellText=summary_table.values,
    colLabels=summary_table.columns,
    cellLoc='center',
    loc='center'
)

# Style adjustments
table.auto_set_font_size(False)
table.set_fontsize(13)
table.scale(1.2, 1.5)

# Define colors
header_color = '#2c3e50'
header_text_color = 'white'
row_colors = ['#f7f9fa', '#e9eef1']
highlight_color = '#a0e6a0'

# Apply styles to cells
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight='bold', color=header_text_color)
        cell.set_facecolor(header_color)
        cell.set_linewidth(1.2)
    else:
        cell.set_facecolor(row_colors[row % 2])
        cell.set_linewidth(0.8)
        cell.set_edgecolor('#d0d0d0')
        
        if col > 0:
            sector_name = summary_table.columns[col]
            time_value = summary_table.iloc[row-1, col]
            try:
                time_float = float(time_value)
                if abs(time_float - best_sector_times[sector_name]) < 0.001:
                    cell.set_facecolor(highlight_color)
                    cell.set_text_props(weight='bold')
            except:
                pass

    cell.set_height(0.075)
    cell.PAD = 0.5

# Add watermark in the middle
watermark_text = "BNP Developer Group"
plt.text(
    0.5, 0.5, watermark_text,
    fontsize=65, color='lightgrey',
    alpha=0.1, ha='center', va='center',
    transform=ax.transAxes,
    rotation=30,
    path_effects=[withStroke(linewidth=3, foreground='white')]
)

# Add "Fastest Lap Overall" - refined version
best_lap_time = top_10.iloc[0]['LapTime']
best_driver = top_10.iloc[0]['Driver']

def format_best_lap_time(td):
    if pd.isnull(td):
        return '-'
    minutes = int(td.total_seconds() // 60)
    seconds = td.total_seconds() % 60
    return f"{minutes}:{seconds:06.3f}"

best_lap_time_str = format_best_lap_time(best_lap_time)

# Add a colored box or badge
bbox_props = dict(boxstyle="round,pad=0.4", 
                  facecolor="#f1c40f", alpha=0.85, edgecolor='#e67e22')

plt.figtext(
    0.5, 0.05, 
    f"Fastest Lap Overall: {best_driver} - {best_lap_time_str}", 
    ha='center', va='center', fontsize=16, fontweight='bold', color='#2c3e50',
    bbox=bbox_props
)

# Adjust layout
plt.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)
plt.savefig('top10_best_sectors_with_watermark.png', dpi=300, bbox_inches='tight')
plt.show()
