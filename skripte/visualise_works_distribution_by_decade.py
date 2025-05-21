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
x_label = "Dekaden"
y_label = "Anzahl der Werke"

# === Hilfsfunktion zum Laden von Excel oder CSV ===
def read_and_process(filepath):
    try:
        if filepath.lower().endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.lower().endswith('.csv'):
            df = pd.read_csv(filepath, encoding='utf-8')
        else:
            raise ValueError(f"Nicht unterstütztes Dateiformat: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Einlesen der Datei {filepath}: {e}")
    
    if 'year' not in df.columns:
        raise ValueError(f"Die Spalte 'year' fehlt in der Datei {filepath}.")
    
    # Entferne ungültige oder fehlende Jahrgänge
    df = df.dropna(subset=['year'])
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    
    # Dekade berechnen
    df['decade'] = (df['year'] // 10) * 10
    return df

# === Daten einlesen und verarbeiten ===
df_main = read_and_process(input_path_main)
df_ger  = read_and_process(input_path_ger)

# === Werke pro Dekade zählen ===
decade_counts_main = df_main['decade'].value_counts().sort_index()
decade_counts_ger  = df_ger ['decade'].value_counts().sort_index()

# === Alle vorkommenden Dekaden erfassen ===
all_decades = sorted(set(decade_counts_main.index).union(set(decade_counts_ger.index)))

main_counts = [decade_counts_main.get(dec, 0) for dec in all_decades]
ger_counts  = [decade_counts_ger.get(dec, 0)  for dec in all_decades]

if not any(main_counts) and not any(ger_counts):
    raise ValueError("Keine gültigen Jahresdaten gefunden – Analyse nicht möglich.")

# === Diagramm erstellen ===
plt.figure(figsize=(10, 6))
bar_width = 6

plt.bar(all_decades, main_counts, color=color_main, label="Nicht Teil von GerDraCor", width=bar_width)
plt.bar(all_decades, ger_counts, bottom=main_counts, color=color_ger, label="Teil von GerDraCor", width=bar_width)

plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(chart_title)
plt.xticks(all_decades, rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', color='grey', alpha=0.7)

max_total = max([m + g for m, g in zip(main_counts, ger_counts)])
y_max = int(np.ceil(max_total / 5)) * 5
plt.yticks(np.arange(0, y_max + 5, 5))
plt.legend()
plt.tight_layout()

# === Diagramm speichern ===
os.makedirs(output_path, exist_ok=True)
output_file = os.path.join(output_path, "works_distribution_by_decade.png")
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Diagramm erfolgreich gespeichert unter:\n{output_file}")
