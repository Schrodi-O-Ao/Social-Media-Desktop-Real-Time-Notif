import requests
import json
import time
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

aoo_path = 'aoo.json'

video_entries = []

search_params = {
    "part": "snippet",
    "channelId": 'UCln9P4Qm3-EAY4aiEPmRwEA',
    "type": "video",
    "maxResults": 1,
    'order': 'date',
    'key': API_KEY,
}

def fetch_latest_video_data():
    response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
    data = response.json()
    return data


def extract_video_id(data):
    video_id = (data['items'][0]['id']['videoId'])
    return video_id


def read_latest_video_id():
    with open(aoo_path, "r") as f: 
        latest_video_id = json.load(f)["new_vid"]
    return latest_video_id


def save_latest_video_id(latest_video_id):
    with open(aoo_path, "w") as f:
        json.dump({"new_vid": latest_video_id}, f)


def is_new_video(video_id, latest_video_id):
    return video_id != latest_video_id


def extract_video_details(data):
    channel = (data['items'][0]['snippet']['channelTitle'])
    title = (data['items'][0]['snippet']['title'])
    date = (data['items'][0]['snippet']['publishedAt'])
    thumbnail = (data['items'][0]['snippet']['thumbnails']['high']['url'])
    video_info = (channel, title, date, thumbnail) 
    return video_info


def display_notification(video_info):
    print(f'''New video --- 
                title: {video_info[1]}
                channel: {video_info[0]}
                date:  {video_info[2]}
                thumbnail: {video_info[3]}''')


try:
    with open(aoo_path, 'r') as f:
        try:
            stored_record = json.load(f)
            print('it exists.')
        except json.JSONDecodeError:
            print('file is empty or corrupt.')
            stored_record = {"new_vid": None}
            with open(aoo_path, 'w') as f:
                json.dump(stored_record, f, indent=4)
except FileNotFoundError:
    print('file not found.')
    stored_record = {"new_vid": None}
    with open(aoo_path, 'w') as f:
        json.dump(stored_record, f, indent=4)


while True:
    response = fetch_latest_video_data()
    new_video_id = extract_video_id(response)
    last_known_video_id = read_latest_video_id()
    if last_known_video_id is None:
        save_latest_video_id(new_video_id)
    else:    
        if is_new_video(new_video_id, last_known_video_id):
            video_details = extract_video_details(response)
            display_notification(video_details)
            save_latest_video_id(new_video_id)
    time.sleep(3600)