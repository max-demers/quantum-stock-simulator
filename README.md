*Read this in other languages: [Français](README.fr.md)*

# Quantum Stock Simulator

This project offers an original and visual approach to modeling the evolution of financial asset prices using mathematical processes from quantum mechanics. The asset's price (stock, gold, etc.) is represented as a probability wave packet that evolves over time against "potential barriers" representing stock market support and resistance levels.

##  Key Features

- **Dynamic Initialization**: Models historical asset returns via the `yfinance` API to extract volatility (dispersion) and drift (directional trend).
- **Quantum Process (Schrödinger Equation)**: Implementation of the Hamiltonian with kinetic energy (based on volatility) and creation of potential wells and barriers.
- **Spatio-Temporal Numerical Resolution**: Uses implicit differential modeling (Crank-Nicolson method) for stable system evolution.
- **Interactive & Static Visualizations**: Real-time animations of probability density crashing against resistances and comparative charts highlighting accumulation effects and probabilistic quantum tunneling.

##  Project Architecture

The project is built around a mathematical core and three distinct entry scripts that utilize it:

1. `quantum_engine.py`: **The Core Quantum Engine**
   This is the library containing fundamental functions: mathematical methods (Crank-Nicolson), Hamiltonian matrix creation, wave packet generation, and animation rendering interface. The scripts below use it as a foundation.
2. `main.py`: **Standard Interactive Simulator**
   The basic entry point (configured for `SPY`). It calls the engine to animate the evolution of probability densities in real-time and detect breakouts.
3. `Comparaison.py`: **Resistance Barrier Impact Study**
   This script runs the simulation in two parallel universes: a smooth probabilistic model with and without market barriers. It generates a comparative visual illustrating the "bounce" creation and "tunneling effect" calculation.
4. `Gold.py`: **Retrospective Backtest on Gold (`GC=F`)**
   Splits historical data (2020-2023) to test the probabalistic projection (2023). The script runs the engine on Gold and overlays the *actual historical price* on the animation to evaluate the Hamiltonian's predictive capability.

##  Prerequisites and Installation

Ensure you have Python 3.8+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```
*(Manual alternative): `pip install numpy matplotlib yfinance scipy`*


##  Usage

### Run the base simulation (Continuous Animation)
```bash
python main.py
```

### Run the barrier effect demonstration (Comparative Chart)
```bash
python Comparaison.py
```

### Run the Gold backtest with historical prices
```bash
python Gold.py
```

### Parameter Configuration
In each execution script (under the standard `if __name__ == "__main__":` block), several algorithmic constants can be tuned:
- `action`: The Yahoo Finance ticker symbol studied (e.g., "SPY", "GC=F", "AAPL").
- `resistance_price_val`: Array of symbolic price levels acting as friction points.
- `barrier_thickness`: The proportion of the probabilistic space taken up by the resistance.
- `potential_strength`: A mass coefficient simulating a shield or complex bounce for the Hamiltonian.


## ⚠️ Disclaimer

This theoretical and mathematical engineering model is for educational and research purposes only. **It provides no guarantees, should not be relied upon for certain forecasts, and does not constitute financial advice or investment recommendations.**
