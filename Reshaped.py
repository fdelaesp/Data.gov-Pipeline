import pandas as pd
import os

# Define directories and file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
reshaped_output_dir = os.path.join(script_dir, 'reshaped_csv_files')  # Directory with reshaped files
combined_output_dir = os.path.join(script_dir, 'combined_files')  # Directory to save the combined file

# Create the directory if it doesn't exist
os.makedirs(combined_output_dir, exist_ok=True)

# File paths
fdic_failed_csv = os.path.join(reshaped_output_dir, 'FDIC_Failed_Bank_List_Reshaped.csv')
locations_csv = os.path.join(reshaped_output_dir, 'Financial_Institution_Office_Locations_Reshaped.csv')
finins_csv = os.path.join(reshaped_output_dir, 'Financial_Institutions_Reshaped.csv')


# Function to check if file exists and read it
def read_csv_file(file_path, encoding='utf-8'):
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        return pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# Read reshaped CSV files
df_failed = read_csv_file(fdic_failed_csv)
df_locations = read_csv_file(locations_csv, encoding='ISO-8859-1')
df_finins = read_csv_file(finins_csv, encoding='ISO-8859-1')

# Debugging statements
print("FDIC Failed Bank List DataFrame:")
print(df_failed.head() if df_failed is not None else "DataFrame is None")
print("\nFinancial Institution Office Locations DataFrame:")
print(df_locations.head() if df_locations is not None else "DataFrame is None")
print("\nFinancial Institutions DataFrame:")
print(df_finins.head() if df_finins is not None else "DataFrame is None")

# Check columns in each DataFrame
print("\nColumns in FDIC Failed Bank List DataFrame:")
print(df_failed.columns if df_failed is not None else "DataFrame is None")

print("\nColumns in Financial Institution Office Locations DataFrame:")
print(df_locations.columns if df_locations is not None else "DataFrame is None")

print("\nColumns in Financial Institutions DataFrame:")
print(df_finins.columns if df_finins is not None else "DataFrame is None")

# Required columns
required_columns_failed_finins = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE', 'Cert']
required_columns_locations = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE', 'CBSA_METRO']

# Ensure all DataFrames have the required columns
for df in [df_failed, df_finins]:
    for col in required_columns_failed_finins:
        if col not in df.columns:
            df[col] = pd.NA  # Add missing columns with NA values

for df in [df_locations]:
    for col in required_columns_locations:
        if col not in df.columns:
            df[col] = pd.NA  # Add missing columns with NA values

# Proceed only if all files are successfully read
if df_failed is not None and df_locations is not None and df_finins is not None:
    # Update 'Information Type' and 'Information Type 2' columns
    df_failed['Information Type'] = 'Cert'
    df_failed['Information Type 2'] = 'Fund'

    df_finins['Information Type'] = 'Cert'
    df_finins['Information Type 2'] = 'UNINUM'

    df_locations['Information Type'] = 'CBSA_METRO'
    df_locations['Information Type 2'] = 'FI_UNINUM'


    # Function to create 'Data 1' and 'Data 2' columns
    def create_data_columns(df, columns, info_type_col, info_type_col_2):
        # Create 'Data 1' column
        df['Data 1'] = df[columns].apply(
            lambda row: ' '.join(pd.to_numeric(row, errors='coerce').dropna().astype(int).astype(str)), axis=1
        )
        # Append the value from the info_type_col
        df['Data 1'] = df['Data 1'] + ' ' + df[info_type_col].astype(str)

        # Create 'Data 2' column
        df['Data 2'] = df[columns].apply(
            lambda row: ' '.join(pd.to_numeric(row, errors='coerce').dropna().astype(int).astype(str)), axis=1
        )
        # Append the value from the info_type_col_2
        df['Data 2'] = df['Data 2'] + ' ' + df[info_type_col_2].astype(str)


    # List of columns to include in 'Data 1' and 'Data 2'
    columns_failed_finins = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE']
    columns_locations = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE']

    create_data_columns(df_failed, columns_failed_finins, 'Cert', 'Fund')
    create_data_columns(df_finins, columns_failed_finins, 'Cert', 'UNINUM')
    create_data_columns(df_locations, columns_locations, 'CBSA_METRO', 'FI_UNINUM')

    # Define column order
    column_order = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE', 'Information Type', 'Data 1', 'Information Type 2',
                    'Data 2']

    # Check if all required columns are present before concatenating
    if all(col in df_failed.columns for col in column_order) and \
            all(col in df_locations.columns for col in column_order) and \
            all(col in df_finins.columns for col in column_order):
        # Combine DataFrames
        combined_df = pd.concat([
            df_failed[column_order],
            df_locations[column_order],
            df_finins[column_order]
        ], ignore_index=True)  # Added ignore_index=True for better concatenation

        # Debugging: Check if combined_df has data
        print("\nCombined DataFrame:")
        print(combined_df.head())

        # Save to Excel
        excel_path = os.path.join(combined_output_dir, 'Combined_Financial_Data.xlsx')
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Combined Data')
            print(f"Combined data saved to {excel_path}")
        except Exception as e:
            print(f"Error saving combined data to Excel: {e}")
    else:
        print("One or more required columns are missing in one or more DataFrames. Please check the DataFrames.")
else:
    print("One or more files could not be read. Please check the file paths and try again.")
