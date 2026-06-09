# Optimisation Logistique Numérique
## Projet L3 Informatique — Modélisation Mathématique 2026

---

## Installation des dépendances

```bash
pip install pulp PyQt5 matplotlib numpy pandas
```

## Lancement de l'application

```bash
python main.py
```

## Structure du projet

```
projet_logistique/
├── main.py                        ← Point d'entrée
├── data/
│   └── donnees.py                 ← Données du problème
├── model/
│   └── optimisation.py            ← Résolution PuLP
├── ui/
│   └── fenetre_principale.py      ← Interface PyQt5
├── visualization/
│   └── graphiques.py              ← Graphiques matplotlib
└── export/
    └── export_resultats.py        ← Export CSV / JSON
```

## Technologie IHM
**PyQt5** — interface graphique native multi-plateforme.

## Fonctionnalités implémentées
- Saisie et modification des demandes, capacités, coûts
- Résolution du problème de programmation linéaire (PuLP / CBC)
- Affichage de la solution optimale sous forme de tableau
- 4 graphiques : flux, capacités, heatmap coûts, comparaison scénarios
- 5 scénarios prédéfinis testables en un clic
- Contraintes avancées (Partie F) activables
- Export CSV et sauvegarde/chargement de scénarios JSON
- Coloration automatique des centres saturés
