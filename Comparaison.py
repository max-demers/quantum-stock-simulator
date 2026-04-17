import numpy as np
import matplotlib.pyplot as plt
import quantum_engine as qe

def plot_barrier_impact(psi_no_barrier, x_no_barrier, psi_with_barrier, x_with_barrier, resistance_prices):
    """ Génère un beau graphique comparatif de l'impact de la barrière """
    plt.figure(figsize=(12, 7))  # On crée une figure
    prices_no = np.exp(x_no_barrier)  # On calcule les prix
    prices_yes = np.exp(x_with_barrier)

    prob_no = np.abs(psi_no_barrier) ** 2  # On calcule la probabilité
    prob_yes = np.abs(psi_with_barrier) ** 2  # On calcule la probabilité

    # Trouver les limites raisonnables pour l'axe X (basé sur le modèle avec barrière pour un bon rendu visuel)
    threshold = np.max(prob_yes) * 0.01  # On calcule le seuil
    active_indices = np.where(prob_yes > threshold)[0]  # On trouve les indices actifs
    if len(active_indices) > 0:  # Si on a des indices actifs
        xlim_min, xlim_max = prices_yes[active_indices[0]], prices_yes[
            active_indices[-1]]  # On définit les limites de l'axe X
    else:
        xlim_min, xlim_max = np.min(prices_yes), np.max(prices_yes)  # On définit les limites de l'axe X

    # Courbe classique (Sans barrière)
    plt.plot(prices_no, prob_no, label="Modèle Standard (Sans Barrière)", color="gray", linestyle="--", lw=2)
    plt.fill_between(prices_no, prob_no, color="gray", alpha=0.1)

    # Courbe quantique (Avec barrière)
    plt.plot(prices_yes, prob_yes, label="Modèle Quantique Actuel (Avec Barrière)", color="royalblue", lw=3)
    plt.fill_between(prices_yes, prob_yes, color="royalblue", alpha=0.3)

    # Affichage de la barrière de résistance
    for res in resistance_prices:
        plt.axvline(x=res, color="red", linestyle="-", linewidth=2.5, label=f"Résistance ({res:.2f}$)")
        plt.axvspan(res, res * 1.005, color='red', alpha=0.15)  # Zone de la barrière

    plt.title("Impact d'une Résistance Boursière sur les Probabilités", fontsize=14, fontweight='bold')
    plt.xlabel("Prix de l'Action ($)", fontsize=12)
    plt.ylabel("Densité de Probabilité (Où le prix a le plus de chances d'être)", fontsize=12)
    plt.xlim(xlim_min * 0.98, xlim_max * 1.02)  # On définit les limites de l'axe X
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)

    # Ajout d'annotations explicatives
    plt.annotate('Accumulation (Rebond)',
                 xy=(resistance_prices[2] * 0.99, np.max(prob_yes) * 0.8),
                 xytext=(resistance_prices[2] * 0.95, np.max(prob_yes) * 0.9),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                 fontsize=10, fontweight='bold', color='darkblue')

    plt.annotate('Effet Tunnel\n(Pénétration faible)',
                 xy=(resistance_prices[2] * 1.01, np.max(prob_no) * 0.2),
                 xytext=(resistance_prices[2] * 1.03, np.max(prob_no) * 0.4),
                 arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=8),
                 fontsize=10, fontweight='bold', color='darkred')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Modifions les paramètres pour que ça tourne en un temps raisonnable
    time_step = 0.01
    num_iterations = 50000
    update_frequency = 100
    num_points = 50000

    # Paramètres de test (SPY)
    action = "SPY"
    # On initialise d'abord sans résistances pour obtenir le initial_price
    params = qe.initialize_parameters(num_points, action)
    x_0, x, dx, mass, initial_drift, initial_volatility, initial_price, real_prices, real_times = params

    # Création d'une grille PLUS LARGE pour la simulation sans barrière (éviter la réflexion aux limites)
    # On la fait 4 fois plus large que la grille standard, avec le même nombre de points.
    x_min_wide = x_0 - 5.0
    x_max_wide = x_0 + 5.0
    x_wide = np.linspace(x_min_wide, x_max_wide, num_points)
    dx_wide = x_wide[1] - x_wide[0]

    # Définition d'une résistance pour illustrer votre valeur ajoutée
    resistance_price_val = [600, 640, 690, 720]
    barrier_thickness = [6, 3, 2.5, 3]
    potential_strength = [29, 18, 38, 20]

    # 2. Création des fonctions d'ondes initiales
    psi_initial = qe.create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)
    psi_initial_wide = qe.create_initial_wave_packet(x_wide, x_0, initial_volatility, initial_drift)

    # 3. Hamiltonien AVEC barrière (sur la grille standard)
    K_coeff, potential_vector_barrier = qe.build_hamiltonian(num_points, dx, mass, x, resistance_price_val,
                                                          potential_strength, barrier_thickness)

    # 4. Hamiltonien SANS barrière (sur la grille large)
    K_coeff_wide, potential_vector_no_barrier = qe.build_hamiltonian(num_points, dx_wide, mass, x_wide, [], [], [])

    print("Calcul du modèle classique avec la simulation rapide...")
    # Simulation rapide SANS barrière
    psi_final_no_barrier = qe.fast_simulation(psi_initial_wide.copy(), K_coeff_wide, time_step, num_iterations,
                                           potential_vector_no_barrier)

    print("Lancement de l'animation quantique avec barrière...")
    # Simulation animée AVEC barrière
    psi_final_with_barrier = qe.run_simulation_and_animate(psi_initial.copy(), K_coeff, time_step, num_iterations, x,
                                                        potential_vector_barrier,
                                                        update_frequency, resistance_price_val, barrier_thickness,
                                                        initial_volatility, initial_drift, real_prices, real_times)

    # 5. Affichage du graphique comparatif final
    plot_barrier_impact(psi_final_no_barrier, x_wide, psi_final_with_barrier, x, resistance_price_val)