# Simulateur de Prix d'Action par Mécanique Quantique

Ce projet propose une approche originale pour modéliser l'évolution du prix d'une action en utilisant les principes de la mécanique quantique. Le prix de l'action est représenté par un paquet d'ondes (fonction d'onde) qui évolue au cours du temps face à des "barrières de potentiel" représentant les niveaux de support et de résistance du marché.

## Fonctionnalités Principales

1. **Initialisation des Paramètres** : Télécharge automatiquement les données historiques récentes d'une action (via `yfinance`) pour calculer sa volatilité intrinsèque et son drift (tendance).
2. **Création du Paquet d'Ondes** : Génère une fonction d'onde initiale (gaussienne) centrée sur le prix actuel de l'action.
3. **Construction du Hamiltonien** : Intègre l'énergie cinétique (basée sur la volatilité du marché) et crée des barrières de potentiel modélisant les zones de résistance ou de support.
4. **Évolution Temporelle (Crank-Nicolson)** : Fait évoluer la fonction d'onde de manière stable dans le temps pour observer comment la probabilité du prix se déplace et interagit avec les obstacles.
5. **Visualisation Interactive** : Affiche une animation en temps réel de la densité de probabilité du prix de l'action frappant les barrières de résistance, avec le calcul dynamique des probabilités de "breakout" (cassure de résistance).

## Prérequis

Assurez-vous d'avoir installé les bibliothèques Python suivantes :

```bash
pip install numpy matplotlib yfinance scipy datetime
```

## Utilisation

Pour lancer la simulation, exécutez simplement le script `main.py` :

```bash
python main.py
```

### Configuration des paramètres

Vous pouvez modifier les paramètres de la simulation directement à la fin du fichier `main.py` dans le bloc `if __name__ == "__main__":` :

- `action` : Le symbole boursier (ticker) de l'action à analyser (par défaut `"SPY"`).
- `resistance_price_val` : Liste des prix où se situent les barrières de résistance.
- `barrier_thickness` : L'épaisseur (en log-prix) de chaque barrière.
- `potential_strength` : La force ou "hauteur" de chaque barrière de potentiel.
- `time_step` (`dt`) : Le pas de temps pour l'évolution de la simulation.
- `num_iterations` : Le nombre total d'itérations de la simulation.

## Structure du Code

- `initialize_parameters()` : Calcule les paramètres physiques de l'action (masse relative à l'inertie, drift `k_0`, volatilité `v_0`) depuis l'API Yahoo Finance.
- `create_initial_wave_packet()` : Construit l'état quantique initial du marché sous forme de cloche de Gauss.
- `build_hamiltonian()` : Génère l'opérateur d'énergie totale, définissant les zones où le prix aura de la difficulté à passer (les résistances).
- `run_simulation_and_animate()` : Cœur de la simulation. Résout l'équation de Schrödinger dépendante du temps par la méthode des différences finies (Crank-Nicolson) et met à jour le graphique animé.

## Avertissement

Ce projet est une expérimentation théorique et mathématique visant à appliquer des concepts de physique quantique à la finance. **Il ne constitue en aucun cas un outil de conseil financier ou d'aide à l'investissement.**
