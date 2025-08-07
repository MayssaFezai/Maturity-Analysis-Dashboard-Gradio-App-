import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt

mois_disponibles = ['Janv.', 'Fev.', 'Mars', 'Avr.', 'Mai', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Dec.']

def generer_graphique(file, mois):
    sheet1 = pd.read_excel(file.name, sheet_name='CDT Assemblage', skiprows=4)
    sheet2 = pd.read_excel(file.name, sheet_name='CDT PE', skiprows=4)

    def extraire(df, mois):
        standards = df.iloc[:, 2]
        valeurs = df[mois]
        df_filtré = pd.DataFrame({'Standard': standards, 'Valeur': valeurs}).dropna()
        exclure = ['Objectifs', 'Résultats', 'mat>', 'mat> B']
        return df_filtré[~df_filtré['Standard'].astype(str).str.contains('|'.join(exclure), case=False)]

    df1 = extraire(sheet1, mois)
    df2 = extraire(sheet2, mois)
    merged = pd.merge(df1, df2, on='Standard', suffixes=('_1', '_2'))
    merged['Moyenne'] = merged[['Valeur_1', 'Valeur_2']].mean(axis=1)

    ordre = sheet1.iloc[:, 2].dropna().tolist()
    ordre_filtré = [s for s in ordre if s in merged['Standard'].values]
    merged = merged.set_index('Standard').loc[ordre_filtré].reset_index()

    # Définir les couleurs selon les valeurs
    couleurs = []
    for val in merged['Moyenne']:
        if val < 3:
            couleurs.append('red')
        elif val < 6.5:
            couleurs.append('yellow')
        elif val < 9.2:
            couleurs.append('green')
        else:
            couleurs.append('skyblue')

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(merged['Standard'], merged['Moyenne'], color=couleurs)
    ax.set_title(f"Moyenne des scores – {mois}")
    ax.set_xlabel("Standards")
    ax.set_ylabel("Moyenne")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return fig

interface = gr.Interface(
    fn=generer_graphique,
    inputs=[
        gr.File(label="Fichier Excel (.xlsx)", file_types=[".xlsx"]),
        gr.Dropdown(choices=mois_disponibles, label="Mois")
    ],
    outputs=gr.Plot(label="Graphique"),
    title="Analyse de Maturité par Standard",
    description="Chargez un fichier Excel, sélectionnez un mois, et visualisez la moyenne des scores."
)

interface.launch()
