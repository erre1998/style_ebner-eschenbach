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
color_ger  = "#e67e22"    # Orange = Teil von GerDraCor
x_label = "Dramatikerinnen"
y_label = "Anzahl der Werke"

# === Helper function to load Excel or CSV ===
def load_file(path):
    try:
        if path.lower().endswith('.xlsx'):
            return pd.read_excel(path)
        elif path.lower().endswith('.csv'):
            return pd.read_csv(path, encoding='utf-8')
        else:
            raise ValueError(f"Nicht unterstütztes Dateiformat: {path}")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Einlesen der Datei {path}: {e}")

# === Load datasets ===
df_main = load_file(input_path_main)
df_ger  = load_file(input_path_ger)

# === Check required column ===
for df, name in [(df_main, "Hauptdatei"), (df_ger, "GerDraCor-Datei")]:
    if 'author-name' not in df.columns:
        raise ValueError(f"Die Spalte 'author-name' fehlt in der {name}.")

# === Clean and drop missing values ===
df_main = df_main[['author-name']].dropna()
df_ger  = df_ger [['author-name']].dropna()

# === Count works per author ===
main_counts = df_main['author-name'].value_counts()
ger_counts  = df_ger ['author-name'].value_counts()

# === Combine and select top 10 ===
combined_counts = main_counts.add(ger_counts, fill_value=0)
top_10_authors = combined_counts.sort_values(ascending=False).head(10).index.tolist()

# === Align data for plotting ===
main_top = main_counts.reindex(top_10_authors, fill_value=0)
ger_top  = ger_counts.reindex(top_10_authors, fill_value=0)
total_top = main_top + ger_top

# === Plot ===
plt.figure(figsize=(12, 6))
x = np.arange(len(top_10_authors))
bar_width = 0.6

plt.bar(x, main_top, color=color_main, label="Nicht Teil von GerDraCor", width=bar_width)
plt.bar(x, ger_top, bottom=main_top, color=color_ger, label="Teil von GerDraCor", width=bar_width)

plt.xlabel(x_label)
plt.ylabel(y_label)
plt.xticks(x, top_10_authors, rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

y_max = int(np.ceil(total_top.max() / 5)) * 5
plt.yticks(np.arange(0, y_max + 5, 5))
plt.legend()
plt.tight_layout()

# === Save output ===
os.makedirs(output_path, exist_ok=True)
output_file = os.path.join(output_path, "top_10_female_authors_stacked_labeled.png")
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Diagramm erfolgreich gespeichert unter:\n{output_file}")
