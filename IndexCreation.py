import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_and_prepare_data(filepath, sheet_name=0):
    """
    Loads data from a single Excel file, and prepares it.
    Each pair of (Exchange Date, Price) columns is treated as a separate company.
    """
    xls = pd.ExcelFile(filepath)
    df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=0)

    all_company_data = []
    company_names = []

    for i in range(0, df_raw.shape[1], 2):
        date_col_name = df_raw.columns[i]
        price_col_name = df_raw.columns[i+1]
        company_name = price_col_name

        company_df = df_raw[[date_col_name, price_col_name]].copy()
        company_df.columns = ['Date', 'Price']
        company_df['Date'] = pd.to_datetime(company_df['Date'])
        company_df.dropna(subset=['Price'], inplace=True)
        company_df.set_index('Date', inplace=True)
        company_df.rename(columns={'Price': company_name}, inplace=True)

        if not company_df.empty:
            all_company_data.append(company_df)
            company_names.append(company_name)

    if not all_company_data:
        return pd.DataFrame(), []

    merged_df = pd.concat(all_company_data, axis=1, join='outer')
    merged_df.sort_index(inplace=True)
    return merged_df, company_names

def calculate_equal_weighted_index(price_data_df, base_value=100):
    """
    Calculates an equal-weighted index.
    """
    filled_price_data = price_data_df.ffill()
    daily_returns = filled_price_data.pct_change()
    num_companies_active = filled_price_data.notna().sum(axis=1)
    index_daily_returns = daily_returns.mean(axis=1)

    first_valid_date = None
    if not num_companies_active[num_companies_active > 0].empty:
        first_valid_date = num_companies_active[num_companies_active > 0].index[0]
        index_daily_returns.loc[first_valid_date] = 0
    else: # Handle case where there's no valid data at all
        return pd.Series(dtype=float), daily_returns, filled_price_data, num_companies_active


    index_values = base_value * (1 + index_daily_returns).cumprod()
    index_values = index_values.reindex(filled_price_data.index)

    if first_valid_date:
        # Set NaNs for dates before any stock was active
        if index_values.index[0] < first_valid_date:
             index_values.loc[:pd.Timestamp(first_valid_date) - pd.Timedelta(days=1)] = float('nan')
        # Ensure the first valid date starts exactly at base_value
        index_values.loc[first_valid_date] = base_value
    else: # If no valid date, the whole series should be NaN
        index_values[:] = float('nan')


    return index_values, daily_returns, filled_price_data, num_companies_active

def plot_monthly_index(index_series, title='Monthly Index Performance'):
    """
    Plots the index performance on a monthly basis.
    Uses the last available index value of each month.
    """
    if index_series.empty or index_series.dropna().empty:
        print("Index series is empty or contains all NaNs. Cannot plot.")
        return

    # Resample to get the last trading day's value of each month
    monthly_index = index_series.resample('M').last() # 'M' stands for month-end frequency

    # Drop NaN values that might result from months with no data
    monthly_index = monthly_index.dropna()

    if monthly_index.empty:
        print("No data available for monthly plotting after resampling and dropping NaNs.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(monthly_index.index, monthly_index.values, marker='o', linestyle='-')

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Index Value')
    plt.grid(True)

    # Format the x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(monthly_index) // 12))) # Adjust interval for readability
    plt.gcf().autofmt_xdate() # Auto-formats the x-axis labels to prevent overlap

    plt.show()

# --- Main Script ---

# Define your file paths
file_path1Neo = 'Neo Banks Price History/All Neo Banks PH.xlsx' # <--- IMPORTANT: CHANGE THIS TO YOUR ACTUAL FILE NAME
file_path2Cha = 'Challenger Banks Price History/All Challenger Banks PH.xlsx'

# Load and prepare data
combined_prices_df, all_company_names = load_and_prepare_data(file_path1)

if not combined_prices_df.empty:
    print("--- Combined and Aligned Price Data (Head) ---")
    print(combined_prices_df.head())

    # Calculate the equal-weighted index
    neo_bank_index, _, _, _ = calculate_equal_weighted_index(combined_prices_df, base_value=100)

    print("\n--- Calculated Neo Bank Index (First 5 values) ---")
    print(neo_bank_index.head())
    print("\n--- Calculated Neo Bank Index (Last 5 values) ---")
    print(neo_bank_index.tail())

    # Plot the monthly index performance
    plot_monthly_index(neo_bank_index, title='Neo Bank Index - Monthly Performance')

    # To save the index to a new Excel file:
    # neo_bank_index_df = pd.DataFrame(neo_bank_index, columns=['NeoBankIndex'])
    # neo_bank_index_df.to_excel('neo_bank_index.xlsx')
    # print("\nIndex saved to neo_bank_index.xlsx")

else:
    print(f"No data loaded from {file_path1}. Please check file path and Excel sheet structure.")