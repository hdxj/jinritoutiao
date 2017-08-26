import requests
url = 'https://www.baidu.com/'
html = requests.get(url)
print(type(html.status_code))