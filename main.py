# =============================================================================
# FICHIER : main.py
# RÔLE    : Point d'entrée de l'application.
#           Lance l'interface PyQt5 avec palette sombre forcée.
# =============================================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPalette, QColor
from ui.fenetre_principale import FenetrePrincipale


def _appliquer_palette_sombre(app):
    """
    Force une palette sombre au niveau système (QPalette).
    C'est la méthode la plus robuste : elle s'applique quelle que soit
    la taille de la fenêtre, la plateforme (Windows/Linux/Mac) ou
    le thème OS. Contrairement au CSS seul, elle ne peut pas être
    écrasée au redimensionnement.
    """
    palette = QPalette()

    # --- Fonds ---
    palette.setColor(QPalette.Window,          QColor("#1E1E2E"))
    palette.setColor(QPalette.Base,            QColor("#2A2A3E"))
    palette.setColor(QPalette.AlternateBase,   QColor("#252535"))
    palette.setColor(QPalette.ToolTipBase,     QColor("#2A2A3E"))

    # --- Textes (c'est ici que le bug se trouvait) ---
    # Sans ces lignes, PyQt5 hérite du thème OS (texte noir)
    # qui devient invisible sur fond sombre au redimensionnement
    palette.setColor(QPalette.WindowText,      QColor("#FFFFFF"))
    palette.setColor(QPalette.Text,            QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipText,     QColor("#FFFFFF"))
    palette.setColor(QPalette.PlaceholderText, QColor("#888899"))
    palette.setColor(QPalette.BrightText,      QColor("#FFFFFF"))

    # --- Boutons ---
    palette.setColor(QPalette.Button,          QColor("#2A2A3E"))
    palette.setColor(QPalette.ButtonText,      QColor("#FFFFFF"))

    # --- Sélection ---
    palette.setColor(QPalette.Highlight,       QColor("#4A90D9"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    # --- Liens ---
    palette.setColor(QPalette.Link,            QColor("#4A90D9"))
    palette.setColor(QPalette.LinkVisited,     QColor("#7A60C9"))

    app.setPalette(palette)


def main():
    """Lance l'application PyQt5."""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Optimisation Logistique Numérique")
    app.setApplicationVersion("1.0")

    # IMPORTANT : palette appliquée AVANT la création de la fenêtre
    _appliquer_palette_sombre(app)

    fenetre = FenetrePrincipale()
    fenetre.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
