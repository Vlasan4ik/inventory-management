import streamlit as st
import pandas as pd
import numpy as np

# --- Заголовок ---
st.title("📦 Модель управління запасами")

# --- Ввідні параметри ---
st.sidebar.header("Параметри моделі")
reorder_point = st.sidebar.number_input("Точка замовлення", min_value=0, value=20)
order_quantity = st.sidebar.number_input("Кількість для замовлення", min_value=1, value=50)
lead_time = st.sidebar.number_input("Час постачання (дні)", min_value=0, value=2)
daily_demand = st.sidebar.number_input("Середній щоденний попит", min_value=0.0, value=10.0)
demand_std = st.sidebar.number_input("Стандартне відхилення попиту", min_value=0.0, value=2.0)

# --- Ініціалізація стану ---
if "stock_level" not in st.session_state:
    st.session_state.stock_level = 100
if "orders" not in st.session_state:
    st.session_state.orders = []
if "inventory_history" not in st.session_state:
    st.session_state.inventory_history = []
if "stockouts" not in st.session_state:
    st.session_state.stockouts = 0
if "days_to_stockout" not in st.session_state:
    st.session_state.days_to_stockout = "-"
if "day" not in st.session_state:
    st.session_state.day = 0

# --- Симуляція одного дня ---
if st.button("Симулювати наступний день"):
    st.session_state.day += 1
    st.write(f"День симуляції: {st.session_state.day}")

    consumption = max(0, np.random.normal(daily_demand, demand_std))
    st.write(f"Споживання за день: {consumption:.2f}")

    st.session_state.stock_level -= consumption

    # Запис історії запасів
    st.session_state.inventory_history.append(st.session_state.stock_level)

    # Дефіцит
    if st.session_state.stock_level <= 0:
        st.session_state.stockouts += 1
        st.session_state.days_to_stockout = 0
        st.write("Виник дефіцит запасів!")
    else:
        if isinstance(st.session_state.days_to_stockout, int):
            st.session_state.days_to_stockout += 1
        else:
            st.session_state.days_to_stockout = 1

    # Замовлення, якщо запас нижче точки замовлення
    if st.session_state.stock_level <= reorder_point:
        st.session_state.orders.append({
            "дата": pd.Timestamp.now(),
            "кількість": order_quantity
        })
        st.session_state.stock_level += order_quantity
        st.write(f"Зроблено замовлення: {order_quantity} од.")

# --- Вивід поточного рівня запасів ---
st.subheader("📊 Поточний рівень запасів:")
st.metric("Запаси", f"{st.session_state.stock_level:.0f} од.")

# --- Історія замовлень ---
st.subheader("📝 Історія замовлень:")
if st.session_state.orders:
    st.dataframe(pd.DataFrame(st.session_state.orders))
else:
    st.info("Замовлень ще не було.")

# --- Аналітичні метрики ---
current_inventory = round(st.session_state.stock_level, 2)
inventory_history = st.session_state.inventory_history
stockouts = st.session_state.stockouts
days_simulated = len(inventory_history)
days_to_stockout = st.session_state.days_to_stockout

avg_inventory = round(sum(inventory_history) / len(inventory_history), 2) if inventory_history else "-"
stockout_rate = round((stockouts / days_simulated) * 100, 2) if days_simulated > 0 else "-"

# --- Вивід метрик ---
st.subheader("📈 Ключові показники:")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Поточний рівень запасів", current_inventory)
col2.metric("Середній рівень запасів", avg_inventory)
col3.metric("Частота дефіциту (%)", stockout_rate)
col4.metric("Днів до дефіциту", days_to_stockout)
