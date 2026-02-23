import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.linalg import solve_banded


def initialize_parameters(N, action):
    ticker = yf.Ticker(action)
    initial_price = ticker.fast_info["last_price"] # Prix intital de l'action
    df = yf.download(action,period="7d",interval="1h") # Récolte des prix sur l'action choisie
    prices = df['Close'].values.flatten() # On prend seulement la valeur de fermeture puis transforme en vecteur
    log_return = np.diff(np.log(prices)) # Différence entre deux éléments consécutifs
    v_0 = np.std(log_return) # Calcul de l'écart-type (volatilité)
    mu = np.mean(log_return) # Moyenne arithmétique des différences de prix pour trouvée le drift
    k_0 = mu/(v_0**2) # Calcul du drift moyen
    x_0 = np.log(initial_price)  # Position (x) de l'action
    x = np.linspace(x_0-0.5, x_0+0.5, N)  # Variation du log prix selon la position initiale
    dx = x[1] - x[0]
    mass = 1 / v_0 ** 2  # Inertie de l'action
    return x_0, x, dx, mass, k_0, v_0, initial_price


def create_initial_wave_packet(x, x_0, v_0, k_0):
    gaussian = np.exp(-((x - x_0) ** 2) / (4 * v_0 ** 2))  # Création de la cloche Gaussienne
    phase = np.exp(1j * k_0 * x)  # Le terme de phase permet le déplacement de x
    A = (1 / (2 * np.pi * v_0 ** 2)) ** (1 / 4)  # Constante pour que l'aire sous la courbe soit de 1
    psi = A * gaussian * phase  # L'état complet de l'action
    return psi


def build_hamiltonian(N, dx, mass, x, resistance_price, V_0, barrier_thickness):
    K_coeff = -1 / (2 * mass * dx ** 2)   # Calcul du coefficient de l'énergie cinétique
    potential_vector = np.zeros(N) # Création du vecteur de potentiel
    for price, thick, strength in zip(resistance_price, barrier_thickness, V_0): # Permet de mettre plusieurs barrières
        log_start = np.log(price) # Emplacement de la résistance
        log_end = np.log(price + thick) # Fin de la résistance
        delta_x = log_end-log_start # Largeur de la résistance
        L_point = int(round(delta_x/N)) # Largeur en point sur le graphique de la résistance
        L_point = max(1,L_point) # Protection contre une épaisseur de moins qu'un point
        idx = (np.abs(x - log_start)).argmin()  # Index de la barrière
        potential_vector[idx: idx + L_point] = strength  # Création de la barrière
    return K_coeff, potential_vector


def run_simulation_and_animate(psi, K_coeff, dt, S, x, potential_vector, steps_per_frame=10):
    # Préparation pour la simulation (logique de Crank-Nicolson)
    alpha = 1j * dt / 2
    H_diag = potential_vector + K_coeff*(-2) # Diagonale principal du Hamiltonian
    diag_main_ML = 1+alpha*H_diag # Diagonale principale de la matrice de gauche
    diag_off_ML = alpha * K_coeff # Diagonales secondaires de la matrice de gauche
    M_L_banded = np.zeros((3, len(psi)), dtype=complex) # Créationd de la matrice en bande pour sauver de la RAM
    M_L_banded[0, 1:] = diag_off_ML # Ajout de la diagonale secondaire supérieure
    M_L_banded[1, :] = diag_main_ML # Ajout de la diagonale principale
    M_L_banded[2, :-1] = diag_off_ML # Ajout de la diagonale secondaire inférieure

    #Configuration du graphique
    plt.ion()  # Activer le mode interactif
    fig, ax = plt.subplots(figsize=(10, 6))

    prob_initial = np.abs(psi) ** 2 # Calcul de la probabilité
    prob_line, = ax.plot(x, prob_initial, label="Probabilité du prix (Action)", color="blue") # Courbe de la probabilité
    fill_collection = ax.fill_between(x, prob_initial, color="blue", alpha=0.2) # Remplissage de l'aire sous la courbe des probabilités

    # Normaliser le potentiel une seule fois pour le mettre à l'échelle
    V_log = np.log1p(potential_vector) # Utilisation des log pour éviter les grands écarts
    V_norm = (V_log / np.max(V_log) if np.max(V_log) > 0 else 1)
    # Afficher la barrière de potentiel, mise à l'échelle de la hauteur initiale du graphique
    potential_line, = ax.plot(x, V_norm * np.max(prob_initial), label="Barrière de potentiel (Résistance)",
                              color="red")

    ax.set_xlabel("Log(Prix)")
    ax.set_ylabel("Densité de Probabilité")
    ax.legend()
    ax.grid(alpha=0.3)

    # Boucle de simulation et d'animation
    for i in range(S):
        # Création des trois diagonales de la matrice résultante du produit scalaire entre psi et M_L
        term_H_psi = H_diag*psi
        term_H_psi[1:] += K_coeff * psi[:-1]
        term_H_psi[:-1] += K_coeff * psi[1:]
        # Fait évoluer la fonction d'onde
        B = psi - alpha * term_H_psi
        psi = solve_banded((1, 1), M_L_banded, B)

        # Met à jour le graphique toutes les x itérations
        if i % steps_per_frame == 0:
            prob = np.abs(psi) ** 2
            prob_line.set_ydata(prob)

            # Gérer la zone remplie (il faut la supprimer et la redessiner)
            fill_collection.remove()
            fill_collection = ax.fill_between(x, prob, color="blue", alpha=0.2)

            # Ajuster les limites de l'axe Y pour que la vague reste visible
            new_ylim_top = np.max(prob) * 1.2
            ax.set_ylim(0, new_ylim_top)

            # Mettre à jour la hauteur de la barrière pour qu'elle corresponde à la nouvelle hauteur du graphique
            potential_line.set_ydata(V_norm * new_ylim_top * 0.95)

            plt.draw()
            plt.pause(0.016)  # Ralentit l'animation

    plt.ioff()  # Désactiver le mode interactif
    plt.show()  # Affiche le graphique final

    return psi


if __name__ == "__main__":
    time_step = 0.1 #Temps de chaque itération
    num_iterations = 5000  # Nombre total d'itérations
    update_frequency = 1  # Mettre à jour le graphique toutes les x itérations (ralentit le mouvement)
    num_points = 30000 # Précision du graphique
    barrier_thickness = [55,5.75] # Différentes épaisseur des barrières en dollars
    potential_strength = [20,100] # Force des barrière de potentiel
    resistance_price_val = [140,200] # Différents prix des résistances
    action = "NVDA" # Nom de l'action qu'on suit

    # 1. Initialisation
    x_0, x, dx, mass,initial_drift,initial_volatility, initial_price = initialize_parameters(num_points, action)

    # 2. Création de la fonction d'ondes initiale
    psi_initial = create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Construction du Hamiltonien
    K_coeff, potential_vector = build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength,
                                            barrier_thickness)

    # 4. Lancement de la simulation et de l'animation
    psi_final = run_simulation_and_animate(psi_initial, K_coeff, time_step, num_iterations, x, potential_vector,
                                           steps_per_frame=update_frequency)
