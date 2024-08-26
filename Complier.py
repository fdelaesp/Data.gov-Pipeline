import os
import pandas as pd
import chardet  # For encoding detection

# Define directories and file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_output_dir = os.path.join(script_dir, 'downloaded_csv_files')
reshaped_output_dir = os.path.join(script_dir, 'reshaped_csv_files')  # New directory for reshaped files

# Create the reshaped output directory if it doesn't exist
os.makedirs(reshaped_output_dir, exist_ok=True)


# Function to detect encoding and read FDIC Failed Bank List CSV
def read_fdic_failed_bank_list_csv(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    return pd.read_csv(file_path, encoding=encoding)


# Function to read other CSV files with default UTF-8 encoding
def read_csv_with_default_encoding(file_path):
    return pd.read_csv(file_path, encoding='utf-8')


# FDIC Failed Bank List file ------------------------------------------------------------------------------------
fdic_failed_bank_list_csv = os.path.join(csv_output_dir, 'FDIC_Failed_Bank_List.csv')
try:
    df_failed = read_fdic_failed_bank_list_csv(fdic_failed_bank_list_csv)

    # Print original column names for debugging
    print("Original columns in FDIC Failed Bank List:", df_failed.columns.tolist())

    df_failed.columns = df_failed.columns.str.strip()  # Clean column names: Strip whitespace
    print("Cleaned columns in FDIC Failed Bank List:", df_failed.columns.tolist())

    df_failed.insert(0, 'Indicator', 'Failed Bank')  # Add 'indicator' column with value 'Failed Bank'

    # Rename columns
    df_failed.rename(columns={'State': 'STATE', 'Closing Date': 'DATE', 'Bank Name': 'NAME','City': 'CITY'}, inplace=True)

    # Print columns after renaming for debugging
    print("Columns after renaming in FDIC Failed Bank List:", df_failed.columns.tolist())

    # Define the column order
    column_order = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE']

    # Filter column_order to only include columns that are actually in the DataFrame
    existing_columns = [col for col in column_order if col in df_failed.columns]
    remaining_columns_failed = [col for col in df_failed.columns if col not in existing_columns]
    ordered_columns_failed = existing_columns + remaining_columns_failed
    df_failed = df_failed[ordered_columns_failed]

    # Check reshaped output directory and file path
    reshaped_failed_csv = os.path.join(reshaped_output_dir, 'FDIC_Failed_Bank_List_Reshaped.csv')
    print("Reshaped FDIC Failed Bank List file path:", reshaped_failed_csv)

    # Try saving the DataFrame and catch potential errors
    try:
        df_failed.to_csv(reshaped_failed_csv, index=False)
        print(f"Reshaped FDIC Failed Bank List saved to {reshaped_failed_csv}")
    except Exception as e:
        print("Error saving FDIC Failed Bank List:", e)
except Exception as e:
    print("Error reading FDIC Failed Bank List:", e)

# Financial Institution Office Locations file ----------------------------------------------------------------------------------
financial_institution_office_locations_csv = os.path.join(csv_output_dir, 'Financial_Institution_Office_Locations.csv')
df_locations = read_csv_with_default_encoding(financial_institution_office_locations_csv)


def remove_leading_zeros(column):
    if column.dtype == 'object':
        return column.astype(str).str.lstrip('0')
    return column


df_locations = df_locations.apply(remove_leading_zeros)
print(df_locations)
print("LOCATIONS LOADED AS DF")

# Rename columns
df_locations.rename(columns={'STALP': 'STATE', 'ESTYMD': 'DATE', 'Closing Date': 'DATE'}, inplace=True)

# Financial Institutions file ----------------------------------------------------------------------------------
financial_institutions_csv = os.path.join(csv_output_dir, 'Financial_Institutions.csv')
df_finins = read_csv_with_default_encoding(financial_institutions_csv)
df_finins = df_finins.apply(remove_leading_zeros)
print(df_finins)
print("FINANCIAL INST. LOADED AS DF")

# Rename columns
df_finins.rename(columns={'STALP': 'STATE', 'ESTYMD': 'DATE', 'Closing Date': 'DATE'}, inplace=True)

# Add 'indicator' column and rearrange columns in locations DataFrame
df_locations2 = df_locations[['STATE', 'OFFNAME', 'CITY', 'NAME', 'FI_UNINUM', 'DATE', 'CBSA_METRO']]
df_locations2.insert(0, 'Indicator', 'Office Location')  # Add 'indicator' column with value 'Location'

# Reorder columns
column_order = ['Indicator', 'NAME', 'CITY', 'STATE', 'DATE']
remaining_columns_locations = [col for col in df_locations2.columns if col not in column_order]
ordered_columns_locations = column_order + remaining_columns_locations
df_locations2 = df_locations2[ordered_columns_locations]

# Save reshaped locations DataFrame and handle potential errors
reshaped_locations_csv = os.path.join(reshaped_output_dir, 'Financial_Institution_Office_Locations_Reshaped.csv')
print("Reshaped Financial Institution Office Locations file path:", reshaped_locations_csv)

try:
    df_locations2.to_csv(reshaped_locations_csv, index=False)
    print(f"Reshaped locations saved to {reshaped_locations_csv}")
except Exception as e:
    print("Error saving Financial Institution Office Locations:", e)

# Add 'indicator' column and rearrange columns in institutions DataFrame
df_finins2 = df_finins[['STATE', 'NAMEHCR', 'CITY', 'NAME', 'UNINUM', 'DATE', 'CERT']]
df_finins2.insert(0, 'Indicator', 'Financial Institution')  # Add 'indicator' column with value 'Institution'

# Reorder columns
remaining_columns_finins = [col for col in df_finins2.columns if col not in column_order]
ordered_columns_finins = column_order + remaining_columns_finins
df_finins2 = df_finins2[ordered_columns_finins]

# Save reshaped financial institutions DataFrame and handle potential errors
reshaped_finins_csv = os.path.join(reshaped_output_dir, 'Financial_Institutions_Reshaped.csv')
print("Reshaped Financial Institutions file path:", reshaped_finins_csv)

try:
    df_finins2.to_csv(reshaped_finins_csv, index=False)
    print(f"Reshaped financial institutions saved to {reshaped_finins_csv}")
except Exception as e:
    print("Error saving Financial Institutions:", e)
