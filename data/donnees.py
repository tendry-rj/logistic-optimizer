# =============================================================================
# FICHIER : data/donnees.py
# RÔLE    : Couche données — toutes les données du problème sont ici.
#           Un seul endroit à modifier si les données changent.
# =============================================================================

# --- Noms des régions et des centres ---
# On les stocke dans des listes pour pouvoir les utiliser partout
REGIONS  = ["R1", "R2", "R3", "R4"]   # 4 régions sources de requêtes
CENTRES  = ["C1", "C2", "C3"]          # 3 centres de traitement

# --- Demandes par région ---
# DEMANDES[i] = nombre de requêtes que la région i doit faire traiter
# R1 a 1200 requêtes, R2 en a 900, etc.
DEMANDES = [1200, 900, 700, 600]

# --- Capacités maximales des centres ---
# CAPACITES[j] = nombre maximum de requêtes que le centre j peut traiter
# C1 peut traiter jusqu'à 1500 requêtes, C2 jusqu'à 1200, C3 jusqu'à 1000
CAPACITES = [1500, 1200, 1000]

# --- Coûts unitaires de traitement ---
# COUTS[i][j] = coût pour traiter UNE requête de la région i dans le centre j
# Exemple : COUTS[0][0] = 5  → traiter 1 requête de R1 dans C1 coûte 5
# Exemple : COUTS[0][2] = 7  → traiter 1 requête de R1 dans C3 coûte 7
COUTS = [
    # C1  C2  C3
    [5,   4,   6],   # R1
    [6,   5,   4],   # R2
    [7,   6,   5],   # R3
    [8,   7,   6],   # R4
]

# --- Constantes du modèle ---
# Nombre de régions et de centres, calculés automatiquement
# Utile pour éviter les "magic numbers" dans le code
NB_REGIONS = len(REGIONS)    # = 4
NB_CENTRES = len(CENTRES)    # = 3

# --- Contraintes supplémentaires (Partie F) ---
# Pourcentage maximum qu'un centre peut traiter d'une même région (60%)
MAX_POURCENTAGE_PAR_REGION = 0.60

# Seuil au-delà duquel une pénalité s'applique (90% de capacité)
SEUIL_PENALITE = 0.90

# Coût fixe d'activation d'un centre (si on l'utilise, on paye ce montant)
COUT_FIXE_ACTIVATION = [500, 400, 300]  # C1, C2, C3


# --- Fonction utilitaire ---
def get_donnees_par_defaut():
    """
    Retourne un dictionnaire contenant toutes les données initiales du problème.
    Utile pour réinitialiser les données depuis l'IHM.
    """
    return {
        "regions"   : REGIONS.copy(),
        "centres"   : CENTRES.copy(),
        "demandes"  : DEMANDES.copy(),
        "capacites" : CAPACITES.copy(),
        "couts"     : [ligne.copy() for ligne in COUTS],  # copie profonde de la matrice
    }
