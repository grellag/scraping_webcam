from gazpacho import get, Soup
from urllib.request import urlretrieve
from pathlib import Path
import urllib.request
import urllib.error
import socket
import time
from datetime import datetime
import os
import requests # to get image from the web
import shutil # to save it locally
import glob
import logger.logger
import pandas as pd
import base64

def move_last_file(source, destination, new_filename):
    filelist = [ f for f in os.listdir(destination) if f.endswith(".jpg") ]

    for f in filelist:
        try:
            os.remove(os.path.join(destination, f))
            log.debug(f'move_last_file - Rimosso file: {f} in {destination}')
        except:
            log.debug(f'move_last_file - Non trovato file: {f} in {destination}')
    '''
    folder = os.listdir(source)               # returns a list with all the files in source

    while folder:                             # True if there are any files, False if empty list
    for i in range(5):                     # 5 files at a time 
        file = folder[0]                    # select the first file's name
        curr_file = source + '\\' + file    # creates a string - full path to the file
        shutil.move(curr_file, destination) # move the files
        folder.pop(0)                       # Remove the moved file from the list
    '''
    list_of_files = glob.glob(source + r'\*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    
    print(new_filename)
    try:
        shutil.copy(latest_file, destination) # move the files
        log.debug(f'move_last_file - Copiato file: {latest_file} in {destination}')
    except:
        log.debug(f'move_last_file - Errore su copia file: {latest_file} in {destination}')
    try:
        from pathlib import Path
        file_name = Path(latest_file).stem
        old_filename = destination + '\\' + file_name + '.jpg'
        new_filename = destination + '\\' + new_filename
        os.rename(old_filename, new_filename) 
    except:
        log.debug(f'move_last_file - Rinomina: {latest_file} in {destination}')

def get_url_file_name(url):
    url = url.split("#")[0]
    url = url.split("?")[0]
    return os.path.basename(url)

def is_url_image(image_url):
    image_types = ('.png', '.jpg')
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    elif os.path.splitext(get_url_file_name(image_url))[1] in image_types:
        return True
    return False

def DownFileFromUrl(url, download_path, dlfile):
    head, tail = os.path.split(url) 
    file_img = tail
    r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(dlfile, 'wb') as f:
            r.raw.decode_content = True
            print("r.url: ", r.url)
            print("f.name: ", f.name)
            print("download_path: ", dlfile)
            try:
                shutil.copyfileobj(r.raw, f)
                log.debug(f'DownFileFromUrl - Found Download folder {file_img}')
            except:
                log.debug(f'DownFileFromUrl - Error Download folder {file_img}')
    return file_img
    
def url_retrieve(url: str, outfile: Path, overwrite: bool = True,):
    """
    Parameters
    ----------
    url: str
        URL to download from
    outfile: pathlib.Path
        output filepath (including name)
    overwrite: bool
        overwrite if file exists
    """
    outfile = Path(outfile).expanduser().resolve()
    if outfile.is_dir():
        err = "Please specify full filepath, including filename"
        log.debug(f'Error in url_retrieve: {err}')
        raise ValueError(err)

    if overwrite or not outfile.is_file():
        outfile.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, str(outfile))
        except (socket.gaierror, urllib.error.URLError) as err:
            err = "could not download {} due to {}".format(url, err)
            log.debug(f'Error in url_retrieve: {err}')
            raise ConnectionError(err)

def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

# [START list_service_accounts]
from google.oauth2 import service_account
import googleapiclient.discovery

def list_service_accounts(project_id):
    """Lists all service accounts for the current project."""

    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build('iam', 'v1', credentials=credentials)

    service_accounts = service.projects().serviceAccounts().list(name='projects/' + project_id).execute()

    for account in service_accounts['accounts']:
        print('Name: ' + account['name'])
        print('Email: ' + account['email'])
        print(' ')
    return service_accounts

# [END list_service_accounts]

# [START storage_file_upload_from_memory]
from google.cloud import storage

def authenticate_implicit_with_adc(project_id="your-google-cloud-project-id"):
    """
    When interacting with Google Cloud Client libraries, the library can auto-detect the
    credentials to use.

    // TODO(Developer):
    //  1. Before running this sample,
    //  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
    //  2. Replace the project variable.
    //  3. Make sure that the user account or service account that you are using
    //  has the required permissions. For this sample, you must have "storage.buckets.list".
    Args:
        project_id: The project id of your Google Cloud project.
    """

    # This snippet demonstrates how to list buckets.
    # *NOTE*: Replace the client created below with the client required for your application.
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
    storage_client = storage.Client(project=project_id)
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        print(bucket.name)
    #print("Listed all storage buckets.")

def blob_metadata(project_id, bucket_name, blob_name):
    """Prints out a blob's metadata."""
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    # Retrieve a blob, and its metadata, from Google Cloud Storage.
    # Note that `get_blob` differs from `Bucket.blob`, which does not
    # make an HTTP request.
    blob = bucket.get_blob(blob_name)

    print(f"Blob: {blob.name}")
    print(f"Bucket: {blob.bucket.name}")
    print(f"Storage class: {blob.storage_class}")
    print(f"ID: {blob.id}")
    print(f"Size: {blob.size} bytes")
    print(f"Updated: {blob.updated}")
    print(f"Generation: {blob.generation}")
    print(f"Metageneration: {blob.metageneration}")
    print(f"Etag: {blob.etag}")
    print(f"Owner: {blob.owner}")
    print(f"Component count: {blob.component_count}")
    print(f"Crc32c: {blob.crc32c}")
    print(f"md5_hash: {blob.md5_hash}")
    print(f"Cache-control: {blob.cache_control}")
    print(f"Content-type: {blob.content_type}")
    print(f"Content-disposition: {blob.content_disposition}")
    print(f"Content-encoding: {blob.content_encoding}")
    print(f"Content-language: {blob.content_language}")
    print(f"Metadata: {blob.metadata}")
    print(f"Medialink: {blob.media_link}")
    print(f"Custom Time: {blob.custom_time}")
    print("Temporary hold: ", "enabled" if blob.temporary_hold else "disabled")
    print(
        "Event based hold: ",
        "enabled" if blob.event_based_hold else "disabled",
    )
    if blob.retention_expiration_time:
        print(
            f"retentionExpirationTime: {blob.retention_expiration_time}"
        )
    return blob.name

def delete_blob(project_id, bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

def upload_blob_from_memory(project_id, bucket_name, contents, destination_blob_name, Type):
    """Uploads a file to the bucket."""
    storage_client  = storage.Client(project=project_id)
    bucket          = storage_client.bucket(bucket_name)
    blob            = bucket.blob(destination_blob_name)
    """Check if exists"""
    ret_id = blob_metadata(project_id, bucket_name, destination_blob_name)
    if ret_id != None:
        delete_blob(project_id, bucket_name, destination_blob_name)
        log.debug(f'Deleted {blob.name} in {bucket.name}')
    if Type == "image":
        blob.upload_from_filename(contents)
    else:
        blob.upload_from_string(contents)
    ret_id = blob_metadata(project_id, bucket_name, blob.name)
    log.debug(f'Saved {ret_id} in {bucket.name}')
# [END storage_file_upload_from_memory]

#
from typing import List

def set_bucket_public_iam(project_id,
    bucket_name: str = "your-bucket-name",
    members: List[str] = ["allUsers"],
):
    """Set a public IAM Policy to bucket"""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    policy = bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append(
        {"role": "roles/storage.objectViewer", "members": members}
    )

    bucket.set_iam_policy(policy)

    print(f"Bucket {bucket.name} is now publicly readable")
#

if __name__ == "__main__":
    log = logger.logger.setup_applevel_logger(file_name = 'app_webcam_debug.log')
    authenticate_implicit_with_adc("grellag-python")  
    #list_service_accounts("grellag-python")
    html_output = "index.html"
    log.debug(f'Sto aggiornando HTML con {html_output}')

    upload_blob_from_memory("grellag-python", "www.giorgiogrella.net", html_output, "index.html", "text")
    upload_blob_from_memory("grellag-python", "www.giorgiogrella.net", "style.css", "style.css", "text")
    set_bucket_public_iam("grellag-python", "www.giorgiogrella.net")
    #time.sleep(5) # Sleep for 3 seconds

    log.debug(f'Aggiornato HTML con: {html_output}')
    log.debug('Done html file')