#  Optimisation Logistique - Problème de Transport

**Application desktop** de résolution du **problème de transport à coût minimal** par **programmation linéaire** avec **PuLP + CBC**.

### Fonctionnalités

- Interface graphique moderne avec **PyQt5**
- Saisie interactive des demandes, capacités et coûts unitaires
- Résolution automatique du problème d'optimisation
- 4 visualisations claires avec **Matplotlib** :
  - Répartition des flux (barres groupées)
  - Utilisation des capacités des centres
  - Heatmap des coûts effectifs
  - Comparaison de scénarios
- 5 scénarios prédéfinis testables en un clic
- Contraintes avancées (Partie F) activables
- Export des résultats en **CSV**
- Sauvegarde et chargement de scénarios en **JSON**

### Technologies

- **Python** 3.8+
- **PyQt5** — Interface graphique
- **PuLP + CBC** — Programmation linéaire
- **Matplotlib + NumPy** — Visualisations
- **Pandas** (gestion des données)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/tonusername/logistic-optimizer.git
cd logistic-optimizer

# 2. Créer un environnement virtuel
python -m venv venv

# Windows :
venv\Scripts\activate
# Linux / Mac :
# source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

### Structure du projet

```bash
logistic-optimizer/
├── main.py                    # Point d'entrée
├── data/                      # Données du problème
├── model/                     # Modèle PuLP
├── ui/                        # Interface PyQt5
├── visualization/             # Graphiques Matplotlib
├── export/                    # Export CSV & JSON
├── scenarios/                 # Scénarios prédéfinis
├── requirements.txt
├── .gitignore
└── LICENSE
```

### Licence
Ce projet est distribué sous **licence MIT** (voir le fichier LICENSE).

