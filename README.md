# Simulateur de Prix d'Action par Mécanique Quantique (PI)

Ce projet propose une approche originale et visuelle pour modéliser l'évolution du prix d'un actif financier en utilisant les processus mathématiques de la mécanique quantique. Le prix de l'actif (action, or, etc.) est représenté par un paquet d'ondes de probabilités qui évolue au cours du temps face à des "barrières de potentiel", représentant les niveaux de support et de résistance du marché boursier.

## 🚀 Fonctionnalités Principales

- **Initialisation dynamique** : Modélisation des rendements historiques d'un actif via l'API `yfinance` pour extraire la volatilité (dispersion) et le drift (tendance directionnelle).
- **Processus quantique (Équation de Schrödinger)** : Implémentation du Hamiltonien avec énergie cinétique (basée sur la volatilité) et création de puits et barrières de potentiel.
- **Résolution Numérique Spatio-Temporelle** : Utilisation de la modélisation différentielle implicite (Méthode de Crank-Nicolson) pour faire évoluer le système de façon stable.
- **Visualisations Interactives & Statiques** : Animations en temps réel de la densité de probabilité se fracassant sur les résistances et graphiques comparatifs mettant en évidence les effets d'accumulation et d'effet tunnel probabiliste.

## 📁 Architecture du Projet

Le projet est architecturé autour d'un cœur mathématique et de trois scripts d'entrée distincts qui l'exploitent :

1. `quantum_engine.py` : **Le Cœur du Moteur Quantique**
   C'est la bibliothèque contenant les fonctions fondamentales : méthodes mathématiques (Crank-Nicolson), création de la matrice du Hamiltonien, génération des paquets d'ondes et interface de rendu d'animation. Les scripts ci-dessous s'en servent comme socle.
2. `main.py` : **Simulateur Standard Interactif**
   C'est le point de lancement basique (configuré sur `SPY`). Il appelle le moteur pour animer l'évolution des densités de probabilités en temps réel et détecter les franchissements (breakouts).
3. `Comparaison.py` : **Étude d'Impact des Barrières de Résistances**
   Ce script exploite le moteur pour exécuter la simulation sous deux univers parallèles : le modèle probabiliste lisse avec et sans les barrières de limites boursières. Il génère un visuel comparatif illustrant la création du "rebond" et du calcul "d'effet tunnel".
4. `Gold.py` : **Test Chronologique Rétrospectif sur l'Or (`GC=F`)**
   Sépare les données historiques (2020-2023) pour tester la projection probabilisée (2023). Le script lance le moteur sur l'Or et superpose le *prix réel historique* en overlay de l'animation pour évaluer la capacité prédictive du Hamiltonien.

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


## ⚠️ Avertissement

Le déploiement de ces éléments informatiques correspond à une ingénierie mathématique et théorique pure. **Il ne représente aucune garantie, ne saurait faire l'objet de prévisions assurées et n'implique ni conseil patrimonial ni recommandation avisée d'investissement.**
