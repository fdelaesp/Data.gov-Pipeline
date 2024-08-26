import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib3

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Directory paths
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_output_dir = os.path.join(script_dir, 'downloaded_csv_files')
os.makedirs(csv_output_dir, exist_ok=True)

# URL to scrape for specific datasets
main_url = 'https://catalog.data.gov/dataset/?q=bank+list&sort=views_recent+desc&res_format=CSV&ext_location=&ext_bbox=&ext_prev_extent=&organization_type=Federal+Government'

# URL of the FDIC Failed Bank List page
fdic_url = 'https://www.fdic.gov/bank-failures/failed-bank-list'

# Function to download specific CSV files based on direct links
def download_specific_csvs():
    print("Scraping datasets from data.gov...")
    response = requests.get(main_url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Define the specific dataset names and their links
    specific_files = {
        'Financial Institution Office Locations': 'https://s3-us-gov-west-1.amazonaws.com/cg-2e5c99a6-e282-42bf-9844-35f5430338a5/downloads/locations.csv',
        'Financial Institutions': 'https://s3-us-gov-west-1.amazonaws.com/cg-2e5c99a6-e282-42bf-9844-35f5430338a5/downloads/institutions.csv'
    }

    # Download each specific file
    for dataset_name, dataset_link in specific_files.items():
        filename = os.path.join(csv_output_dir, dataset_name.replace(' ', '_') + '.csv')
        print(f"Downloading {dataset_name} from {dataset_link} to {filename}")
        response = requests.get(dataset_link, verify=False)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {filename} successfully.")
        else:
            print(f"Failed to download {dataset_name}. Status code: {response.status_code}")

# Function to download FDIC Failed Bank List CSV
def download_fdic_failed_bank_list():
    print("Scraping FDIC Failed Bank List...")
    response = requests.get(fdic_url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the link to the CSV file
    csv_link = None
    for a_tag in soup.find_all('a', href=True):
        if 'banklist.csv' in a_tag['href']:
            csv_link = urllib.parse.urljoin(fdic_url, a_tag['href'])
            break

    # Download the CSV file
    if csv_link:
        filename = os.path.join(csv_output_dir, 'FDIC_Failed_Bank_List.csv')
        print(f"Downloading FDIC Failed Bank List from {csv_link} to {filename}")
        response = requests.get(csv_link, verify=False)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print("FDIC Failed Bank List download complete!")
        else:
            print(f"Failed to download FDIC Failed Bank List. Status code: {response.status_code}")
    else:
        print("CSV link not found on the FDIC page.")

# Execute the functions
download_specific_csvs()
download_fdic_failed_bank_list()
