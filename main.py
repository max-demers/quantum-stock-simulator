import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.linalg import solve_banded
from datetime import datetime, timedelta


def initialize_parameters(N, action, resistance_prices=None):
    ticker = yf.Ticker(action)
    # On télécharge un historique plus large pour faire du backtesting
    # 20 jours au total : 14 pour calibrer, 6 pour tester
    df = yf.download(action, period="20d", interval="1h")
    
    # Séparation : on garde les 100 derniers points pour le test (environ 4-5 jours de bourse)
    test_size = 100
    df_train = df.iloc[:-test_size]
    df_test = df.iloc[-test_size:]
    
    prices_train = df_train['Close'].values.flatten()
    initial_price = prices_train[-1] # Le prix à l'instant T=0 de la simulation
    
    log_return = np.diff(np.log(prices_train))
    v_0 = np.std(log_return)
    k_0 = np.mean(log_return)
    
    x_0 = np.log(initial_price)
    x_min = x_0 - 0.15
    x_max = x_0 + 0.15
    
    if resistance_prices:
        max_res = np.log(max(resistance_prices) * 1.05)
        min_res = np.log(min(resistance_prices) * 0.95)
        x_min = min(x_min, min_res)
        x_max = max(x_max, max_res)

    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]
    mass = 1 / v_0 ** 2
    
    # On retourne aussi les prix réels futurs pour la comparaison
    real_prices_future = df_test['Close'].values.flatten()
    real_times_future = df_test.index
    
    return x_0, x, dx, mass, k_0, v_0, initial_price, real_prices_future, real_times_future


def create_initial_wave_packet(x, x_0, v_0, k_0):
    gaussian = np.exp(-((x - x_0) ** 2) / (4 * v_0 ** 2))
    phase = np.exp(1j * k_0 * x)
    A = (1 / (2 * np.pi * v_0 ** 2)) ** (1 / 4)
    psi = A * gaussian * phase
    return psi


def build_hamiltonian(N, dx, mass, x, resistance_price, V_0, barrier_thickness):
    K_coeff = -1 / (2 * mass * dx ** 2)
    potential_vector = np.zeros(N)
    for price, thick, strength in zip(resistance_price, barrier_thickness, V_0):
        log_start = np.log(price)
        log_end = np.log(price + thick)

        idx_1 = (np.abs(x - log_start)).argmin()
        idx_2 = (np.abs(x - log_end)).argmin()

        idx_start = min(idx_1, idx_2)
        idx_end = max(idx_1, idx_2)
        L_point = max(1, idx_end - idx_start)

        if isinstance(strength, (list, tuple)) and len(strength) == 2:
            v_at_price, v_at_thick = strength
            vals = np.linspace(v_at_price, v_at_thick, L_point) if idx_1 <= idx_2 else np.linspace(v_at_thick, v_at_price, L_point)
            potential_vector[idx_start: idx_start + L_point] = vals
        else:
            potential_vector[idx_start: idx_start + L_point] = strength
    return K_coeff, potential_vector


def run_simulation_and_animate(psi, K_coeff, dt, S, x, potential_vector, steps_per_frame=10,
                               resistance_price=None, barrier_thickness=None,
                               v0=0, k0=0, real_prices=None, real_times=None):
    alpha = 1j * dt / 2
    H_diag = - potential_vector + K_coeff * (-2)
    diag_main_ML = 1 + alpha * H_diag
    diag_off_ML = alpha * K_coeff
    M_L_banded = np.zeros((3, len(psi)), dtype=complex)
    M_L_banded[0, 1:] = diag_off_ML
    M_L_banded[1, :] = diag_main_ML
    M_L_banded[2, :-1] = diag_off_ML

    breakout_indices = []
    dx = x[1] - x[0]
    if resistance_price is not None and barrier_thickness is not None:
        for p, t in zip(resistance_price, barrier_thickness):
            log_end = np.log(p + t)
            idx = (np.abs(x - log_end)).argmin()
            breakout_indices.append(idx)

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))

    prob_initial = np.abs(psi) ** 2
    prob_line, = ax.plot(x, prob_initial, label="Probabilité du prix (Modèle)", color="blue", lw=2)
    fill_collection = ax.fill_between(x, prob_initial, color="blue", alpha=0.3)
    # Ligne pour le PRIX RÉEL
    real_price_line = ax.axvline(x=np.nan, color="black", linestyle="-", lw=3, label="Prix Réel (Marché)")
    V_abs = np.abs(potential_vector)
    V_log = np.log1p(V_abs)
    V_norm = (V_log / np.max(V_log) if np.max(V_log) > 0 else 1)
    V_plot = V_norm * np.sign(potential_vector)
    potential_line, = ax.plot(x, V_plot * np.max(prob_initial), label="Obstacles (Résistances)",
                              color="red", linestyle="--", alpha=0.4)

    prob_labels = [ax.text(x[idx], 0, "", color="darkred", fontweight="bold", ha="center", fontsize=9)
                   for idx in breakout_indices]

    # Panel de statistiques
    stats_text = ax.text(0.02, 0.97, "", transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    start_time = real_times[0] if real_times is not None else datetime.now()
    timer_text = ax.text(0.5, 0.96, "", transform=ax.transAxes, fontsize=12,
                         verticalalignment='top', horizontalalignment='center',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                         fontweight='bold', color='darkblue')

    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{np.exp(val):.1f}$"))
    ax.set_xlabel("Prix ($)")
    ax.set_ylabel("Densité de Probabilité")
    ax.set_title(f"Validation du Modèle Quantique vs Réalité")
    ax.legend(loc='upper right')
    ax.grid(alpha=0.2)

    valid_points = 0
    total_points = 0

    for i in range(S):
        term_H_psi = H_diag * psi
        term_H_psi[1:] += K_coeff * psi[:-1]
        term_H_psi[:-1] += K_coeff * psi[1:]
        B = psi - alpha * term_H_psi
        psi = solve_banded((1, 1), M_L_banded, B)

        if i % steps_per_frame == 0:
            # On synchronise le temps de la simulation avec l'index des prix réels
            # On simule par pas de dt (0.01h), donc i*dt nous donne l'heure écoulée
            real_idx = int(i * dt) 
            if real_prices is not None and real_idx < len(real_prices):
                current_real_price = float(real_prices[real_idx])
                log_real_price = np.log(current_real_price)
                real_price_line.set_xdata([log_real_price])
                # Calcul de la précision (Est-ce que le prix réel est sous la cloche ?)
                prob = np.abs(psi) ** 2
                price_idx = (np.abs(x - log_real_price)).argmin()
                
                # Calcul de l'espérance (Prix prédit moyen)
                expected_log_price = float(np.sum(x * prob) * dx)
                expected_price = float(np.exp(expected_log_price))
                
                # Z-Score simplifié : distance entre réel et espérance en unités de volatilité
                z_score = float(np.abs(log_real_price - expected_log_price) / v0)
                
                if z_score < 2: # Dans l'intervalle de confiance de 95%
                    valid_points += 1
                total_points += 1
                
                stats_text.set_text(f"--- VALIDATION ---\n"
                                    f"Drift: {k0:.2%}\n"
                                    f"Volatilité: {v0:.2%}\n"
                                    f"Prix Prédit (moy): {expected_price:.2f}$\n"
                                    f"Prix Réel: {current_real_price:.2f}$\n"
                                    f"Z-Score: {z_score:.2f}\n"
                                    f"Fiabilité Modèle: {(valid_points/total_points):.1%}")

            timer_text.set_text(f"Temps : {(start_time + timedelta(hours=i*dt)).strftime('%Y-%m-%d %H:%M')}")
            
            prob = np.abs(psi) ** 2
            prob_line.set_ydata(prob)
            fill_collection.remove()
            fill_collection = ax.fill_between(x, prob, color="blue", alpha=0.3)

            new_ylim_top = max(0.5, np.max(prob) * 1.3)
            ax.set_ylim(-0.02, new_ylim_top)
            potential_line.set_ydata(V_plot * new_ylim_top * 0.7)

            for j, idx in enumerate(breakout_indices):
                p_breakout = np.sum(prob[idx:]) * dx
                if p_breakout > 0.5: p_breakout = np.sum(prob[:idx])* dx
                prob_labels[j].set_text(f"Breakout:\n{p_breakout:.1%}")
                prob_labels[j].set_position((x[idx], new_ylim_top * 0.8))

            plt.draw()
            plt.pause(0.001)

    plt.ioff()
    plt.show()
    return psi


if __name__ == "__main__":
    time_step = 0.05 # On augmente un peu le pas pour que l'animation soit fluide
    num_iterations = 2000 # Correspond à environ 100h de trading
    update_frequency = 5
    num_points = 50000
    
    # Paramètres de test (SPY)
    barrier_thickness = [5,8,4,5]
    potential_strength = [150,(1,12),100,150]
    resistance_price_val = [600,643,690,715] # Ajustez selon le prix actuel du SPY
    action = "SPY"

    # 1. Initialisation avec split Train/Test
    params = initialize_parameters(num_points, action, resistance_price_val)
    x_0, x, dx, mass, initial_drift, initial_volatility, initial_price, real_prices, real_times = params

    # 2. Création de la fonction d'ondes
    psi_initial = create_initial_wave_packet(x, x_0, initial_volatility, initial_drift)

    # 3. Hamiltonien
    K_coeff, potential_vector = build_hamiltonian(num_points, dx, mass, x, resistance_price_val, potential_strength,
                                                  barrier_thickness)

    # 4. Simulation avec PRIX RÉEL
    psi_final = run_simulation_and_animate(psi_initial, K_coeff, time_step, num_iterations, x, potential_vector,
                                           update_frequency, resistance_price_val, barrier_thickness,
                                           initial_volatility, initial_drift, real_prices, real_times)
