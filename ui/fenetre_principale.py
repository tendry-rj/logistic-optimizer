# =============================================================================
# FICHIER : ui/fenetre_principale.py
# RÔLE    : Couche IHM — interface PyQt5 complète de l'application.
#           Permet la saisie, le calcul, la visualisation et l'export.
# =============================================================================

import sys
import os

# Ajout du dossier parent au path Python pour les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QComboBox, QCheckBox,
    QGroupBox, QSplitter, QStatusBar, QFrame
)
from PyQt5.QtCore    import Qt, QThread, pyqtSignal
from PyQt5.QtGui     import QFont, QColor, QPalette

# Intégration matplotlib dans PyQt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Nos modules
from data.donnees             import get_donnees_par_defaut
from model.optimisation       import resoudre, verifier_contraintes, generer_resume
from visualization.graphiques import (
    graphique_flux, graphique_capacites,
    graphique_heatmap_couts, graphique_comparaison_scenarios
)
from export.export_resultats  import exporter_csv, sauvegarder_scenario, charger_scenario


# =============================================================================
# THÈME COULEURS (style clair moderne)
# =============================================================================
STYLE_GLOBAL = """
    QMainWindow, QWidget {
        background-color: #F5F7FA;
        color: #2C3E50;
        font-family: 'Segoe UI', 'Ubuntu', sans-serif;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #D0D8E4;
        background: #F5F7FA;
        border-radius: 0 6px 6px 6px;
    }
    QTabBar::tab {
        background: #E2E8F0;
        color: #5A6A7E;
        padding: 8px 20px;
        border-radius: 4px 4px 0 0;
        margin-right: 2px;
        border: 1px solid #D0D8E4;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background: #2A72D5;
        color: white;
        font-weight: bold;
        border-color: #2A72D5;
    }
    QTabBar::tab:hover:!selected {
        background: #CBD5E1;
        color: #2C3E50;
    }
    QPushButton {
        background-color: #2A72D5;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
    }
    QPushButton:hover   { background-color: #3A82E5; }
    QPushButton:pressed { background-color: #1A62C5; }
    QPushButton#btn_danger {
        background-color: #E74C3C;
        color: white;
    }
    QPushButton#btn_danger:hover { background-color: #F05C4B; }
    QPushButton#btn_success {
        background-color: #27AE60;
        color: white;
    }
    QPushButton#btn_success:hover { background-color: #2ECC71; }
    QLineEdit, QTextEdit {
        background-color: #FFFFFF;
        border: 1px solid #BDC9D7;
        border-radius: 4px;
        padding: 4px 8px;
        color: #2C3E50;
        selection-background-color: #2A72D5;
        selection-color: #FFFFFF;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #2A72D5;
        color: #2C3E50;
    }
    QTableWidget {
        background-color: #FFFFFF;
        gridline-color: #D0D8E4;
        color: #2C3E50;
        selection-background-color: #DBEAFE;
        selection-color: #1E3A5F;
        border: 1px solid #D0D8E4;
        border-radius: 4px;
    }
    QTableWidget::item { padding: 4px; color: #2C3E50; }
    QTableWidget::item:selected {
        background-color: #DBEAFE;
        color: #1E3A5F;
    }
    QHeaderView::section {
        background-color: #E2E8F0;
        color: #4A5568;
        padding: 6px;
        border: none;
        border-right: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
        font-weight: bold;
    }
    QGroupBox {
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 12px;
        background-color: #FFFFFF;
        color: #4A5568;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        background-color: #FFFFFF;
        color: #2A72D5;
    }
    QLabel#label_titre {
        font-size: 18px;
        font-weight: bold;
        color: #2A72D5;
    }
    QLabel#label_cout {
        font-size: 22px;
        font-weight: bold;
        color: #27AE60;
    }
    QLabel {
        color: #2C3E50;
        background-color: transparent;
    }
    QCheckBox { color: #2C3E50; spacing: 8px; }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border: 2px solid #BDC9D7;
        border-radius: 3px;
        background-color: #FFFFFF;
    }
    QCheckBox::indicator:checked {
        background-color: #2A72D5;
        border-color: #2A72D5;
    }
    QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #BDC9D7;
        border-radius: 4px;
        padding: 4px 8px;
        color: #2C3E50;
        min-width: 200px;
    }
    QComboBox:focus {
        border: 2px solid #2A72D5;
    }
    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        color: #2C3E50;
        selection-background-color: #DBEAFE;
        selection-color: #1E3A5F;
        border: 1px solid #BDC9D7;
    }
    QStatusBar {
        background-color: #E2E8F0;
        color: #4A5568;
        border-top: 1px solid #CBD5E1;
    }
    QFrame {
        background-color: #F5F7FA;
    }
    QScrollBar:vertical {
        background: #E2E8F0;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #94A3B8;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #64748B;
    }
"""


# =============================================================================
# THREAD DE CALCUL (pour ne pas bloquer l'interface pendant l'optimisation)
# =============================================================================

class ThreadCalcul(QThread):
    """
    Lance l'optimisation dans un thread séparé pour éviter que l'interface
    se bloque pendant le calcul (important pour de grands problèmes).
    """
    # Signal émis quand le calcul est terminé
    calcul_termine = pyqtSignal(dict)
    # Signal émis en cas d'erreur
    erreur         = pyqtSignal(str)

    def __init__(self, demandes, capacites, couts, contraintes_avancees):
        super().__init__()
        self.demandes             = demandes
        self.capacites            = capacites
        self.couts                = couts
        self.contraintes_avancees = contraintes_avancees

    def run(self):
        """Méthode exécutée dans le thread secondaire."""
        try:
            resultat = resoudre(
                self.demandes,
                self.capacites,
                self.couts,
                self.contraintes_avancees
            )
            self.calcul_termine.emit(resultat)   # envoie le résultat à l'IHM
        except Exception as e:
            self.erreur.emit(str(e))


# =============================================================================
# FENÊTRE PRINCIPALE
# =============================================================================

class FenetrePrincipale(QMainWindow):
    """
    Fenêtre principale de l'application.
    Contient 4 onglets : Données, Résultats, Graphiques, Scénarios.
    """

    def __init__(self):
        super().__init__()

        # --- Données courantes (initialisées avec les valeurs par défaut) ---
        donnees = get_donnees_par_defaut()
        self.regions   = donnees["regions"]
        self.centres   = donnees["centres"]
        self.demandes  = donnees["demandes"]
        self.capacites = donnees["capacites"]
        self.couts     = donnees["couts"]

        # --- Résultat de la dernière optimisation ---
        self.resultat_courant = None

        # --- Historique des scénarios pour comparaison ---
        self.historique_scenarios = []

        # --- Construction de l'interface ---
        self._configurer_fenetre()
        self._construire_interface()
        self._appliquer_style()

    # -------------------------------------------------------------------------
    # CONFIGURATION GÉNÉRALE DE LA FENÊTRE
    # -------------------------------------------------------------------------

    def _configurer_fenetre(self):
        """Titre, taille, icône de la fenêtre principale."""
        self.setWindowTitle("Optimisation Logistique Numérique — L3 Informatique")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 800)

        # Barre de statut en bas
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt. Modifiez les données puis lancez le calcul.")

    def _appliquer_style(self):
        """Applique le thème clair à toute l'application."""
        self.setStyleSheet(STYLE_GLOBAL)

    # -------------------------------------------------------------------------
    # CONSTRUCTION DE L'INTERFACE PRINCIPALE
    # -------------------------------------------------------------------------

    def _construire_interface(self):
        """Crée le widget central avec le système d'onglets."""
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(10, 10, 10, 10)

        # Titre en haut
        titre = QLabel("Système d'Optimisation Logistique")
        titre.setObjectName("label_titre")
        titre.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(titre)

        # Système d'onglets
        self.onglets = QTabWidget()
        layout_principal.addWidget(self.onglets)

        # Créer les 4 onglets
        self.onglets.addTab(self._creer_onglet_donnees(),    " Données")
        self.onglets.addTab(self._creer_onglet_resultats(),  " Résultats")
        self.onglets.addTab(self._creer_onglet_graphiques(), " Graphiques")
        self.onglets.addTab(self._creer_onglet_scenarios(),  " Scénarios")

    # =========================================================================
    # ONGLET 1 : DONNÉES
    # =========================================================================

    def _creer_onglet_donnees(self):
        """
        Onglet permettant de saisir/modifier :
        - les demandes par région
        - les capacités des centres
        - la matrice des coûts
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # ---- Section Demandes ----
        grp_demandes = QGroupBox("Demandes par région (nb de requêtes)")
        layout_dem   = QHBoxLayout(grp_demandes)

        STYLE_CHAMP = """
            QLineEdit {
                color: #2C3E50;
                background-color: #FFFFFF;
                border: 2px solid #BDC9D7;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #2A72D5;
            }
        """
        self.champs_demandes = []
        for i, (region, val) in enumerate(zip(self.regions, self.demandes)):
            col = QVBoxLayout()
            lbl = QLabel(region)
            lbl.setStyleSheet("color: #4A5568; font-weight: bold;")
            col.addWidget(lbl)
            champ = QLineEdit(str(int(val)))
            champ.setFixedWidth(110)
            champ.setMinimumHeight(34)
            champ.setAlignment(Qt.AlignCenter)
            champ.setEchoMode(QLineEdit.Normal)
            champ.setStyleSheet(STYLE_CHAMP)
            self.champs_demandes.append(champ)
            col.addWidget(champ)
            layout_dem.addLayout(col)

        layout_dem.addStretch()
        layout.addWidget(grp_demandes)

        # ---- Section Capacités ----
        grp_capa  = QGroupBox("Capacités maximales des centres")
        layout_cap = QHBoxLayout(grp_capa)

        self.champs_capacites = []
        for j, (centre, val) in enumerate(zip(self.centres, self.capacites)):
            col = QVBoxLayout()
            lbl = QLabel(centre)
            lbl.setStyleSheet("color: #4A5568; font-weight: bold;")
            col.addWidget(lbl)
            champ = QLineEdit(str(int(val)))
            champ.setFixedWidth(110)
            champ.setMinimumHeight(34)
            champ.setAlignment(Qt.AlignCenter)
            champ.setEchoMode(QLineEdit.Normal)
            champ.setStyleSheet(STYLE_CHAMP)
            self.champs_capacites.append(champ)
            col.addWidget(champ)
            layout_cap.addLayout(col)

        layout_cap.addStretch()
        layout.addWidget(grp_capa)

        # ---- Section Coûts (tableau modifiable) ----
        grp_couts  = QGroupBox("Coûts unitaires de traitement (lignes=Régions, colonnes=Centres)")
        layout_cout = QVBoxLayout(grp_couts)

        self.table_couts = QTableWidget(len(self.regions), len(self.centres))
        self.table_couts.setHorizontalHeaderLabels(self.centres)
        self.table_couts.setVerticalHeaderLabels(self.regions)
        self.table_couts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Remplir le tableau avec les valeurs initiales
        for i in range(len(self.regions)):
            for j in range(len(self.centres)):
                item = QTableWidgetItem(str(self.couts[i][j]))
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#2C3E50"))
                self.table_couts.setItem(i, j, item)

        layout_cout.addWidget(self.table_couts)
        layout.addWidget(grp_couts)

        # ---- Options avancées ----
        grp_options = QGroupBox("Options")
        layout_opt  = QHBoxLayout(grp_options)
        self.cb_contraintes_avancees = QCheckBox("Activer les contraintes avancées (Partie F)")
        self.cb_contraintes_avancees.setToolTip(
            "Ajoute : max 60% par région, C3 ne traite pas R4, seuil 90%"
        )
        layout_opt.addWidget(self.cb_contraintes_avancees)
        layout_opt.addStretch()
        layout.addWidget(grp_options)

        # ---- Boutons ----
        layout_boutons = QHBoxLayout()

        btn_reinit = QPushButton(" Réinitialiser")
        btn_reinit.setObjectName("btn_danger")
        btn_reinit.clicked.connect(self._reinitialiser_donnees)

        btn_calculer = QPushButton(" Lancer l'optimisation")
        btn_calculer.setObjectName("btn_success")
        btn_calculer.setFixedHeight(40)
        btn_calculer.clicked.connect(self._lancer_calcul)

        layout_boutons.addWidget(btn_reinit)
        layout_boutons.addStretch()
        layout_boutons.addWidget(btn_calculer)

        layout.addLayout(layout_boutons)
        layout.addStretch()
        return widget

    # =========================================================================
    # ONGLET 2 : RÉSULTATS
    # =========================================================================

    def _creer_onglet_resultats(self):
        """Affiche la solution optimale, le coût et le récapitulatif."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Coût total (grand affichage)
        self.label_cout = QLabel(" Coût total : —")
        self.label_cout.setObjectName("label_cout")
        self.label_cout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_cout)

        # Tableau de la solution x[i][j]
        grp_sol = QGroupBox("Répartition optimale des requêtes")
        layout_sol = QVBoxLayout(grp_sol)

        self.table_solution = QTableWidget(len(self.regions), len(self.centres))
        self.table_solution.setHorizontalHeaderLabels(self.centres)
        self.table_solution.setVerticalHeaderLabels(self.regions)
        self.table_solution.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_solution.setEditTriggers(QTableWidget.NoEditTriggers)  # lecture seule
        layout_sol.addWidget(self.table_solution)
        layout.addWidget(grp_sol)

        # Résumé textuel (rapport lisible)
        grp_resume = QGroupBox("Résumé détaillé")
        layout_res = QVBoxLayout(grp_resume)
        self.texte_resume = QTextEdit()
        self.texte_resume.setReadOnly(True)
        self.texte_resume.setFont(QFont("Courier New", 10))
        self.texte_resume.setFixedHeight(180)
        layout_res.addWidget(self.texte_resume)
        layout.addWidget(grp_resume)

        # Boutons export
        layout_btns = QHBoxLayout()
        btn_csv = QPushButton(" Exporter en CSV")
        btn_csv.clicked.connect(self._exporter_csv)
        btn_save = QPushButton(" Sauvegarder scénario")
        btn_save.clicked.connect(self._sauvegarder_scenario)
        layout_btns.addWidget(btn_csv)
        layout_btns.addWidget(btn_save)
        layout_btns.addStretch()
        layout.addLayout(layout_btns)

        return widget

    # =========================================================================
    # ONGLET 3 : GRAPHIQUES
    # =========================================================================

    def _creer_onglet_graphiques(self):
        """Affiche les 4 graphiques matplotlib intégrés dans l'interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sélecteur de graphique
        layout_select = QHBoxLayout()
        layout_select.addWidget(QLabel("Graphique à afficher :"))
        self.combo_graphique = QComboBox()
        self.combo_graphique.addItems([
            "Répartition des flux",
            "Utilisation des capacités",
            "Heatmap des coûts",
            "Comparaison des scénarios",
        ])
        self.combo_graphique.currentIndexChanged.connect(self._afficher_graphique)
        layout_select.addWidget(self.combo_graphique)
        layout_select.addStretch()
        layout.addLayout(layout_select)

        # Zone d'affichage du graphique
        self.frame_graphique = QFrame()
        self.frame_graphique.setFrameShape(QFrame.StyledPanel)
        self.layout_graphique = QVBoxLayout(self.frame_graphique)

        # Placeholder avant calcul
        self.label_placeholder = QLabel("Lancez d'abord une optimisation pour voir les graphiques.")
        self.label_placeholder.setAlignment(Qt.AlignCenter)
        self.layout_graphique.addWidget(self.label_placeholder)

        layout.addWidget(self.frame_graphique)
        self.canvas_actuel = None
        return widget

    # =========================================================================
    # ONGLET 4 : SCÉNARIOS
    # =========================================================================

    def _creer_onglet_scenarios(self):
        """Permet de tester les 5 scénarios prédéfinis et de comparer."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        grp_scenarios = QGroupBox("Scénarios prédéfinis (Partie E)")
        layout_sc = QVBoxLayout(grp_scenarios)

        # Description des scénarios
        scenarios_info = [
            ("Scénario 1", "Augmentation de 20% des demandes"),
            ("Scénario 2", "Réduction de 25% de la capacité de C2"),
            ("Scénario 3", "Augmentation de 30% des coûts de C3"),
            ("Scénario 4", "Indisponibilité de C2 (capacité = 0)"),
            ("Scénario 5", "Contrainte custom : R1 prioritaire (max 10% vers C3)"),
        ]

        self.boutons_scenarios = []
        for nom, desc in scenarios_info:
            ligne = QHBoxLayout()
            lbl   = QLabel(f"<b>{nom}</b> — {desc}")
            btn   = QPushButton("▶ Tester")
            btn.setFixedWidth(90)
            btn.clicked.connect(lambda _, n=nom: self._tester_scenario(n))
            ligne.addWidget(lbl)
            ligne.addStretch()
            ligne.addWidget(btn)
            layout_sc.addLayout(ligne)
            self.boutons_scenarios.append(btn)

        layout.addWidget(grp_scenarios)

        # Tableau de comparaison des scénarios testés
        grp_comp = QGroupBox("Historique et comparaison des scénarios")
        layout_comp = QVBoxLayout(grp_comp)

        self.table_historique = QTableWidget(0, 3)
        self.table_historique.setHorizontalHeaderLabels(["Scénario", "Coût total (€)", "Δ vs Base (%)"])
        self.table_historique.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_historique.setEditTriggers(QTableWidget.NoEditTriggers)
        layout_comp.addWidget(self.table_historique)

        btn_comparer = QPushButton(" Générer graphique de comparaison")
        btn_comparer.clicked.connect(self._comparer_scenarios)
        layout_comp.addWidget(btn_comparer)

        layout.addWidget(grp_comp)
        layout.addStretch()
        return widget

    # =========================================================================
    # LOGIQUE MÉTIER — Lecture et validation des données
    # =========================================================================

    def _lire_donnees_interface(self):
        """
        Lit les valeurs saisies dans l'interface et les valide.
        Retourne (demandes, capacites, couts) ou lève ValueError si invalide.
        """
        erreurs = []

        # Lire les demandes
        demandes = []
        for i, champ in enumerate(self.champs_demandes):
            texte = champ.text().strip()
            try:
                val = float(texte)
                if val < 0:
                    erreurs.append(f"Demande R{i+1} : valeur négative interdite")
                demandes.append(val)
            except ValueError:
                erreurs.append(f"Demande R{i+1} : '{texte}' n'est pas un nombre")

        # Lire les capacités
        capacites = []
        for j, champ in enumerate(self.champs_capacites):
            texte = champ.text().strip()
            try:
                val = float(texte)
                if val < 0:
                    erreurs.append(f"Capacité C{j+1} : valeur négative interdite")
                capacites.append(val)
            except ValueError:
                erreurs.append(f"Capacité C{j+1} : '{texte}' n'est pas un nombre")

        # Lire la matrice des coûts
        couts = []
        for i in range(self.table_couts.rowCount()):
            ligne = []
            for j in range(self.table_couts.columnCount()):
                item = self.table_couts.item(i, j)
                texte = item.text().strip() if item else "0"
                try:
                    val = float(texte)
                    if val < 0:
                        erreurs.append(f"Coût R{i+1}/C{j+1} : valeur négative interdite")
                    ligne.append(val)
                except ValueError:
                    erreurs.append(f"Coût R{i+1}/C{j+1} : '{texte}' n'est pas un nombre")
            couts.append(ligne)

        # Vérification globale : capacité totale >= demande totale
        if not erreurs:
            if sum(capacites) < sum(demandes):
                erreurs.append(
                    f"⚠ Capacité totale ({sum(capacites)}) < Demande totale ({sum(demandes)})"
                    " → Problème infaisable !"
                )

        if erreurs:
            raise ValueError("\n".join(erreurs))

        return demandes, capacites, couts

    # =========================================================================
    # LOGIQUE MÉTIER — Lancement du calcul
    # =========================================================================

    def _lancer_calcul(self):
        """Valide les données et lance l'optimisation dans un thread."""
        try:
            demandes, capacites, couts = self._lire_donnees_interface()
        except ValueError as e:
            QMessageBox.critical(self, "Données invalides", str(e))
            return

        # Mémoriser les données utilisées pour ce calcul
        self.demandes  = demandes
        self.capacites = capacites
        self.couts     = couts

        contraintes_avancees = self.cb_contraintes_avancees.isChecked()

        # Désactiver le bouton pendant le calcul
        self.status_bar.showMessage("Calcul en cours...")

        # Lancer le thread de calcul
        self.thread = ThreadCalcul(demandes, capacites, couts, contraintes_avancees)
        self.thread.calcul_termine.connect(self._afficher_resultats)
        self.thread.erreur.connect(self._afficher_erreur_calcul)
        self.thread.start()

    def _afficher_erreur_calcul(self, msg):
        """Affiche une erreur survenue pendant le calcul."""
        QMessageBox.critical(self, "Erreur de calcul", msg)
        self.status_bar.showMessage("Erreur pendant le calcul.")

    # =========================================================================
    # LOGIQUE MÉTIER — Affichage des résultats
    # =========================================================================

    def _afficher_resultats(self, resultat):
        """
        Appelé quand le calcul est terminé.
        Met à jour l'onglet Résultats et les graphiques.
        """
        self.resultat_courant = resultat

        if not resultat["optimal"]:
            QMessageBox.warning(self, "Pas de solution", resultat.get("message", ""))
            self.status_bar.showMessage("Optimisation : aucune solution trouvée.")
            return

        # Mettre à jour le coût total
        cout = resultat["cout_total"]
        self.label_cout.setText(f"💰 Coût total optimal : {cout:,.2f} €")

        # Mettre à jour le tableau solution
        sol  = resultat["solution"]
        nb_r = resultat["nb_regions"]
        nb_c = resultat["nb_centres"]

        for i in range(nb_r):
            for j in range(nb_c):
                val  = sol.get((i, j), 0)
                item = QTableWidgetItem(f"{val:.1f}")
                item.setTextAlignment(Qt.AlignCenter)

                # Colorer les centres saturés (>= 90%) — tons clairs adaptés au thème clair
                util_j = resultat["utilisation"][j]
                if util_j["pourcentage"] >= 90:
                    item.setBackground(QColor("#FECACA"))   # rouge clair
                    item.setForeground(QColor("#991B1B"))
                elif util_j["pourcentage"] >= 70:
                    item.setBackground(QColor("#FDE68A"))   # orange/jaune clair
                    item.setForeground(QColor("#92400E"))

                self.table_solution.setItem(i, j, item)

        # Mettre à jour le résumé texte
        resume = generer_resume(resultat, self.regions, self.centres)
        self.texte_resume.setPlainText(resume)

        # Ajouter à l'historique des scénarios
        self.historique_scenarios.append({
            "nom"    : f"Calcul #{len(self.historique_scenarios)+1}",
            "cout"   : cout,
            "couleur": "#2A72D5",
        })
        self._maj_table_historique()

        # Afficher le graphique par défaut (flux)
        self._afficher_graphique()

        # Basculer vers l'onglet Résultats
        self.onglets.setCurrentIndex(1)
        self.status_bar.showMessage(f"✅ Optimisation réussie. Coût total : {cout:,.2f} €")

    # =========================================================================
    # GRAPHIQUES
    # =========================================================================

    def _afficher_graphique(self):
        """
        Génère et affiche le graphique sélectionné dans le combobox.
        Supprime l'ancien canvas avant d'en créer un nouveau.
        """
        if self.resultat_courant is None or not self.resultat_courant["optimal"]:
            return

        # Supprimer l'ancien canvas et le placeholder
        if self.canvas_actuel:
            self.layout_graphique.removeWidget(self.canvas_actuel)
            self.canvas_actuel.setParent(None)
            self.canvas_actuel = None

        if self.label_placeholder.parent():
            self.layout_graphique.removeWidget(self.label_placeholder)
            self.label_placeholder.hide()

        # Choisir le graphique selon la sélection
        index = self.combo_graphique.currentIndex()
        sol   = self.resultat_courant["solution"]
        util  = self.resultat_courant["utilisation"]

        if index == 0:
            fig = graphique_flux(sol, self.regions, self.centres)
        elif index == 1:
            fig = graphique_capacites(util, self.centres, self.capacites)
        elif index == 2:
            fig = graphique_heatmap_couts(sol, self.couts, self.regions, self.centres)
        elif index == 3:
            if len(self.historique_scenarios) < 2:
                QMessageBox.information(self, "Info", "Testez au moins 2 scénarios d'abord.")
                return
            fig = graphique_comparaison_scenarios(self.historique_scenarios)

        # Intégrer la figure matplotlib dans le widget PyQt
        canvas = FigureCanvas(fig)
        self.layout_graphique.addWidget(canvas)
        self.canvas_actuel = canvas

        # Basculer vers l'onglet graphiques
        self.onglets.setCurrentIndex(2)

    # =========================================================================
    # SCÉNARIOS
    # =========================================================================

    def _tester_scenario(self, nom_scenario):
        """
        Modifie les données selon le scénario choisi et lance le calcul.
        """
        from data.donnees import get_donnees_par_defaut
        base = get_donnees_par_defaut()

        demandes  = base["demandes"].copy()
        capacites = base["capacites"].copy()
        couts     = [l.copy() for l in base["couts"]]

        couleur = "#2A72D5"

        if nom_scenario == "Scénario 1":
            demandes = [int(d * 1.2) for d in demandes]
            couleur  = "#E8705A"

        elif nom_scenario == "Scénario 2":
            capacites[1] = int(capacites[1] * 0.75)
            couleur = "#F39C12"

        elif nom_scenario == "Scénario 3":
            couts = [
                [c if j != 2 else round(c * 1.3, 2) for j, c in enumerate(ligne)]
                for ligne in couts
            ]
            couleur = "#9B59B6"

        elif nom_scenario == "Scénario 4":
            capacites[1] = 0
            couleur = "#E74C3C"

        elif nom_scenario == "Scénario 5":
            couts[0][2] = 999
            couleur = "#27AE60"

        # Lancer le calcul avec les données modifiées
        self.status_bar.showMessage(f"Test du {nom_scenario} en cours...")

        self.thread = ThreadCalcul(demandes, capacites, couts, False)

        def on_done(res):
            if res["optimal"]:
                self.historique_scenarios.append({
                    "nom"    : nom_scenario,
                    "cout"   : res["cout_total"],
                    "couleur": couleur,
                })
                self._maj_table_historique()
                self.status_bar.showMessage(
                    f"{nom_scenario} → Coût : {res['cout_total']:,.2f} €"
                )
                QMessageBox.information(
                    self, nom_scenario,
                    f" Coût optimal : {res['cout_total']:,.2f} €\n"
                    + generer_resume(res, base["regions"], base["centres"])
                )
            else:
                QMessageBox.warning(self, nom_scenario, "Pas de solution pour ce scénario.")

        self.thread.calcul_termine.connect(on_done)
        self.thread.start()

    def _maj_table_historique(self):
        """Met à jour le tableau de comparaison des scénarios."""
        self.table_historique.setRowCount(len(self.historique_scenarios))
        cout_base = self.historique_scenarios[0]["cout"] if self.historique_scenarios else 1

        for row, sc in enumerate(self.historique_scenarios):
            delta = ((sc["cout"] - cout_base) / cout_base * 100) if cout_base else 0
            self.table_historique.setItem(row, 0, QTableWidgetItem(sc["nom"]))
            self.table_historique.setItem(row, 1, QTableWidgetItem(f"{sc['cout']:,.2f}"))
            item_delta = QTableWidgetItem(f"{delta:+.1f}%")
            if delta > 0:
                item_delta.setForeground(QColor("#C0392B"))   # rouge = plus cher
            elif delta < 0:
                item_delta.setForeground(QColor("#27AE60"))   # vert = moins cher
            self.table_historique.setItem(row, 2, item_delta)

    def _comparer_scenarios(self):
        """Affiche le graphique de comparaison des scénarios testés."""
        if len(self.historique_scenarios) < 2:
            QMessageBox.information(self, "Info", "Testez au moins 2 scénarios d'abord.")
            return
        self.combo_graphique.setCurrentIndex(3)
        self._afficher_graphique()

    # =========================================================================
    # EXPORT ET SAUVEGARDE
    # =========================================================================

    def _exporter_csv(self):
        """Ouvre une boîte de dialogue pour choisir où exporter le CSV."""
        if not self.resultat_courant or not self.resultat_courant["optimal"]:
            QMessageBox.warning(self, "Aucun résultat", "Lancez d'abord une optimisation.")
            return

        chemin, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", "solution.csv", "CSV (*.csv)"
        )
        if chemin:
            exporter_csv(self.resultat_courant, self.regions, self.centres, chemin)
            QMessageBox.information(self, "Export réussi", f"Fichier sauvegardé :\n{chemin}")

    def _sauvegarder_scenario(self):
        """Sauvegarde les données et résultats courants dans un fichier JSON."""
        if not self.resultat_courant or not self.resultat_courant["optimal"]:
            QMessageBox.warning(self, "Aucun résultat", "Lancez d'abord une optimisation.")
            return

        chemin, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le scénario", "scenario.json", "JSON (*.json)"
        )
        if chemin:
            sauvegarder_scenario(
                nom      = "Scénario sauvegardé",
                demandes = self.demandes,
                capacites= self.capacites,
                couts    = self.couts,
                regions  = self.regions,
                centres  = self.centres,
                chemin   = chemin,
            )
            QMessageBox.information(self, "Sauvegarde réussie", f"Scénario sauvegardé :\n{chemin}")

    def _reinitialiser_donnees(self):
        """Remet les données initiales dans tous les champs."""
        rep = QMessageBox.question(
            self, "Confirmation",
            "Réinitialiser toutes les données aux valeurs initiales ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if rep != QMessageBox.Yes:
            return

        base = get_donnees_par_defaut()
        for i, champ in enumerate(self.champs_demandes):
            champ.setText(str(base["demandes"][i]))
        for j, champ in enumerate(self.champs_capacites):
            champ.setText(str(base["capacites"][j]))
        for i in range(len(base["regions"])):
            for j in range(len(base["centres"])):
                self.table_couts.item(i, j).setText(str(base["couts"][i][j]))
        self.status_bar.showMessage("Données réinitialisées.")