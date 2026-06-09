# =============================================================================
# FICHIER : visualization/graphiques.py
# RÔLE    : Couche visualisation — génère tous les graphiques avec matplotlib.
#           Chaque fonction retourne une Figure qu'on peut intégrer dans PyQt.
# =============================================================================

import matplotlib
matplotlib.use('Agg')             # moteur sans fenêtre (pour intégration PyQt)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# Palette de couleurs cohérente pour toute l'application
COULEURS_CENTRES  = ["#4A90D9", "#E8705A", "#5BAD72"]   # C1=bleu, C2=rouge, C3=vert
COULEURS_REGIONS  = ["#9B59B6", "#F39C12", "#1ABC9C", "#E74C3C"]  # R1 R2 R3 R4
FOND              = "#1E1E2E"    # fond sombre
TEXTE             = "#E0E0E0"    # texte clair


def _style_figure(fig, ax_list):
    """
    Applique un style sombre cohérent à une figure et ses axes.
    ax_list peut être un seul ax ou une liste d'axes.
    """
    fig.patch.set_facecolor(FOND)
    if not isinstance(ax_list, (list, np.ndarray)):
        ax_list = [ax_list]
    for ax in ax_list:
        ax.set_facecolor("#2A2A3E")
        ax.tick_params(colors=TEXTE)
        ax.xaxis.label.set_color(TEXTE)
        ax.yaxis.label.set_color(TEXTE)
        ax.title.set_color(TEXTE)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444466")


# =============================================================================
# GRAPHIQUE 1 : Répartition des flux (qui envoie quoi où)
# Type : Grouped bar chart (barres groupées)
# =============================================================================

def graphique_flux(solution, regions, centres):
    """
    Crée un graphique en barres groupées montrant combien de requêtes
    chaque région envoie vers chaque centre.

    solution : dict {(i,j): valeur}
    """
    nb_r = len(regions)
    nb_c = len(centres)

    # Construire la matrice des valeurs : mat[i][j] = x[i,j]
    mat = np.array([
        [solution.get((i, j), 0) for j in range(nb_c)]
        for i in range(nb_r)
    ])

    fig, ax = plt.subplots(figsize=(9, 5))
    _style_figure(fig, ax)

    # Position des groupes sur l'axe x
    x_pos     = np.arange(nb_r)   # [0, 1, 2, 3]
    largeur   = 0.25               # largeur d'une barre
    decalage  = [-0.25, 0, 0.25]  # décalage pour C1, C2, C3

    for j in range(nb_c):
        ax.bar(
            x_pos + decalage[j],   # position x de chaque barre
            mat[:, j],             # hauteurs : requêtes de chaque région vers Cj
            width    = largeur,
            label    = centres[j],
            color    = COULEURS_CENTRES[j],
            alpha    = 0.85,
            edgecolor= "#ffffff22"
        )

    # Annotations : afficher la valeur au-dessus de chaque barre
    for j in range(nb_c):
        for i in range(nb_r):
            val = mat[i, j]
            if val > 0:
                ax.text(
                    x_pos[i] + decalage[j],  # position x
                    val + 5,                  # légèrement au-dessus
                    f"{val:.0f}",
                    ha='center', va='bottom',
                    fontsize=7, color=TEXTE
                )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(regions)
    ax.set_xlabel("Régions")
    ax.set_ylabel("Nombre de requêtes")
    ax.set_title("Répartition des flux : Régions → Centres", fontsize=12, pad=12)
    ax.legend(facecolor="#2A2A3E", labelcolor=TEXTE)
    fig.tight_layout()
    return fig


# =============================================================================
# GRAPHIQUE 2 : Utilisation des capacités des centres
# Type : Barres horizontales avec indicateur de saturation
# =============================================================================

def graphique_capacites(utilisation, centres, capacites):
    """
    Affiche pour chaque centre : capacité totale vs requêtes reçues.
    Met en évidence les centres proches de la saturation (>= 90%).
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    _style_figure(fig, ax)

    y_pos = np.arange(len(centres))

    for j, centre in enumerate(centres):
        util  = utilisation[j]
        pct   = util["pourcentage"]
        recu  = util["recu"]
        capa  = util["capacite"]

        # Couleur de la barre : rouge si >= 90%, orange si >= 70%, sinon vert
        if pct >= 90:
            couleur = "#E74C3C"   # rouge → saturé
        elif pct >= 70:
            couleur = "#F39C12"   # orange → attention
        else:
            couleur = "#2ECC71"   # vert → OK

        # Barre de fond (capacité totale)
        ax.barh(y_pos[j], capa, height=0.5, color="#333355", label="_nolegend_")

        # Barre de remplissage (requêtes reçues)
        ax.barh(y_pos[j], recu, height=0.5, color=couleur, alpha=0.85)

        # Texte : "1200 / 1500 (80.0%)"
        ax.text(
            capa * 1.02, y_pos[j],
            f"{recu:.0f}/{capa} ({pct:.1f}%)",
            va='center', fontsize=9, color=TEXTE
        )

    # Ligne verticale à 90% → seuil d'alerte
    for j in range(len(centres)):
        ax.axvline(
            x    = capacites[j] * 0.90,
            ymin = (j / len(centres)) + 0.05,
            ymax = ((j + 1) / len(centres)) - 0.05,
            color= "#ff6666", linestyle="--", linewidth=1, alpha=0.5
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(centres)
    ax.set_xlabel("Requêtes")
    ax.set_title("Utilisation des capacités des centres", fontsize=12, pad=12)

    # Légende manuelle
    patches = [
        mpatches.Patch(color="#2ECC71", label="OK (< 70%)"),
        mpatches.Patch(color="#F39C12", label="Attention (70-90%)"),
        mpatches.Patch(color="#E74C3C", label="Saturé (≥ 90%)"),
    ]
    ax.legend(handles=patches, facecolor="#2A2A3E", labelcolor=TEXTE, fontsize=8)
    fig.tight_layout()
    return fig


# =============================================================================
# GRAPHIQUE 3 : Tableau récapitulatif des coûts (heatmap)
# =============================================================================

def graphique_heatmap_couts(solution, couts, regions, centres):
    """
    Affiche une heatmap de la matrice des coûts effectifs (coût * flux).
    Plus la case est foncée, plus le coût est élevé.
    """
    nb_r = len(regions)
    nb_c = len(centres)

    # Matrice des coûts effectifs : coût[i][j] * x[i,j]
    mat_couts = np.array([
        [couts[i][j] * solution.get((i, j), 0) for j in range(nb_c)]
        for i in range(nb_r)
    ])

    fig, ax = plt.subplots(figsize=(6, 5))
    _style_figure(fig, ax)

    # Affichage de la heatmap avec colormap bleue
    im = ax.imshow(mat_couts, cmap="YlOrRd", aspect="auto")

    # Labels des axes
    ax.set_xticks(range(nb_c))
    ax.set_xticklabels(centres)
    ax.set_yticks(range(nb_r))
    ax.set_yticklabels(regions)

    # Afficher la valeur dans chaque cellule
    for i in range(nb_r):
        for j in range(nb_c):
            val = mat_couts[i, j]
            # Texte noir si fond clair, blanc si fond foncé
            couleur_texte = "black" if val < mat_couts.max() * 0.6 else "white"
            ax.text(
                j, i, f"{val:.0f}",
                ha="center", va="center",
                fontsize=9, color=couleur_texte, fontweight="bold"
            )

    plt.colorbar(im, ax=ax, label="Coût effectif (€)")
    ax.set_title("Heatmap des coûts effectifs par flux", fontsize=11, pad=10)
    fig.tight_layout()
    return fig


# =============================================================================
# GRAPHIQUE 4 : Comparaison de scénarios (barres côte à côte)
# =============================================================================

def graphique_comparaison_scenarios(scenarios):
    """
    Compare les coûts totaux de plusieurs scénarios.

    scenarios : liste de dict {"nom": str, "cout": float, "couleur": str}
    """
    noms    = [s["nom"]    for s in scenarios]
    couts   = [s["cout"]   for s in scenarios]
    couleurs= [s.get("couleur", "#4A90D9") for s in scenarios]

    fig, ax = plt.subplots(figsize=(8, 5))
    _style_figure(fig, ax)

    barres = ax.bar(noms, couts, color=couleurs, width=0.5, edgecolor="#ffffff22")

    # Valeur au-dessus de chaque barre
    for barre, cout in zip(barres, couts):
        ax.text(
            barre.get_x() + barre.get_width() / 2,
            barre.get_height() + max(couts) * 0.01,
            f"{cout:,.0f} €",
            ha="center", va="bottom", fontsize=9, color=TEXTE
        )

    # Ligne de référence (scénario de base = premier scénario)
    ax.axhline(y=couts[0], color="#aaaaff", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(
        len(noms) - 0.5, couts[0] * 1.005,
        "Base", color="#aaaaff", fontsize=8
    )

    ax.set_ylabel("Coût total optimal (€)")
    ax.set_title("Comparaison des coûts selon les scénarios", fontsize=12, pad=12)
    ax.set_ylim(0, max(couts) * 1.15)
    fig.tight_layout()
    return fig
