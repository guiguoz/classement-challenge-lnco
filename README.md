# 🏃 Challenge Raids Orientation

Application de gestion des classements pour les challenges de raids d'orientation (Trotteur, Orienteur, Raideur).

## ✨ Fonctionnalités

### Import des résultats
- Import de fichiers Excel (.xlsx) ou CSV
- Support jusqu'à 4 coéquipiers par équipe
- Détection automatique des doublons et conflits de noms
- Normalisation intelligente des catégories :
  - Homme / H / Hommes / **Masculin** → Homme
  - Femme / F / Femmes / **Féminin / Feminin** → Femme
  - Mixte / M / Mixtes → Mixte

### Gestion des données
- Création et gestion des saisons/challenges (ex : 2025-2026)
- Ajout, modification et suppression des participants
- Modification des points directement depuis le classement
- Gestion des raids (renommage, changement de date, suppression)

### Classement
- Classement dynamique par circuit et catégorie
- Calcul automatique des points selon le rang dans la catégorie
- Export PDF par catégorie ou classement complet
- Export PDF des statistiques globales (tous circuits réunis) : participants par course avec détail Hommes / Femmes / Mixtes
- Vainqueurs affichés uniquement à l'issue des 7 courses (classement définitif)

### Maintenance & Qualité des données
- **Détection des coureurs invalides** : noms vides ou mal formatés avec possibilité de correction ou suppression
- **Détection des doublons** : participants inscrits plusieurs fois sur une même course
- **Détection des points aberrants** : résultats avec plus de 35 points
- Notifications automatiques quand des problèmes sont détectés

### Sauvegardes
- Sauvegarde automatique quotidienne
- Sauvegarde manuelle à la demande
- Conservation de 30 jours, nettoyage automatique des sauvegardes plus anciennes

### Historique
- Traçabilité complète des modifications (ajouts, modifications, suppressions)
- Détail des changements de points avec participant, course, circuit et catégorie

## 🚀 Installation

### Prérequis
- Python 3.10+

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 💻 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

Ou double-cliquez sur `run.bat` (Windows). Le script détecte automatiquement Python et installe les dépendances si nécessaire.

L'application s'ouvre dans votre navigateur à l'adresse `http://localhost:8501`.

### Navigation

| Page | Description |
|------|-------------|
| **Import** | Importer des fichiers de résultats, créer/supprimer des challenges |
| **Édition** | Ajouter des participants, gérer les raids, maintenance des données, sauvegardes, historique |
| **Classement** | Consulter et modifier les classements, exporter en PDF, supprimer des participants |

## 📁 Structure du projet

```
├── app.py              # Application principale Streamlit
├── database.py         # Gestion de la base de données SQLite
├── utils.py            # Fonctions utilitaires (calcul points, PDF)
├── backup.py           # Système de sauvegarde automatique
├── audit.py            # Historique des modifications
├── dashboard.py        # Tableaux de bord et statistiques
├── challenge.db        # Base de données SQLite
├── requirements.txt    # Dépendances Python
├── run.bat             # Lanceur Windows
├── backups/            # Dossier des sauvegardes automatiques
└── classements/        # Fichiers sources Excel et exports PDF
```

## 🏆 Circuits

| Circuit | Description |
|---------|-------------|
| Trotteur | Niveau débutant |
| Orienteur | Niveau intermédiaire |
| Raideur | Niveau expert |

## 📊 Calcul des points

Les points sont attribués automatiquement selon le classement dans la catégorie :

| Rang | Points |
|------|--------|
| 1er | 35 pts |
| 2ème | 32 pts |
| 3ème | 29 pts |
| 4ème | 27 pts |
| 5ème | 26 pts |
| 6ème | 25 pts |
| 7ème–30ème | 31 − rang |
| 31ème+ | 1 pt |

## 🔧 Configuration

L'application utilise SQLite comme base de données locale (`challenge.db`). Aucune configuration supplémentaire n'est requise.

## 📝 Licence & Mentions Légales

### Propriété

© 2024-2026 Guillaume Lemiègre — Tous droits réservés.

### Développement

Cette application a été développée avec l'assistance d'une intelligence artificielle (Claude/Anthropic).

### Clause de non-responsabilité

CE LOGICIEL EST FOURNI "TEL QUEL", SANS GARANTIE D'AUCUNE SORTE, EXPRESSE OU IMPLICITE, Y COMPRIS, MAIS SANS S'Y LIMITER, LES GARANTIES DE QUALITÉ MARCHANDE, D'ADÉQUATION À UN USAGE PARTICULIER ET DE NON-VIOLATION.

EN AUCUN CAS L'AUTEUR OU LES CONTRIBUTEURS NE POURRONT ÊTRE TENUS RESPONSABLES DE TOUT DOMMAGE DIRECT, INDIRECT, ACCESSOIRE, SPÉCIAL, EXEMPLAIRE OU CONSÉCUTIF DÉCOULANT DE L'UTILISATION DE CE LOGICIEL.

### Données personnelles

Les données saisies dans cette application sont stockées localement sur votre machine. L'auteur ne collecte aucune donnée personnelle.

### Contact

Pour toute question : Guillaume Lemiègre

---

*Développé avec [Streamlit](https://streamlit.io) et l'assistance de l'IA*
