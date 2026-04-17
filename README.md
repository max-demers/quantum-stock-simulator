# Simulateur de Prix d'Action par Mécanique Quantique (PI)

Ce projet propose une approche originale et visuelle pour modéliser l'évolution du prix d'un actif financier en utilisant les processus mathématiques de la mécanique quantique. Le prix de l'actif (action, or, etc.) est représenté par un paquet d'ondes de probabilités qui évolue au cours du temps face à des "barrières de potentiel", représentant les niveaux de support et de résistance du marché boursier.

## 🚀 Fonctionnalités Principales

- **Initialisation dynamique** : Modélisation des rendements historiques d'un actif via l'API `yfinance` pour extraire la volatilité (dispersion) et le drift (tendance directionnelle).
- **Processus quantique (Équation de Schrödinger)** : Implémentation du Hamiltonien avec énergie cinétique (basée sur la volatilité) et création de puits et barrières de potentiel.
- **Résolution Numérique Spatio-Temporelle** : Utilisation de la modélisation différentielle implicite (Méthode de Crank-Nicolson) pour faire évoluer le système de façon stable.
- **Visualisations Interactives & Statiques** : Animations en temps réel de la densité de probabilité se fracassant sur les résistances et graphiques comparatifs mettant en évidence les effets d'accumulation et d'effet tunnel probabiliste.

## 📁 Architecture du Projet

Le projet a évolué et intègre désormais trois cas d'usage démontrant la puissance de l'outil :

1. `main.py` : **Simulateur Standard Interactif**
   C'est le module racine de l'application (historiquement exécuté sur l'actif `SPY`). Il calcule la fonction d'onde, gère l'animation de l'évolution des densités de probabilités en temps réel et détecte les franchissements de niveau (breakouts).
2. `Comparaison.py` : **Étude d'Impact des Barrières de Résistances**
   Permet d'exécuter la simulation sous deux univers parallèles : le modèle probabiliste lisse avec et sans les perturbations induites par les limites boursières. Le script génère un magnifique visuel statique comparatif illustrant ce que permettent vos barrières (création visuelle d'un rebond) et le calcul "d'effet tunnel" induit par le bris de confiance du marché.
3. `Gold.py` : **Test Chronologique Rétrospectif sur l'Or (`GC=F`)**
   Isole l'entraînement des données du Hamiltonien (2020-2023) pour tester le paquet d'ondes dans le futur (2023). Superpose le *prix réel historique* de l'actif en overlay de l'animation probabilisée quantique.

## 🛠️ Prérequis et Installation

Assurez-vous de disposer de Python 3.8+ et installez les dépendances nécessaires présentes au projet :

```bash
# Installation recommandée via le nouveau fichier de référence
pip install -r requirements.txt
```
*(Alternative manual) : `pip install numpy matplotlib yfinance scipy`*


## 💻 Utilisation

### Lancer la simulation de base (Animation Continue)
```bash
python main.py
```

### Lancer la démonstration de l'effet des barrières (Graphique Comparatif)
```bash
python Comparaison.py
```

### Lancer le backtest sur l'Or en lien avec le prix historique
```bash
python Gold.py
```

### Configuration des Paramètres
Dans chacun de ces scripts d’exécution (sous le bloc conditionnel de lancement standard `if __name__ == "__main__":`), de nombreuses constantes algorithmiques sont paramétrables :
- `action` : Le symbole boursier Yahoo Finance pris pour cible d'étude (ex. "SPY", "GC=F", "AAPL").
- `resistance_price_val` : Tableau des niveaux de prix symboliques agissant comme points de frictions.
- `barrier_thickness` : Proportion d'espace du spectre probabilisable accaparé par ladite résistance.
- `potential_strength` : Un coefficient massique simulant un bouclier ou un rebond plus complexe pour le Hamiltonien.

## 💡 Bonnes pratiques et Mises aux normes (Recommandations Futures)

Pour poursuivre la transformation professionnelle de cette plateforme analytique quantique vers des « standards de l'industrie technologique », voici plusieurs initiatives logicielles qui pourraient être appliquées à l'avenir :

1. **Modularisation et Extraction de Bibliothèque** : Actuellement, des fonctions comme `create_initial_wave_packet` ou `build_hamiltonian` sont dans `main.py`, puis importées laborieusement (`import main`) par d'autres scripts. ➡️ *Idéal : Placer ces logiques complexes dans un sous-dossier `core/` ou `physics_engine.py` dédié uniquement aux mathématiques.*
2. **Centraliser la Configuration Boursière** : Gérer les données de la variable `barrier_thickness` ou `resistance_price_val` au moyen d'un fichier externe tel qu'un environnement YAML (`config.yaml`) ou JSON pour découpler la donnée simulée de la formulation logicielle métier.
3. **Journalisation Applicative (Logs)** : Substituer l'instruction `print()` par l'utilisation de la bibliothèque officielle de traçabilité `logging` en Python, ceci permet un archivage sécuritaire de la donnée exécutive du produit.
4. **Validation de Qualité (Typage)** : Documenter avec plus d'exactitude les signatures, par l'utilisation du *Type Hinting*, ex: `def fast_simulation(psi: np.ndarray, dt: float) -> np.ndarray:`.

## ⚠️ Avertissement

Le déploiement de ces éléments informatiques correspond à une ingénierie mathématique et théorique pure. **Il ne représente aucune garantie, ne saurait faire l'objet de prévisions assurées et n'implique ni conseil patrimonial ni recommandation avisée d'investissement.**
