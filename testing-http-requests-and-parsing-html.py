import requests
from bs4 import BeautifulSoup

url = 'https://www.youtube.com/@TechWithTim'

response = requests.get(url)

print('status code: ', response.status_code)
print('content type: ', response.headers.get('Content-Type'))
print(response)

soup = BeautifulSoup(response.text, 'html.parser')

print(soup.title)
for link in soup.find_all('a'):
    print(link.get('href'))