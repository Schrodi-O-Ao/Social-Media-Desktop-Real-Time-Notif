import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

url = "https://www.googleapis.com/youtube/v3/search"

aoo_path = 'aoo.json'

video_entries = []

params = {}

response = requests.get(url, params = params)

data = response.json()

channel = (data['items'][0]['snippet']['channelTitle'])
title = (data['items'][0]['snippet']['title'])
date = (data['items'][0]['snippet']['publishedAt'])
thumbnail = (data['items'][0]['snippet']['thumbnails']['default']['url'])


latest_video_id = (data['items'][0]['id']['videoId'])
print(data)
print(f'Title: {title}')
print(f'ID: {latest_video_id}')
print(f'channel: {channel}')
print(f'date: {date}')
print(f'thumbnail: {thumbnail}')