import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # For better date formatting

def create_and_plot_financial_index(excel_filepath, sheet_name=0, base_value=100):
    """
    Creates an equally weighted financial index from company stock prices
    read from an Excel file and plots it. Handles different IPO dates.

    The Excel file should have 'Exchange Date' as the first column,
    and subsequent columns for each company's closing price.

    Args:
        excel_filepath (str): Path to the Excel file.
        sheet_name (str or int, optional): Sheet name or index if the Excel file
                                           has multiple sheets. Defaults to 0 (the first sheet).
        base_value (float, optional): The value to which each stock (and thus the initial index)
                                      is conceptually rebased. Defaults to 100.

    Returns:
        pandas.Series: The calculated financial index.
                       Returns None if an error occurs or no data is processed.
    """
    try:
        # 1. Load Data
        # Assuming the first column is the date and should be the index
        df_prices = pd.read_excel(excel_filepath, sheet_name=sheet_name, index_col=0)
        
        # Ensure the index is parsed as datetime objects
        df_prices.index = pd.to_datetime(df_prices.index)
        
        # Sort by date, just in case it's not already
        df_prices = df_prices.sort_index()

        print("--- Original Data (first 5 rows) ---")
        print(df_prices.head())

        if df_prices.empty:
            print("Error: The DataFrame is empty after loading. Check the Excel file and sheet name.")
            return None

        # 2. Rebase Each Stock
        # We will create a new DataFrame for rebased prices
        df_rebased = pd.DataFrame(index=df_prices.index)

        valid_companies_for_index = []

        for company_name in df_prices.columns:
            stock_prices = df_prices[company_name].copy()
            
            # Find the first valid price for this stock (its "IPO price" in this dataset)
            first_valid_index = stock_prices.first_valid_index()
            
            if first_valid_index is None:
                print(f"Warning: Company '{company_name}' has no price data. Skipping.")
                continue
                
            first_price = stock_prices[first_valid_index]
            
            if pd.isna(first_price) or first_price == 0:
                print(f"Warning: First price for company '{company_name}' is NaN or zero. Skipping.")
                continue

            # Rebase: (Price_t / Price_first_day) * BaseValue
            # This makes the stock's "value" start at `base_value` on its first day of data
            # It will be NaN before its first_valid_index
            rebased_series = (stock_prices / first_price) * base_value
            df_rebased[company_name] = rebased_series
            valid_companies_for_index.append(company_name)

        if not valid_companies_for_index:
            print("Error: No valid company data found to create an index.")
            return None
            
        print(f"\n--- Rebased Data for {len(valid_companies_for_index)} companies (first 5 rows) ---")
        print(df_rebased[valid_companies_for_index].head())

        # 3. Calculate the Index
        # The index is the mean of the rebased prices of available stocks at each point in time.
        # .mean(axis=1) calculates the mean across columns for each row, automatically skipping NaNs.
        financial_index = df_rebased[valid_companies_for_index].mean(axis=1)
        
        # Remove any leading NaNs from the index itself (e.g., if all first prices are on different days)
        financial_index = financial_index.loc[financial_index.first_valid_index():]


        if financial_index.empty:
            print("Error: The resulting index is empty. This could happen if there are no overlapping periods of data.")
            return None

        print("\n--- Calculated Financial Index (first 5 values) ---")
        print(financial_index.head())
        print("\n--- Calculated Financial Index (last 5 values) ---")
        print(financial_index.tail())

        # 4. Plot the Index
        plt.figure(figsize=(14, 7))
        plt.plot(financial_index.index, financial_index.values, label=f'Custom Financial Index (Base {base_value})', color='dodgerblue')
        
        plt.title('Custom Equally Weighted Financial Index Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(f'Index Value (Rebased to {base_value})', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Improve date formatting on x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
        plt.xticks(rotation=30, ha='right')
        
        plt.tight_layout() # Adjust plot to prevent labels from overlapping
        plt.show()

        return financial_index

    except FileNotFoundError:
        print(f"Error: The file '{excel_filepath}' was not found.")
        return None
    except KeyError as e:
        print(f"Error: A required column might be missing or named incorrectly (e.g., 'Exchange Date' as index). Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Example Usage ---
if __name__ == "__main__":
    # To use this script:
    # 1. Save your Excel file (e.g., "stock_data.xlsx") in the same directory as this script,
    #    or provide the full path.
    # 2. Make sure the first column is named 'Exchange Date' (or similar, and adjust index_col if needed)
    #    and contains dates. Subsequent columns should be company stock prices.
    # 3. Run the script.

    # Create a dummy Excel file based on the provided image format for demonstration
    data = {
        'Exchange Date': pd.to_datetime([
            '2025-05-07', '2025-05-06', '2025-05-05', '2025-05-02', '2025-05-01',
            '2025-04-30', '2025-04-29', '2025-04-28', '2025-04-25', '2025-04-24',
            '2025-04-23', '2025-04-22', '2025-04-21', '2025-04-17', '2025-04-16',
            '2025-04-15'
        ]),
        'DAVE': [
            107.83, 105.92, 104.75, 104.72, 96.43, 94.82, 95.22, 93.68, 92.93, 89.96,
            85.91, 83.37, 80.66, 84.27, 82.17, 83.84
        ],
        'ZIP': [
            1.1722, 1.0485, 1.0444, 1.0565, 1.1011, 1.1075, 1.1039, 1.0738, 1.0735, 1.0015,
            0.9611, 1.0607, 1.0955, 0.9386, 0.9487, 0.9333
        ],
        'WISE': [
            13.57, 13.77, None, 13.66, 13.21, 13.04, 13.25, 13.00, 12.89, 12.93,
            12.82, 12.77, 12.77, 12.82, 12.85, 12.60
        ], # WISE has a None on 05-May
        'RELY': [
            21.09, 21.20, 20.99, 20.94, 20.27, 20.22, 20.41, 20.01, 20.05, 19.98,
            19.63, 19.35, 19.10, 19.93, 19.84, 20.19
        ],
        'NEWCO': [ # A company that IPOs later
            None, None, None, None, None, None, None, 50.00, 51.50, 50.75,
            49.00, 49.50, 48.00, None, None, None # Assume some missing data too
        ]
    }
    dummy_df = pd.DataFrame(data)
    dummy_df = dummy_df.set_index('Exchange Date').sort_index() # Sort ascending for typical time series
    
    # If your actual data is sorted descending (newest first), you'll need to sort it:
    # dummy_df = dummy_df.sort_index(ascending=True) 
    # The script already does df_prices.sort_index()

    dummy_excel_file = 'All Financial Institutions.xlsx'
    dummy_df.to_excel(dummy_excel_file, sheet_name='StockData')
    print(f"Dummy Excel file '{dummy_excel_file}' created with sheet 'StockData'.")

    # Call the function with the dummy file
    # Replace 'sample_financial_data.xlsx' with your actual file name
    # and 'StockData' with your actual sheet name if it's different.
    index_series = create_and_plot_financial_index(dummy_excel_file, sheet_name='StockData')

    if index_series is not None:
        print("\n--- Index Series successfully created. ---")
        # You can save the index to a new Excel or CSV file if needed:
        # index_series.to_csv('financial_index.csv', header=['IndexValue'])
        # index_series.to_excel('financial_index.xlsx', sheet_name='Index')