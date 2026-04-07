import requests

api_key = "632ddb10f04af8fa9aa5cbac77bacc46"
city = "Lahore"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

res = requests.get(url)
print(res.json())
