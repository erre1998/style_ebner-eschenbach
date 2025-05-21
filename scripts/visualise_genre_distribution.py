import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === Define paths (individuell anzupassen) ===
input_path_main = r"E:\python\input\FemAut_works_19th_not_in_DraCor.csv"
input_path_ger  = r"E:\python\input\FemAut_works_19th_in_DraCor.csv"
output_path     = r"E:\python\output"

# === Chart settings ===
color_main = "#3498db"    # Blau = Nicht Teil von GerDraCor
color_ger = "#e67e22"     # Orange = Teil von GerDraCor
x_label = "Genre"
y_label = "Anzahl der Werke"

# === Load datasets ===
try:
    df_main = pd.read_csv(input_path_main, encoding='utf-8')
    df_ger  = pd.read_csv(input_path_ger,  encoding='utf-8')
except Exception as e:
    raise RuntimeError(f"Fehler beim Einlesen der CSV-Dateien: {e}")

# === Validate columns ===
for df, name in [(df_main, "Haupt-Datei"), (df_ger, "GerDraCor-Datei")]:
    if 'genre' not in df.columns:
        raise ValueError(f"Die Spalte 'genre' wurde in der {name} nicht gefunden.")

# === Clean and normalize genres ===
# Leere Strings ("") und NaN auf 'na' setzen, alles klein schreiben
for df in (df_main, df_ger):
    df['genre'] = (
        df['genre']
        .fillna('')               # NaN → ''
        .replace('', 'na')        # '' → 'na'
        .str.lower()              # Kleinbuchstaben
    )

# Optional: Nur diese Genres berücksichtigen
valid_genres = ['comedy', 'tragedy', 'na']
df_main = df_main[df_main['genre'].isin(valid_genres)]
df_ger  = df_ger[df_ger['genre'].isin(valid_genres)]

# === Count genres ===
main_counts = df_main['genre'].value_counts().reindex(valid_genres, fill_value=0)
ger_counts  = df_ger ['genre'].value_counts().reindex(valid_genres, fill_value=0)

# === Create grouped bar chart ===
genres = valid_genres
x = np.arange(len(genres))
bar_width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - bar_width/2, main_counts, width=bar_width, color=color_main, label="Nicht Teil von GerDraCor")
plt.bar(x + bar_width/2, ger_counts,  width=bar_width, color=color_ger,  label="Teil von GerDraCor")

# Achsenbeschriftungen
plt.xlabel(x_label)
plt.ylabel(y_label)

# X-Tick-Labels übersetzen
xtick_labels = {
    'comedy': "Typen der Komödie",
    'tragedy': "Typen der Tragödie",
    'na': "Ohne Genrezuordnung"
}
plt.xticks(x, [xtick_labels[g] for g in genres])

plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()

# === Save output ===
os.makedirs(output_path, exist_ok=True)
output_file = os.path.join(output_path, "genre_distribution_grouped_bar_chart.png")
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Diagramm gespeichert unter:\n{output_file}")
