import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.linalg import solve_banded


def initialize_parameters(price, N, action):
    df = yf.download(action,period="7d",interval="1h") # Récolte des prix sur l'action choisie
    prices = df['Close'].values.flatten() # On prend seulement la valeur de fermeture puis transforme en vecteur
    log_return = np.diff(np.log(prices)) # Différence entre deux éléments consécutifs
    v_0 = np.std(log_return) # Calcul de l'écart-type (volatilité)
    mu = np.mean(log_return) # Moyenne arithmétique des différences de prix pour trouvée le drift
    k_0 = mu/(v_0**2) # Calcul du drift moyen
    x_0 = np.log(price)  # Position (x) de l'action
    x = np.linspace(5.5, 7, N)  # Variation du log prix
    dx = x[1] - x[0]
    mass = 1 / v_0 ** 2  # Inertie de l'action
    return x_0, x, dx, mass,k_0,v_0


def create_initial_wave_packet(x, x_0, v_0, k_0):
    gaussian = np.exp(-((x - x_0) ** 2) / (4 * v_0 ** 2))  # Création de la cloche Gaussienne
    phase = np.exp(1j * k_0 * x)  # Le terme de phase permet le déplacement de x
    A = (1 / (2 * np.pi * v_0 ** 2)) ** (1 / 4)  # Constante pour que l'aire sous la courbe soit de 1
    psi = A * gaussian * phase  # L'état complet de l'action
    return psi


def build_hamiltonian(N, dx, mass, x, resistance_price, V_0, L_point):
    # Création de la matrice pour la dérivé seconde par différence finie (Matrice de transformation)
    main_diag = -2 * np.ones(N)
    off_diag = np.ones(N - 1)
    M_T = (np.diag(main_diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k=-1))
    K = -1 / (2 * mass * dx ** 2) * M_T  # Calcul de l'énergie cinétique

    # Création de la matrice de potentiel
    potential_vector = np.zeros(N)
    for price in resistance_price: # Permet de mettre plusieurs barrières
        x_res = np.log(price)  # Trouve l'emplacement de la barrière
        idx = (np.abs(x - x_res)).argmin()  # Index de la barrière
        potential_vector[idx: idx + L_point] = V_0  # Création de la barrière
    V = np.diag(potential_vector)  # Matrice de potentiel

    H = K + V  # Création du Hamiltonien
    return H, potential_vector


def run_simulation_and_animate(psi, H, dt, S, x, potential_vector, steps_per_frame=10):
    # Préparation pour la simulation (logique de Crank-Nicolson)
    N = H.shape[0]
    M_L = np.eye(N) + (1j * dt / 2) * H
    M_R = np.eye(N) - (1j * dt / 2) * H
    # Matrice en bande pour sauver de la RAM
    diag_main = np.diag(M_L)
    diag_up = np.diag(M_L, k=1)
    diag_down = np.diag(M_L, k=-1)
    M_L_banded = np.zeros((3, len(psi)), dtype=complex)
    M_L_banded[0, 1:] = diag_up
    M_L_banded[1, :] = diag_main
    M_L_banded[2, :-1] = diag_down

    #Configuration du graphique
    plt.ion()  # Activer le mode interactif
    fig, ax = plt.subplots(figsize=(10, 6))

    prob_initial = np.abs(psi) ** 2
    prob_line, = ax.plot(x, prob_initial, label="Probabilité du prix (Action)", color="blue")
    fill_collection = ax.fill_between(x, prob_initial, color="blue", alpha=0.2)

    # Normaliser le potentiel une seule fois pour le mettre à l'échelle
    V_norm = potential_vector / (np.max(potential_vector) if np.max(potential_vector) > 0 else 1)
    # Afficher la barrière de potentiel, mise à l'échelle de la hauteur initiale du graphique
    potential_line, = ax.plot(x, V_norm * np.max(prob_initial) * 1.2, label="Barrière de potentiel (Résistance)",
                              color="red")

    ax.set_xlabel("Log(Prix)")
    ax.set_ylabel("Densité de Probabilité")
    ax.legend()
    ax.grid(alpha=0.3)

    # Boucle de simulation et d'animation
    for i in range(S):
        # Fait évoluer la fonction d'onde
        B = M_R.dot(psi)
        psi = solve_banded((1, 1), M_L_banded, B)

        # Met à jour le graphique toutes les 'steps_per_frame' itérations
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
            potential_line.set_ydata(V_norm * new_ylim_top)

            plt.draw()
            plt.pause(0.016)  # Ralentit l'animation

    plt.ioff()  # Désactiver le mode interactif
    plt.show()  # Affiche le graphique final

    return psi


if __name__ == "__main__":
    time_step = 0.1 #Temps de chaque itération
    num_iterations = 5000  # Nombre total d'itérations
    update_frequency = 1  # Mettre à jour le graphique toutes les x itérations (ralentit le mouvement)
    initial_price = 500 # Prix initial
    num_points = 10000 # Précision du graphique
    barrier_thickness = 20 # Épaisseur de la barrière
    potential_strength = 100 # Force de la barrière de potentiel
    resistance_price_val = [300,800] # Doit toujours être une liste
    action = "NVDA" # Nom de l'action qu'on suit

    # 1. Initialisation
    x_0, x, dx, mass,initial_drift,initial_volatility = initialize_parameters(initial_price, num_points, action)

    # 2. Création de la fonction d'ondes initiale
    psi_initial = create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Construction du Hamiltonien
    H, potential_vector = build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength,
                                            barrier_thickness)

    # 4. Lancement de la simulation et de l'animation
    psi_final = run_simulation_and_animate(psi_initial, H, time_step, num_iterations, x, potential_vector,
                                           steps_per_frame=update_frequency)
