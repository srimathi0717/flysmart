from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
from source.config import SKY_SCANNER_URL,HEADERS

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize SQLite database
conn = sqlite3.connect('flights.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS flights
             (price INTEGER, flight_type TEXT, departure_city TEXT, arrival_city TEXT, flight_date TEXT, airline TEXT, airline_code TEXT)''')
conn.commit()

# Initialize Selenium WebDriver
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
async def get_least_price_flight(request: Request, from_entity_id: str = Form(...), to_entity_id: str = Form(...), year_month: str = Form(...)):
    querystring = {"fromEntityId": from_entity_id, "toEntityId": to_entity_id, "yearMonth": year_month}

    try:
        # Fetch data using requests
        response = requests.get(SKY_SCANNER_URL, headers=HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()

        price_grid = data.get('data', {}).get('PriceGrids', {}).get('Grid', [[]])
        traces = data.get('data', {}).get('Traces', {})

        flights = []

        def parse_trace(trace_str):
            parts = trace_str.split('*')
            date_str = parts[4]
            date_formatted = datetime.strptime(date_str, '%Y%m%d').strftime('%d-%m-%Y')
            return {
                "FlightType": parts[1],
                "DepartureCity": parts[2],
                "ArrivalCity": parts[3],
                "FlightDate": date_formatted,
                "Airline": parts[5],
                "AirlineCode": parts[6]
            }

        for day in price_grid[0]:
            if 'Indirect' in day:
                price = day['Indirect']['Price']
                trace_refs = day['Indirect']['TraceRefs']
                flight_details = [parse_trace(traces[ref]) for ref in trace_refs]
                flights.append({
                    "price": price,
                    "details": flight_details
                })

        if flights:
            # Insert data into SQLite database
            with sqlite3.connect('flights.db') as conn:
                c = conn.cursor()
                for flight in flights:
                    for detail in flight['details']:
                        c.execute('''INSERT INTO flights (price, flight_type, departure_city, arrival_city, flight_date, airline, airline_code)
                                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                  (flight['price'], detail['FlightType'], detail['DepartureCity'], detail['ArrivalCity'], detail['FlightDate'], detail['Airline'], detail['AirlineCode']))
                conn.commit()

            least_price_flight = min(flights, key=lambda x: x["price"])
            least_price = least_price_flight["price"]
            least_price_details = least_price_flight["details"]

            # Selenium: Fetch additional data if needed (example placeholder)
            driver.get("https://www.skyscanner.co.in/")  
            # Add your Selenium data fetching logic here

            # Generate visualization
            with sqlite3.connect('flights.db') as conn:
                df = pd.read_sql_query("SELECT flight_date, COUNT(*) as flight_count FROM flights GROUP BY flight_date", conn)

            fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))

            wedges, texts, autotexts = ax.pie(df['flight_count'], labels=df['flight_date'], autopct='%1.1f%%', startangle=140, textprops=dict(color="w"))
            ax.legend(wedges, df['flight_date'], title="Flight Dates", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.setp(autotexts, size=10, weight="bold")
            ax.set_title("Flight Frequency by Date")

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()

            return templates.TemplateResponse("results.html", {
                "request": request,
                "least_price": least_price,
                "flight_details": least_price_details,
                "image_base64": image_base64
            })
        else:
            raise HTTPException(status_code=404, detail="No flight details available.")
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Error occurred: {err}")
    except ValueError as json_err:
        raise HTTPException(status_code=500, detail=f"JSON decode error: {json_err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        driver.quit()  # Ensure the driver is quit to free resources

# Close SQLite connection when shutting down the app
@app.on_event("shutdown")
def shutdown_event():
    conn.close()
