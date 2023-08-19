from google_photos_downloader import GooglePhotosApi, getAlbumsList, getAlbumContents
from pathlib import Path
import json, os, requests

from rich.progress import Progress
from rich.status import Status
from rich import print

baseDirectory = "L:\\GooglePhotosMarck\\Albums"
nofAlbums = 0
albums = []

consoleStatus = Status('Download albums')

consoleStatus.start()

def getAlbumData(pageToken = None):
    global nofAlbums, albums
    # Get albums
    albumData = getAlbumsList(pageToken).json()

    for album in albumData["albums"]:
        if("title" not in album):
            continue
        if("mediaItemsCount" not in album):
            continue
        albums.append(album)

    if ("nextPageToken" in albumData):
        getAlbumData(pageToken=albumData["nextPageToken"])
        
getAlbumData()
print()
print(f"[yellow]{len(albums)} albums found")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------")

print("Creating directories for albums...", end='\r')

for album in albums:
    title = album["title"]
    titleSanitized = "".join(x for x in title if (x not in ":.")).strip()
    albumDirectory = baseDirectory + "\\" + titleSanitized
    try:
        Path(albumDirectory).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    with open(albumDirectory + "\\info.json", "w") as infofile:
        json.dump(album, infofile)
    album["localpath"] = albumDirectory

print("[green]Creating directories for albums done!")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------")

print("Start downloading album contents...")

consoleStatus.stop()

def downloadAlbumContents(album, progress, task, pageToken = None):
    albumContents = getAlbumContents(album["id"], pageToken=pageToken).json()
    for item in albumContents["mediaItems"]:
            progress.update(task, advance=1, description=f'[yellow]{item["filename"]:50}')
            # Check if exists
            targetFile = os.path.join(album["localpath"], item["filename"])
            if os.path.isfile(targetFile):
                album["mediaItemsCountSkipped"] += 1
            else:    
                if item["mimeType"]== "video/mp4":
                    url = item["baseUrl"] + "=dv"
                else:
                    url = item["baseUrl"] + "=d"
                itemData = requests.get(url)
                size = int(itemData.headers["Content-Length"])

                with open(targetFile, 'wb') as f:
                    f.write(itemData.content)
                    f.close()

            album["mediaItemsCountProcessed"] += 1

    if ("nextPageToken" in albumContents):
        downloadAlbumContents(album, progress, task, pageToken=albumContents["nextPageToken"])
    else:
        print(f'{album["title"]:50} : {album["mediaItemsCount"]:>4} items done ({album["mediaItemsCountSkipped"]:>4} skipped)')

for album in albums:
    album["mediaItemsCountProcessed"] = 0
    album["mediaItemsCountSkipped"] = 0
    print(f'[cyan]{album["title"]:50} ({album["mediaItemsCount"]:>4} items)')
    with Progress() as progress:
        task = progress.add_task(f'[cyan]{"Downloading":50}', total=int(album["mediaItemsCount"]))
        downloadAlbumContents(album, progress, task)