import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.linalg import solve_banded


def initialize_parameters(N, action, resistance_prices=None):
    ticker = yf.Ticker(action)
    initial_price = ticker.fast_info["last_price"] # Prix intital de l'action
    df = yf.download(action,period="100d",interval="1h") # Récolte des prix sur l'action choisie
    prices = df['Close'].values.flatten() # On prend seulement les valeurs de fermeture
    log_return = np.diff(np.log(prices)) # Différence entre deux éléments consécutifs
    v_0 = np.std(log_return) # Calcul de l'écart-type (volatilité)
    mu = np.mean(log_return) # Moyenne arithmétique des différences de prix pour trouvée le drift
    k_0 = mu/(v_0**2) # Calcul du drift moyen
    x_0 = np.log(initial_price)  # Position (x) de l'action

    # Ajustement de la plage pour inclure les barrières si présentes
    x_min = x_0 - 0.1
    x_max = x_0 + 0.1
    if resistance_prices: # Permet d'ajuster les limites
        max_res = np.log(max(resistance_prices) * 1.05)
        min_res = np.log(min(resistance_prices) * 0.95)
        x_min = min(x_min, min_res)
        x_max = max(x_max, max_res)

    x = np.linspace(x_min, x_max, N)  # Variation du log prix
    dx = x[1] - x[0] # Longueur d'un point
    mass = 1 / v_0 ** 2  # Inertie de l'action
    return x_0, x, dx, mass, k_0, v_0, initial_price


def create_initial_wave_packet(x, x_0, v_0, k_0):
    gaussian = np.exp(-((x - x_0) ** 2) / (4 * v_0 ** 2))  # Création de la cloche Gaussienne
    phase = np.exp(1j * k_0 * x)  # Le terme de phase permet le déplacement de x
    A = (1 / (2 * np.pi * v_0 ** 2)) ** (1 / 4)  # Constante pour que l'aire sous la courbe soit de 1
    psi = A * gaussian * phase  # L'état complet de l'action
    return psi


def build_hamiltonian(N, dx, mass, x, resistance_price, V_0, barrier_thickness):
    K_coeff = -1 / (2 * mass * dx**2)   # Calcul du coefficient de l'énergie cinétique
    potential_vector = np.zeros(N) # Création du vecteur de potentiel
    for price, thick, strength in zip(resistance_price, barrier_thickness, V_0): # Permet de mettre plusieurs barrières
        log_start = np.log(price) # Emplacement de la résistance
        log_end = np.log(price + thick) # Fin de la résistance
        delta_x = log_end-log_start # Largeur de la résistance
        L_point = int(round(delta_x/dx)) # Largeur en point sur le graphique de la résistance
        L_point = max(1,L_point) # Protection contre une épaisseur de moins qu'un point
        idx = (np.abs(x - log_start)).argmin()  # Index de la barrière
        potential_vector[idx: idx + L_point] = strength  # Création de la barrière
    return K_coeff, potential_vector


def run_simulation_and_animate(psi, K_coeff, dt, S, x, potential_vector, steps_per_frame=10, resistance_price=None, barrier_thickness=None):
    # Préparation pour la simulation (logique de Crank-Nicolson)
    alpha = 1j * dt / 2
    H_diag = potential_vector + K_coeff*(-2) # Diagonale principal du Hamiltonian
    diag_main_ML = 1+alpha*H_diag # Diagonale principale de la matrice de gauche
    diag_off_ML = alpha * K_coeff # Diagonales secondaires de la matrice de gauche
    M_L_banded = np.zeros((3, len(psi)), dtype=complex) # Créationd de la matrice en bande pour sauver de la RAM
    M_L_banded[0, 1:] = diag_off_ML # Ajout de la diagonale secondaire supérieure
    M_L_banded[1, :] = diag_main_ML # Ajout de la diagonale principale
    M_L_banded[2, :-1] = diag_off_ML # Ajout de la diagonale secondaire inférieure

    # Préparation des indices pour le calcul des probabilités de breakout
    breakout_indices = []
    dx = x[1] - x[0]
    if resistance_price is not None and barrier_thickness is not None: # Si j'ai des valeurs
        for p, t in zip(resistance_price, barrier_thickness):
            log_end = np.log(p + t)
            idx = (np.abs(x - log_end)).argmin()
            breakout_indices.append(idx) # Création d'une liste des effets tunels

    #Configuration du graphique
    plt.ion()  # Activer le mode interactif
    fig, ax = plt.subplots(figsize=(12, 7))

    prob_initial = np.abs(psi) ** 2 # Calcul de la probabilité
    prob_line, = ax.plot(x, prob_initial, label="Probabilité du prix (Action)", color="blue") # Courbe de la probabilité
    fill_collection = ax.fill_between(x, prob_initial, color="blue", alpha=0.2) # Remplissage de l'aire sous la courbe des probabilités

    # Normaliser le potentiel une seule fois pour le mettre à l'échelle
    V_abs = np.abs(potential_vector)
    V_log = np.log1p(V_abs) 
    V_norm = (V_log / np.max(V_log) if np.max(V_log) > 0 else 1)
    V_plot = V_norm * np.sign(potential_vector) # Garde le signe pour supports/résistances
    
    potential_line, = ax.plot(x, V_plot * np.max(prob_initial), label="Obstacles (Résistances/Supports)",
                              color="red", linestyle="--", alpha=0.5)

    # Création des labels de texte pour les probabilités
    prob_labels = [ax.text(x[idx], 0, "", color="darkred", fontweight="bold", ha="center", fontsize=9) 
                   for idx in breakout_indices]

    ax.set_xlabel("Log(Prix)")
    ax.set_ylabel("Densité de Probabilité")
    ax.set_title(f"Simulation Quantique de l'Action")
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

            # Gérer la zone remplie
            fill_collection.remove()
            fill_collection = ax.fill_between(x, prob, color="blue", alpha=0.2)

            # Ajuster les limites de l'axe Y
            new_ylim_top = np.max(prob) * 1.5
            ax.set_ylim(min(-0.05, np.min(V_plot)*new_ylim_top), new_ylim_top)

            # Mettre à jour la hauteur de la barrière
            potential_line.set_ydata(V_plot * new_ylim_top * 0.7)

            # Mise à jour des probabilités de breakout
            for j, idx in enumerate(breakout_indices):
                p_breakout = np.sum(prob[idx:]) * dx
                prob_labels[j].set_text(f"Breakout:\n{p_breakout:.1%}")
                prob_labels[j].set_position((x[idx], new_ylim_top * 0.75))

            plt.draw()
            plt.pause(0.016)

    plt.ioff()
    plt.show()

    return psi


if __name__ == "__main__":
    time_step = 0.01
    num_iterations = 55000
    update_frequency = 1
    num_points = 20000
    barrier_thickness = [1.5, 0.75, 1.0, 2.0] 
    potential_strength = [200, 120, 160, 400]
    resistance_price_val = [185, 182.5, 177.5, 172] 
    action = "NVDA" 

    # 1. Initialisation avec prise en compte des résistances pour la plage
    x_0, x, dx, mass, initial_drift, initial_volatility, initial_price = initialize_parameters(num_points, action, resistance_price_val)

    # 2. Création de la fonction d'ondes initiale
    psi_initial = create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Construction du Hamiltonien
    K_coeff, potential_vector = build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength,
                                            barrier_thickness)

    # 4. Lancement de la simulation et de l'animation avec les nouveaux paramètres
    psi_final = run_simulation_and_animate(psi_initial, K_coeff, time_step, num_iterations, x, potential_vector, 
                                          update_frequency, resistance_price_val, barrier_thickness)
