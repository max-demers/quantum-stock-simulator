import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve_banded

def initialize_parameters(price, v_0, N):
    x_0 = np.log(price) # Position (x) de l'action
    x = np.linspace(5.5,7,N) # Variation du log prix
    dx = x[1]-x[0]
    mass = 1 / v_0 ** 2  # Inertie de l'action
    return x_0, x, dx, mass

def create_initial_wave_packet(x,x_0,v_0,k_0):
    gaussian = np.exp(-((x-x_0)**2)/(4*v_0**2)) # Création de la cloche Gaussienne
    phase = np.exp(1j*k_0*x) # Le terme de phase permet le déplacement de x
    A = (1/(2*np.pi*v_0**2))**(1/4) # Constante pour que l'aire sous la courbe soit de 1
    psi = A *gaussian *phase # L'état complet de l'action
    return psi

def build_hamiltonian(N,dx,mass,x,resistance_price,V_0,L_point):
    #Création de la matrice pour la dérivé seconde par différence finie (Matrice de transformation)
    main_diag = -2*np.ones(N)
    off_diag = np.ones(N-1)
    M_T = (np.diag(main_diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k = -1))
    K = -1/(2*mass*dx**2) * M_T # Calcul de l'énergie cinétique

    #Création de la matrice de potentiel
    potential_vector = np.zeros(N)
    x_res = np.log(resistance_price) # Trouve l'emplacement de la barrière
    idx = (np.abs(x-x_res)).argmin() # Index de la barrière
    potential_vector[idx: idx+L_point] = V_0 # Création de la barrière
    V = np.diag(potential_vector) # Matrice de potentiel

    H = K + V #Création du Hamiltonien
    return H, potential_vector

def evolve_wave_packet(psi,H,dt,S):
    N = H.shape[0]
    # Crank-Nicolson
    M_L = np.eye(N) + (1j*dt/2)*H # Création de la matrice de gauche
    M_R = np.eye(N) - (1j*dt/2)*H # Création de la matrice de droite
    # Transformation de la matrice
    diag_main = np.diag(M_L)
    diag_up = np.diag(M_L, k=1)
    diag_down = np.diag(M_L, k=-1)
    M_L_banded = np.zeros((3, len(psi)), dtype = complex)
    M_L_banded[0, 1:] = diag_up
    M_L_banded[1,:] = diag_main
    M_L_banded[2,:-1] = diag_down
    for i in range(S): # Boucle qui modifie la fonction d'onde (psi)
        B = M_R.dot(psi) # Valeur intermédiaire
        psi = solve_banded((1,1),M_L_banded,B) # Nouvelle valeur de psi
    return psi

def plot_results(x,psi_final,potential_vector):
    prob = np.abs(psi_final)**2 # Probabilité

    # Création du graphique
    plt.figure(figsize=(10,6))
    plt.plot(x,prob,label = "Probabilité du prix (Action)",color = "blue", alpha = 0.2)
    plt.fill_between(x,prob,color="Blue",alpha= 0.2)
    V_plot = potential_vector/(np.max(potential_vector) if np.max(potential_vector)>0 else 1)
    plt.plot(x,V_plot*np.max(prob), label="Densité de Probabilité", color = "red")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()

if __name__ == "__main__":
    time_step = 0.01 # Pas de temps de la simulation
    num_iterations = 1000 # Nb d'itération de la simulation
    initial_price = 500 # Prix de départ
    initial_volatility = 0.1  # volatilité
    initial_drift = 10  # momentum du marché (drift)
    num_points = 1000  # Nombre de point dans la grille
    barrier_thickness = 10 # Épaisseur de la barrière de potentiel
    potential_strength = 500 # Valeur de la barrière de potentiel
    resistance_price_val = 550 # Prix de la barrière de potentiel


    #1. Initialisation
    x_0, x, dx, mass = initialize_parameters(initial_price, initial_volatility, num_points)

    #2. Création de la fonction d'ondes initial
    psi_initial = create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    #3. Construction du Hamiltonien
    H, potential_vector = build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength, barrier_thickness)

    #4. Évolution de la fonction d'ondes
    psi_final = evolve_wave_packet(psi_initial, H, time_step, num_iterations)

    #5. Affichage des résultats
    plot_results(x,psi_final, potential_vector)