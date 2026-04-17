import quantum_engine as qe

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


    # Définition d'une résistance pour illustrer votre valeur ajoutée
    resistance_price_val = [600,640,690,720]
    barrier_thickness = [6,3,2.5,3]
    potential_strength = [29,18,38,20]

    # 2. Création des fonctions d'ondes initiales
    psi_initial = qe.create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Hamiltonien AVEC barrière (sur la grille standard)
    K_coeff, potential_vector_barrier = qe.build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength, barrier_thickness)

    print("Lancement de l'animation quantique avec barrière...")
    # Simulation animée AVEC barrière
    psi_final_with_barrier = qe.run_simulation_and_animate(psi_initial.copy(), K_coeff, time_step, num_iterations, x, potential_vector_barrier,
                                           update_frequency, resistance_price_val, barrier_thickness,
                                           initial_volatility, initial_drift, real_prices, real_times)
