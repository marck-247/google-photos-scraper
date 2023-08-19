from google_photos_downloader import getMediaItemsForDateRange
from pathlib import Path
import json, os, requests, calendar
from datetime import date, datetime
from dateutil.parser import *

from rich.progress import Progress
from rich.status import Status
from rich import print

print("-------------------------------------------------------------------------------------------------------------------------------------------------------")

baseDirectory = "L:\\GooglePhotosMarck\\Timeline"
timeline = []

earliestDate = date(2022,1,1)
latestDate = date(2022,12,31)

print(f"[cyan]Start date : {earliestDate:%d-%m-%Y}")
print(f"[cyan]Latest date: {latestDate:%d-%m-%Y}")

consoleStatus = Status('Investigating timeline')

consoleStatus.start()

def getItemsInDateRange(dateFrom:date, dateTo:date, pageToken = None):
    global timeline
    # Get data
    timelineData = getMediaItemsForDateRange(dateFrom, dateTo, pageToken=pageToken)

    if timelineData.status_code != 200:
        print("[red]Error while trying to request media items!")
        print("[grey]" + timelineData.reason)
        print("[grey]" + timelineData.text)
        return

    for mediaItem in timelineData.json()["mediaItems"]:
        timeline.append(mediaItem)

    consoleStatus.update(f'Investigating timeline ({len(timeline)} items so far)')

    if ("nextPageToken" in timelineData.json()):
        getItemsInDateRange(dateFrom, dateTo, pageToken=timelineData.json()["nextPageToken"])
        
getItemsInDateRange(earliestDate, latestDate)
print(f"[green]{len(timeline)} mediaItems found")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------")

consoleStatus.update("Creating directories for timeline...")

# Create 'year' and 'month' directories
allDirs = []
currentYear = earliestDate.year
currentMonth = earliestDate.month
while (currentYear <= latestDate.year):
    allDirs.append(str(currentYear))
    while (currentMonth <= 12 and (currentYear != latestDate.year or currentMonth <= latestDate.month)):
         allDirs.append(str(currentYear) + "\\" + f"{currentMonth:02} " + calendar.month_name[currentMonth])
         currentMonth += 1
    currentYear += 1
    currentMonth = 1

for dir in allDirs:
    try:
        Path(baseDirectory + "\\" + dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError: pass

print("[green]Creating directories for albums done!")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
consoleStatus.stop()
print(f"[cyan]Downloading from timeline (total {len(timeline):>4} items)")
with Progress() as progress:
    task = progress.add_task(f'[cyan]{"Downloading":100}', total=len(timeline))
    mediaItemsCountDownloaded = 0
    mediaItemsCountSkipped = 0
    for mediaItem in timeline:
        creationTime = parse(mediaItem["mediaMetadata"]["creationTime"])
        targetDirectory = str(creationTime.year) + "\\" + f"{creationTime.month:02} " + calendar.month_name[creationTime.month]
        if targetDirectory not in allDirs:
            raise FileNotFoundError(f"Directory does not exist ({targetDirectory})")
        
        # Check if exists
        targetFile = os.path.join(baseDirectory, targetDirectory, mediaItem["filename"])
        if os.path.isfile(targetFile):
            mediaItemsCountSkipped += 1
        else:    
            if mediaItem["mimeType"]== "video/mp4":
                url = mediaItem["baseUrl"] + "=dv"
            else:
                url = mediaItem["baseUrl"] + "=d"
            itemData = requests.get(url)
            size = int(itemData.headers["Content-Length"])

            with open(targetFile, 'wb') as f:
                f.write(itemData.content)
                f.close()

            mediaItemsCountDownloaded += 1

        progress.update(task, advance=1, description=f'[yellow]{creationTime:%d-%m-%Y} : {mediaItem["filename"]:100}')

print(f"[green]Downloading items from timeline done! {mediaItemsCountDownloaded:>4} items downloaded ,{mediaItemsCountSkipped:>4} skipped")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
