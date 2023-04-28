import os
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# Set up credentials and Drive API client
creds = None
creds = service_account.Credentials.from_service_account_file(
    '\path\to\your\credentialFile.json',
    scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

# Define the ID of the Google Drive folder 
# YOUR GOOGLE DRIVE FOLDER ID DOWN BELOW: 
folder_id = ' --> YOUR FOLDER ID HERE <-- '  


# Define a function to get the link for a file
def get_link(file_id):
    try:
        response = service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        return response['webViewLink']
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

# Define a function to get the files in a folder and their links
def get_files_and_links(folder_id):
    results = []
    query = f"'{folder_id}' in parents"
    page_token = None
    while True:
        try:
            params = {'q': query, 'fields': 'nextPageToken, files(id, name)'}
            if page_token:
                params['pageToken'] = page_token
            files = service.files().list(**params).execute()
            results.extend(files['files'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f'An error occurred: {error}')
            page_token = None
    files_df = pd.DataFrame(results)
    files_df['Link'] = files_df['id'].apply(get_link)
    return files_df[['name', 'Link']]

# Call the function to get the files and links
files_df = get_files_and_links(folder_id)

# Save the data to an Excel file
files_df.to_excel('links.xlsx', index=False)
