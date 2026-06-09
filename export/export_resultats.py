# =============================================================================
# FICHIER : export/export_resultats.py
# RÔLE    : Couche export — sauvegarde les résultats en CSV ou PDF.
# =============================================================================

import csv
import os
from datetime import datetime


# =============================================================================
# EXPORT CSV
# =============================================================================

def exporter_csv(resultat, regions, centres, chemin_fichier=None):
    """
    Exporte la solution optimale dans un fichier CSV.

    Colonnes : Région, Centre, Requêtes affectées, Coût unitaire, Coût total
    Retourne le chemin du fichier créé.
    """
    if chemin_fichier is None:
        # Nom automatique avec horodatage si non fourni
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        chemin_fichier = f"export_solution_{ts}.csv"

    if not resultat["optimal"]:
        return None   # pas d'export si pas de solution

    sol = resultat["solution"]
    nb_r = resultat["nb_regions"]
    nb_c = resultat["nb_centres"]

    with open(chemin_fichier, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # En-tête du fichier
        writer.writerow(["=== RÉSULTATS DE L'OPTIMISATION ==="])
        writer.writerow([f"Coût total optimal : {resultat['cout_total']} €"])
        writer.writerow([f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
        writer.writerow([])  # ligne vide

        # En-tête du tableau
        writer.writerow(["Région", "Centre", "Requêtes affectées", "% de la demande"])

        # Données ligne par ligne
        for i in range(nb_r):
            for j in range(nb_c):
                val = sol.get((i, j), 0)
                if val > 0:   # on n'écrit que les flux non nuls
                    # On récupère la demande depuis resultat si disponible
                    writer.writerow([
                        regions[i],
                        centres[j],
                        f"{val:.1f}",
                        "",    # sera rempli si on passe les demandes
                    ])

        writer.writerow([])

        # Utilisation des centres
        writer.writerow(["=== UTILISATION DES CENTRES ==="])
        writer.writerow(["Centre", "Requêtes reçues", "Capacité max", "Taux d'utilisation"])
        for j, (centre, util) in enumerate(zip(centres, resultat["utilisation"].values())):
            writer.writerow([
                centre,
                f"{util['recu']:.1f}",
                util["capacite"],
                f"{util['pourcentage']:.1f}%"
            ])

    return chemin_fichier


# =============================================================================
# SAUVEGARDE D'UN SCÉNARIO (format JSON-like en texte)
# =============================================================================

def sauvegarder_scenario(nom, demandes, capacites, couts, regions, centres, chemin=None):
    """
    Sauvegarde les paramètres d'un scénario dans un fichier texte structuré.
    Permet de recharger le scénario plus tard depuis l'IHM.
    """
    import json

    if chemin is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        chemin = f"scenario_{nom}_{ts}.json"

    donnees = {
        "nom"      : nom,
        "date"     : datetime.now().isoformat(),
        "regions"  : regions,
        "centres"  : centres,
        "demandes" : demandes,
        "capacites": capacites,
        "couts"    : couts,
    }

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    return chemin


def charger_scenario(chemin):
    """
    Charge un scénario depuis un fichier JSON.
    Retourne un dictionnaire avec toutes les données.
    """
    import json

    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    with open(chemin, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    return donnees
