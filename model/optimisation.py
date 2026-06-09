# =============================================================================
# FICHIER : model/optimisation.py
# RÔLE    : Couche modélisation — formule et résout le problème de PL.
#           Utilise la bibliothèque PuLP pour la programmation linéaire.
# =============================================================================

import pulp  # bibliothèque de programmation linéaire


# =============================================================================
# FONCTION PRINCIPALE DE RÉSOLUTION
# =============================================================================

def resoudre(demandes, capacites, couts, contraintes_avancees=False):
    """
    Résout le problème de transport (minimisation du coût).

    Paramètres :
        demandes  (list)  : demandes[i] = nb requêtes de la région i
        capacites (list)  : capacites[j] = capacité max du centre j
        couts     (list)  : couts[i][j]  = coût unitaire région i → centre j
        contraintes_avancees (bool) : si True, ajoute les contraintes de la Partie F

    Retourne :
        dict avec statut, variables x[i][j], coût total, et détails
    """

    nb_regions = len(demandes)   # nombre de lignes (4 régions)
    nb_centres = len(capacites)  # nombre de colonnes (3 centres)

    # -------------------------------------------------------------------------
    # ÉTAPE 1 : Créer le problème PuLP
    # "Minimisation" car on veut le coût le plus faible possible
    # -------------------------------------------------------------------------
    probleme = pulp.LpProblem(
        name  = "Optimisation_Logistique",
        sense = pulp.LpMinimize   # on minimise (≠ LpMaximize)
    )

    # -------------------------------------------------------------------------
    # ÉTAPE 2 : Définir les variables de décision x[i][j]
    # x[i][j] = nombre de requêtes de la région i envoyées au centre j
    # lowBound=0 impose x[i][j] >= 0 (on ne peut pas envoyer un nb négatif)
    # cat='Continuous' permet des valeurs décimales (on peut mettre 'Integer' si besoin)
    # -------------------------------------------------------------------------
    x = {}
    for i in range(nb_regions):
        for j in range(nb_centres):
            # Nom de la variable : x_R1_C1, x_R1_C2, etc. → utile pour le debug
            nom_var = f"x_R{i+1}_C{j+1}"
            x[i, j] = pulp.LpVariable(name=nom_var, lowBound=0, cat='Continuous')

    # -------------------------------------------------------------------------
    # ÉTAPE 3 : Définir la fonction objectif (ce qu'on minimise)
    # Coût total = somme sur toutes les paires (i,j) de : coût[i][j] * x[i][j]
    # pulp.lpSum() est l'équivalent PuLP du Σ mathématique
    # -------------------------------------------------------------------------
    probleme += pulp.lpSum(
        couts[i][j] * x[i, j]
        for i in range(nb_regions)
        for j in range(nb_centres)
    ), "Cout_Total"   # on donne un nom à la fonction objectif

    # -------------------------------------------------------------------------
    # ÉTAPE 4 : Contraintes de demande
    # Pour chaque région i : la somme des requêtes envoyées à tous les centres
    # doit EXACTEMENT couvrir la demande de cette région
    # Mathématiquement : Σ_j x[i][j] = demandes[i]   ∀i
    # -------------------------------------------------------------------------
    for i in range(nb_regions):
        probleme += (
            pulp.lpSum(x[i, j] for j in range(nb_centres)) == demandes[i],
            f"Demande_R{i+1}"   # nom de la contrainte pour le rapport
        )

    # -------------------------------------------------------------------------
    # ÉTAPE 5 : Contraintes de capacité
    # Pour chaque centre j : la somme des requêtes reçues de toutes les régions
    # ne doit PAS dépasser la capacité maximale du centre
    # Mathématiquement : Σ_i x[i][j] <= capacites[j]   ∀j
    # -------------------------------------------------------------------------
    for j in range(nb_centres):
        probleme += (
            pulp.lpSum(x[i, j] for i in range(nb_regions)) <= capacites[j],
            f"Capacite_C{j+1}"
        )

    # -------------------------------------------------------------------------
    # ÉTAPE 6 (optionnelle) : Contraintes avancées (Partie F)
    # -------------------------------------------------------------------------
    if contraintes_avancees:
        _ajouter_contraintes_avancees(probleme, x, demandes, capacites, nb_regions, nb_centres)

    # -------------------------------------------------------------------------
    # ÉTAPE 7 : Résolution avec le solveur par défaut (CBC, inclus dans PuLP)
    # msg=0 désactive les logs du solveur dans le terminal
    # -------------------------------------------------------------------------
    solveur = pulp.PULP_CBC_CMD(msg=0)
    statut_code = probleme.solve(solveur)

    # -------------------------------------------------------------------------
    # ÉTAPE 8 : Récupérer et retourner les résultats
    # -------------------------------------------------------------------------
    statut = pulp.LpStatus[statut_code]  # "Optimal", "Infeasible", etc.

    if statut != "Optimal":
        # Si pas de solution trouvée (ex: capacité insuffisante)
        return {
            "statut"    : statut,
            "optimal"   : False,
            "message"   : f"Aucune solution optimale trouvée. Statut : {statut}",
            "solution"  : None,
            "cout_total": None,
        }

    # Extraire les valeurs de x[i][j] après résolution
    # pulp.value(var) retourne la valeur numérique de la variable
    solution = {}
    for i in range(nb_regions):
        for j in range(nb_centres):
            val = pulp.value(x[i, j])
            solution[i, j] = round(val, 2) if val is not None else 0.0

    # Calculer le coût total optimal
    cout_total = pulp.value(probleme.objective)

    # Calculer l'utilisation de chaque centre (en % de sa capacité)
    utilisation = {}
    for j in range(nb_centres):
        total_recu = sum(solution[i, j] for i in range(nb_regions))
        utilisation[j] = {
            "recu"      : total_recu,
            "capacite"  : capacites[j],
            "pourcentage": round((total_recu / capacites[j]) * 100, 1)
        }

    return {
        "statut"      : statut,
        "optimal"     : True,
        "solution"    : solution,        # x[i,j] pour chaque paire (région, centre)
        "cout_total"  : round(cout_total, 2),
        "utilisation" : utilisation,     # taux d'utilisation de chaque centre
        "nb_regions"  : nb_regions,
        "nb_centres"  : nb_centres,
    }


# =============================================================================
# CONTRAINTES AVANCÉES (Partie F)
# =============================================================================

def _ajouter_contraintes_avancees(probleme, x, demandes, capacites, nb_regions, nb_centres):
    """
    Ajoute les contraintes supplémentaires de la Partie F.
    Cette fonction est appelée uniquement si contraintes_avancees=True.
    """

    # Contrainte F1 : Un centre ne peut pas traiter plus de 60% des requêtes
    # d'une même région
    # x[i][j] <= 0.60 * demandes[i]   ∀i, ∀j
    for i in range(nb_regions):
        for j in range(nb_centres):
            probleme += (
                x[i, j] <= 0.60 * demandes[i],
                f"Max60pct_R{i+1}_C{j+1}"
            )

    # Contrainte F2 : Le centre C3 (index 2) ne peut pas traiter les requêtes
    # de R4 (index 3)
    # x[3][2] = 0
    if nb_regions > 3 and nb_centres > 2:
        probleme += (
            x[3, 2] == 0,
            "C3_interdit_R4"
        )

    # Contrainte F3 : Pénalité si un centre dépasse 90% de sa capacité
    # On modélise ça en ajoutant une variable de dépassement d[j] >= 0
    # et en ajoutant son coût (ici coût * 1.5) à la fonction objectif
    # Note : cette contrainte modifie la fonction objectif, elle est donc
    # appliquée séparément dans une version avancée.
    # Ici on impose simplement que chaque centre ne dépasse pas 90%
    for j in range(nb_centres):
        seuil = 0.90 * capacites[j]
        probleme += (
            pulp.lpSum(x[i, j] for i in range(nb_regions)) <= seuil,
            f"Seuil90pct_C{j+1}"
        )


# =============================================================================
# VÉRIFICATION DES CONTRAINTES
# =============================================================================

def verifier_contraintes(solution, demandes, capacites):
    """
    Vérifie que la solution respecte bien toutes les contraintes.
    Retourne une liste de messages (vide si tout est bon).
    """
    nb_regions = len(demandes)
    nb_centres = len(capacites)
    erreurs = []

    # Vérifier les demandes
    for i in range(nb_regions):
        total = sum(solution.get((i, j), 0) for j in range(nb_centres))
        if abs(total - demandes[i]) > 0.01:  # tolérance numérique
            erreurs.append(
                f"⚠ R{i+1} : {total:.1f} traitées ≠ {demandes[i]} demandées"
            )

    # Vérifier les capacités
    for j in range(nb_centres):
        total = sum(solution.get((i, j), 0) for i in range(nb_regions))
        if total > capacites[j] + 0.01:
            erreurs.append(
                f"⚠ C{j+1} : {total:.1f} reçues > {capacites[j]} de capacité"
            )

    return erreurs


# =============================================================================
# GÉNÉRATION DU RÉSUMÉ TEXTUEL
# =============================================================================

def generer_resume(resultat, regions, centres):
    """
    Génère un résumé lisible des résultats de l'optimisation.
    Retourne une chaîne de caractères formatée.
    """
    if not resultat["optimal"]:
        return f"❌ Optimisation échouée : {resultat['message']}"

    lignes = []
    lignes.append("=" * 50)
    lignes.append("   RÉSULTATS DE L'OPTIMISATION")
    lignes.append("=" * 50)
    lignes.append(f"\n✅ Statut : {resultat['statut']}")
    lignes.append(f"💰 Coût total optimal : {resultat['cout_total']:.2f} €\n")

    lignes.append("📦 Répartition des requêtes :")
    lignes.append("-" * 40)

    sol = resultat["solution"]
    nb_r = resultat["nb_regions"]
    nb_c = resultat["nb_centres"]

    # Afficher la matrice solution sous forme de tableau texte
    header = "        " + "  ".join(f"{c:>8}" for c in centres)
    lignes.append(header)

    for i in range(nb_r):
        row = f"{regions[i]:>6}  " + "  ".join(
            f"{sol.get((i,j), 0):>8.1f}" for j in range(nb_c)
        )
        lignes.append(row)

    lignes.append("\n📊 Utilisation des centres :")
    lignes.append("-" * 40)
    for j, (centre, util) in enumerate(zip(centres, resultat["utilisation"].values())):
        barre = "█" * int(util["pourcentage"] / 5)  # barre visuelle en texte
        lignes.append(
            f"{centre} : {util['recu']:>6.1f}/{util['capacite']}  "
            f"({util['pourcentage']:>5.1f}%)  {barre}"
        )

    return "\n".join(lignes)
