import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import json
import requests
from datetime import date

class GooglePhotosApi:
    def __init__(self,
                 api_name = 'photoslibrary',
                 client_secret_file= f'./credentials/client_secret.json',
                 api_version = 'v1',
                 scopes = ['https://www.googleapis.com/auth/photoslibrary']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api

        Return:
            service:
        '''

        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./credentials/token_{self.api_name}_{self.api_version}.pickle'

        self.cred = None

    def run_local_server(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server()

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)
        
        return self.cred

# Initialize photos api and create service
google_photos_api = GooglePhotosApi()
creds = google_photos_api.run_local_server()

headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer {}'.format(creds.token)
}

def getAlbumsList(pageToken = None):
    url = 'https://photoslibrary.googleapis.com/v1/albums'

    if pageToken is not None:
        url += "?pageToken=" + pageToken    

    try:
        res = requests.request("GET", url, headers=headers)
    except:
        print('Request error') 
    
    return(res)

def getAlbumContents(albumID, pageToken = None, pageSize = 100):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    payload = {
        "pageSize": pageSize, 
        "albumId": albumID,
        "pageToken": pageToken
        }
    
    try:
        res = requests.request("POST", url,  headers=headers, params=payload)
    except:
        print('Request error') 
    
    return(res)

def getMediaItemsList(pageToken = None, pageSize = 100):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems'
    
    if pageToken is not None:
        url += "?pageToken=" + pageToken + "&pageSize=" + str(pageSize)
    else:
        url += "?pageSize=" + str(pageSize)
    
    try:
        res = requests.request("GET", url,  headers=headers)
    except:
        print('Request error') 
    
    return(res)

def getMediaItemsForDate(_date: date):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    payload = {"filters": {"dateFilter": {"dates": [{"day": _date.day,"month": _date.month,"year": _date.year}]}}}
    
    try:
        res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    except:
        print('Request error') 
    
    return(res)

def getMediaItemsForDateRange(fromDate: date, toDate: date, pageToken = None, pageSize = 100):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    payload = {"filters": {"dateFilter": {"ranges": [{
        "startDate":    {"day": fromDate.day,"month": fromDate.month,"year": fromDate.year},
        "endDate":      {"day": toDate.day,"month": toDate.month,"year": toDate.year},
        }]}},
        "pageSize": pageSize, 
        "pageToken": pageToken}
    
    try:
        res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    except:
        print('Request error') 
    
    return(res)

# -------------------------------------------------------------------------------------------------------------------------------------------------------

