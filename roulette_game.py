import streamlit as st
import pandas as pd
import numpy as np
import random
from PIL import Image
import os

def spin_wheel():
    winning_number = random.randint(0, 36)
    # Define red and black numbers 
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    if winning_number == 0:
        winning_color = "green"
    elif winning_number in red_numbers:
        winning_color = "red"
    else:
        winning_color = "black"
    return winning_number, winning_color

def check_bet(bet_type, bet_choice, winning_number, winning_color, bet_amount):
    # For colour bet
    if bet_type == 1:
        if bet_choice.lower() == winning_color:
            payout = 2 * bet_amount
            return f"You won! {winning_number} ({winning_color}) - Payout: £{payout}", bet_amount
        else:
            return f"You lost. Winning number: {winning_number} ({winning_color}).", -bet_amount
    # For number bet
    elif bet_type == 2:
        try:
            if int(bet_choice) == winning_number:
                payout = 36 * bet_amount
                return f"Jackpot! {winning_number} - Payout: £{payout}", bet_amount * 35
            else:
                return f"You lost. Winning number: {winning_number} ({winning_color}).", -bet_amount
        except ValueError:
            return "Invalid number entered.", 0
    # For range bet 
    elif bet_type == 3:
        ranges = {"1-12": range(1, 13), "13-24": range(13, 25), "25-36": range(25, 37)}
        if bet_choice in ranges and winning_number in ranges[bet_choice]:
            payout = 3 * bet_amount
            return f"You won! {winning_number} is in {bet_choice} - Payout: £{payout}", bet_amount * 2
        else:
            return f"You lost. Winning number: {winning_number} ({winning_color}).", -bet_amount
    # For even/odd bet
    elif bet_type == 4:
        if winning_number == 0:
            return f"You lost. Winning number: {winning_number} is neither even nor odd.", -bet_amount
        elif bet_choice.lower() == "even" and winning_number % 2 == 0:
            payout = 2 * bet_amount
            return f"You won! {winning_number} is even - Payout: £{payout}", bet_amount
        elif bet_choice.lower() == "odd" and winning_number % 2 == 1:
            payout = 2 * bet_amount
            return f"You won! {winning_number} is odd - Payout: £{payout}", bet_amount
        else:
            return f"You lost. Winning number: {winning_number} ({winning_color}).", -bet_amount
    else:
        return "Invalid bet type.", 0


if 'balance' not in st.session_state:
    st.session_state.balance = 0

if 'history' not in st.session_state:
    st.session_state.history = []  # To store (winning_number, color) tuples

if 'game_stage' not in st.session_state:
    st.session_state.game_stage = 'deposit'  # stages: deposit, bet, result

if 'bet_type' not in st.session_state:
    st.session_state.bet_type = None

if 'bet_amount' not in st.session_state:
    st.session_state.bet_amount = 0

if 'bet_choice' not in st.session_state:
    st.session_state.bet_choice = None

if 'result' not in st.session_state:            
    st.session_state.result = None 

st.title("Roulette")
st.write("Welcome to the Roulette Game! Place your deposit and bet on your favorite outcome.")

try:
    img_path = os.path.join(os.path.dirname(__file__), "roulette_wheel_image.png")
    roulette_img = Image.open(img_path)
    st.image(roulette_img, caption="Roulette Wheel", width=300)
    cols = st.columns(3)
    cols[1].image("roulette_wheel.png", width=300)
except Exception as e:
    print("")

if st.session_state.game_stage == 'deposit':
    st.subheader("Deposit Money")
    deposit = st.number_input("Enter deposit amount (£):", min_value=1, step=1)
    if st.button("Deposit", key="deposit_btn"):
        st.session_state.balance = deposit
        st.session_state.game_stage = 'bet'
        st.success(f"Deposit successful! Your balance is now £{st.session_state.balance}.")


if st.session_state.game_stage == 'bet':
    st.subheader("Place Your Bet")
    st.write(f"Current Balance: £{st.session_state.balance}")
    
    st.session_state.bet_type = st.selectbox("Select Bet Type", 
        options=["Select", "Colour", "Number", "Range", "Even/Odd"], index=0)
    
    if st.session_state.bet_type != "Select":
        st.session_state.bet_amount = st.number_input("Enter bet amount (£):", min_value=1, max_value=st.session_state.balance, step=1)
        if st.session_state.bet_type == "Colour":
            st.session_state.bet_choice = st.radio("Choose a colour", options=["Red", "Black", "Green"])
        elif st.session_state.bet_type == "Number":
            st.session_state.bet_choice = st.text_input("Enter a number (0-36):")
        elif st.session_state.bet_type == "Range":
            st.session_state.bet_choice = st.selectbox("Choose a range", options=["1-12", "13-24", "25-36"])
        elif st.session_state.bet_type == "Even/Odd":
            st.session_state.bet_choice = st.radio("Choose Even or Odd", options=["Even", "Odd"])
        
        if st.button("Confirm Bet", key="confirm_bet_btn"):
            # Ensure bet amount is valid
            if st.session_state.bet_amount > 0 and st.session_state.bet_amount <= st.session_state.balance:
                st.session_state.game_stage = 'result'
                st.session_state.result = None
            else:
                st.error("Invalid bet amount.")


if st.session_state.game_stage == 'result':
    st.subheader("Spinning the Wheel...")
    spinner = st.empty()
    spinner.info("Spinning...")

    if st.session_state.result is None:         
        winning_number, winning_color = spin_wheel()
        result_message, delta = check_bet(
            bet_type={"Colour": 1, "Number": 2, "Range": 3, "Even/Odd": 4}[st.session_state.bet_type],
            bet_choice=st.session_state.bet_choice,
            winning_number=winning_number,
            winning_color=winning_color,
            bet_amount=st.session_state.bet_amount
        )
        st.session_state.result = (result_message, delta, winning_number, winning_color)
    else:
        result_message, delta, winning_number, winning_color = st.session_state.result  
    
    spinner.empty()  
    st.write(result_message)
    st.session_state.balance += delta
    st.write(f"New Balance: £{st.session_state.balance}")
    
    if st.session_state.balance > 0:
        if st.button("Spin Again"):
            st.session_state.game_stage = 'bet'
            st.session_state.result = None
    else:
        st.warning("No funds remaining. Please deposit money to continue playing.")

if st.button("Restart Game", key="restart_game_btn"):
    st.session_state.balance = 0
    st.session_state.history = []
    st.session_state.game_stage = 'deposit'
    st.session_state.result = None
    st.success("Game restarted. Please deposit money.")


#URL :"https://roulettegame.streamlit.app/"