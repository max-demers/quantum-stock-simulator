import numpy as np
import yfinance as yf
import quantum_engine as qe


def initialize_parameters(N, action, resistance_prices=None):
    """ Initialise les paramètres de la simulation et télécharge les données boursières via yfinance """
    
    # Période d'entraînement pour calculer le drift (k_0) et la volatilité (v_0) avant la simulation
    train_start = "2020-01-01"
    train_end = "2023-02-20"
    df_train = yf.download(action, start=train_start, end=train_end)

    # Période de test (la période que l'on veut simuler et visualiser)
    start_date = "2023-02-20"
    end_date = "2023-11-06"
    df_test = yf.download(action, start=start_date, end=end_date)

    if df_train.empty or df_test.empty:
        raise ValueError("Les données n'ont pas pu être téléchargées. Vérifiez le ticker ou votre connexion.")

    prices_train = df_train['Close'].values.flatten()
    real_prices_future = df_test['Close'].values.flatten()
    real_times_future = df_test.index
    
    # Le prix à l'instant T=0 de la simulation correspond au premier jour de la période Test
    initial_price = real_prices_future[0] 

    log_return = np.diff(np.log(prices_train))
    v_0 = np.std(log_return)
    mu = np.mean(log_return)

    x_0 = np.log(initial_price)
    x_min = x_0 - 0.4 # On élargit un peu l'espace des prix pour couvrir toute la période
    x_max = x_0 + 0.4

    if resistance_prices:
        max_res = np.log(max(resistance_prices) * 1.05)
        min_res = np.log(min(resistance_prices) * 0.95)
        x_min = min(x_min, min_res)
        x_max = max(x_max, max_res)

    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]
    mass = 1 / v_0 ** 2
    k_0 = mu - 1/(2*mass)
    k_0 = 5
    return x_0, x, dx, mass, k_0, v_0, initial_price, real_prices_future, real_times_future


if __name__ == "__main__":
    time_step = 0.01 # Unité de temps (1.0 = 1 jour de trading)
    num_iterations = 18500 # Correspond à environ 185 jours de trading (couvre la période)
    update_frequency = 100 # On met à jour le graphique tous les 100 pas (donc tous les 1 jour)
    num_points = 50000 # On augmente le nombre de points pour une meilleure précision

    # Paramètres de test (Or)
    barrier_thickness = [25,80] # Épaisseur de la barrière
    potential_strength = [400,600] # Force de la barrière
    resistance_price_val = [1730,2020] # Prix de la résistance adaptés à l'Or
    action = "GC=F" # Action à tester

    # 1. Initialisation avec split Train/Test
    params = initialize_parameters(num_points, action, resistance_price_val)
    x_0, x, dx, mass, initial_drift, initial_volatility, initial_price, real_prices, real_times = params

    # 2. Création de la fonction d'ondes
    psi_initial = qe.create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Hamiltonien
    K_coeff, potential_vector = qe.build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength,
                                                  barrier_thickness)

    # 4. Simulation avec PRIX RÉEL
    psi_final = qe.run_simulation_and_animate(psi_initial, K_coeff, time_step, num_iterations, x, potential_vector,
                                           update_frequency, resistance_price_val, barrier_thickness,
                                           initial_volatility, initial_drift, real_prices, real_times)