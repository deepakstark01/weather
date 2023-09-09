import requests
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Welcome to the weather world"}

@app.get("/get_temp")
async def get_temp(query: str):
    url = "https://www.google.com/search?q="
    query = query + "+weather"
    url = url + query
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')  # Fix: Use 'html.parser'
    temperature_element = soup.find(class_='BNeawe iBp4i AP7Wnd')
    temperature = temperature_element.get_text()
    return {"current_temp": temperature}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
