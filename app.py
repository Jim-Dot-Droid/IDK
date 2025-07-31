
import streamlit as st
import pandas as pd
import numpy as np
import os

# File paths
HISTORY_FILE = "history.csv"
RESULTS_FILE = "results.csv"
INITIAL_BALANCE = 0.1
BET_AMOUNT = 0.01

# Load previous game results
def load_results():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    return pd.DataFrame(columns=["prediction", "actual", "correct"])

# Save new game result
def save_result(prediction, actual, correct):
    df = load_results()
    df.loc[len(df)] = [prediction, actual, correct]
    df.to_csv(RESULTS_FILE, index=False)

# Calculate running SOL balances
def get_balance_series(df):
    balance = INITIAL_BALANCE
    series = []
    for _, row in df.iterrows():
        if row["prediction"] == "Above":
            if row["correct"]:
                balance += BET_AMOUNT
            else:
                balance -= BET_AMOUNT
        series.append(balance)
    return series

def get_martingale_series(df):
    balance = INITIAL_BALANCE
    series = []
    streak = 0
    for _, row in df.iterrows():
        if row["prediction"] == "Above":
            bet = BET_AMOUNT * (2 ** streak)
            if row["correct"]:
                balance += bet
                streak = 0
            else:
                balance -= bet
                streak += 1
        series.append(balance)
    return series

def normalize_input(value):
    return value / 100 if value > 10 else value

# Main app
def main():
    st.title("Crash Predictor — SOL Balance Tracker")

    df = load_results()

    st.subheader("Add a Multiplier")
    new_val = st.text_input("Enter multiplier (e.g. 1.87 or 187 for %):")
    if st.button("Add"):
        try:
            val = normalize_input(float(new_val))
            # Simplified prediction
            prediction = "Above" if np.random.rand() > 0.5 else "Under"
            correct = (prediction == "Above" and val > 2.0) or (prediction == "Under" and val <= 2.0)
            save_result(prediction, val, correct)
            st.success(f"Prediction was {prediction}, actual {val:.2f} → {'Correct' if correct else 'Wrong'}")
            df = load_results()
        except:
            st.error("Invalid number entered.")

    st.subheader("Balance Over Time")
    if not df.empty:
        df["Flat Balance"] = get_balance_series(df)
        df["Martingale Balance"] = get_martingale_series(df)
        st.line_chart(df[["Flat Balance", "Martingale Balance"]])

        st.metric("Final Flat Balance", f"{df['Flat Balance'].iloc[-1]:.4f} SOL")
        st.metric("Final Martingale Balance", f"{df['Martingale Balance'].iloc[-1]:.4f} SOL")
    else:
        st.info("No data yet. Add a multiplier to get started.")

    if st.button("Reset All Data"):
        if os.path.exists(RESULTS_FILE):
            os.remove(RESULTS_FILE)
        st.success("Data reset.")

if __name__ == "__main__":
    main()
