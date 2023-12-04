import streamlit as st
import pandas as pd

# Displaying the forecast
st.title('Goodlawyer 2024 Forecast')

with st.sidebar.expander("Fractional Inputs"):
    starting_accounts = st.number_input('Starting Active Accounts', min_value=0, value=65)
    new_accounts = st.number_input('New Accounts Per Month', value=11)
    deal_size = st.number_input('Average Deal Size', value=5000, step=500)
    take_rate = st.number_input('Fractional Take Rate %', min_value=0, max_value=100, value=20, step=1)
    account_churn = st.number_input('Account Churn (%)', min_value=0, max_value=100, value=3, step=1)

with st.sidebar.expander("Marketplace Inputs"):
    monthly_gmv = st.number_input('Monthly GMV', value=250000, step=50000)
    marketplace_take_rate = st.number_input('Take Rate %', min_value=0, max_value=100, value=18, step=1)
    growth_rate = st.number_input('Growth %', value=-1)

with st.sidebar.expander("Financial Inputs"):
    starting_cash_balance = st.number_input('Starting Cash Balance', value=1400000, step=100000)
    starting_monthly_expenses = st.number_input('Starting Monthly Expenses', value=150000, step=10000)
    quarterly_increase = st.number_input('Quarterly Increase', value=20000, step=5000)

# Creating a dataframe for the months of 2024
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
df = pd.DataFrame(index=months)
df.index.name = 'Months'

# Calculating the total and net revenue for each month
starting_accounts_current = starting_accounts
lost_accounts = 0
current_monthly_gmv = monthly_gmv
total_accounts_added = 0
cash_balance = starting_cash_balance
monthly_expenses = starting_monthly_expenses

for month in df.index:
    lost_accounts = (starting_accounts_current + new_accounts) * (account_churn / 100)
    starting_accounts_current = (starting_accounts_current + new_accounts) - lost_accounts
    total_accounts_added += new_accounts
    df.loc[month, 'Total Revenue'] = round(deal_size * starting_accounts_current)
    df.loc[month, 'Fractional Revenue'] = round(df.loc[month, 'Total Revenue'] * (take_rate / 100))
    df.loc[month, 'Marketplace Revenue'] = round(current_monthly_gmv * (marketplace_take_rate / 100))
    df.loc[month, 'Active Accounts'] = round(starting_accounts_current)
    df.loc[month, 'Lost Accounts'] = round(lost_accounts)
    df.loc[month, 'Net Revenue'] = round(df.loc[month, 'Fractional Revenue'] + df.loc[month, 'Marketplace Revenue'])
    df.loc[month, 'Monthly Expenses'] = round(monthly_expenses)
    df.loc[month, 'Net Burn'] = round(df.loc[month, 'Net Revenue'] - monthly_expenses)
    df.loc[month, 'Cash Balance'] = round(cash_balance + df.loc[month, 'Net Revenue'] - monthly_expenses)
    df.loc[month, 'Runway'] = 'Infinite' if df.loc[month, 'Net Burn'] >= 0 else round(df.loc[month, 'Cash Balance'] / (-1 * df.loc[month, 'Net Burn']))
    cash_balance = round(df.loc[month, 'Cash Balance'])
    current_monthly_gmv += round(current_monthly_gmv * (growth_rate / 100))
    if (int(month) % 3 == 0):  # Check if the month is a multiple of 3
        monthly_expenses += quarterly_increase  # Increase the monthly expenses every quarter

# Displaying the data
tabs = st.tabs(["Revenue", "Accounts", "Cash", "Data"])

with tabs[0]:
    st.bar_chart(df[['Fractional Revenue', 'Marketplace Revenue']].sort_index(), color=['#004B71', '#018E82'], use_container_width=True)

with tabs[1]:
    st.bar_chart(df[['Active Accounts', 'Lost Accounts']].sort_index(), color=['#004B71','#FF3131'])

with tabs[2]:
    st.bar_chart(df[['Cash Balance', 'Monthly Expenses', 'Net Burn']].sort_index(), color=['#004B71', '#FF3131', '#000000'], use_container_width=True)

with tabs[3]:
    st.dataframe(df.T.drop('Total Revenue'))  # Removed 'Total Revenue' row

# Displaying KPI metrics in a table
total_revenue_2024 = round(df['Fractional Revenue'].sum() + df['Marketplace Revenue'].sum())
ending_active_accounts = round(df.loc[df.index[-1], 'Active Accounts'])
ending_cash_balance = round(df.loc[df.index[-1], 'Cash Balance'])
runway_in_months = round(df.loc[df.index[-1], 'Runway'])

kpi_data = {'2024 KPIs': ['Total Revenue', 'Active Fractionals', 'Ending Cash Balance', 'Runway in Months'], 'Value': [f"${total_revenue_2024:,}", ending_active_accounts, f"${ending_cash_balance:,}", runway_in_months]}
kpi_df = pd.DataFrame(kpi_data)
st.dataframe(kpi_df, hide_index=True)

