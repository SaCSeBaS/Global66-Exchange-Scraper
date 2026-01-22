from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.id import ID
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time


def main(context):

    APP_WRITE_URL = os.environ.get('APP_WRITE_URL')
    APP_WRITE_PROJECT_ID = os.environ.get('APP_WRITE_PROJECT_ID')
    APP_WRITE_KEY = os.environ.get('APP_WRITE_KEY')
    APP_WRITE_DB_ID = os.environ.get('APP_WRITE_DB_ID')
    APP_WRITE_DB_TABLE_ID = os.environ.get('APP_WRITE_DB_TABLE_ID')

    now = datetime.now()
    in_currency = "PEN"
    out_currency = "EUR"
    source = "https://www.global66.com/"

    api_url = "https://api.global66.com/quote/public"
    params = {
        "originRoute": "227",
        "destinationRoute": "36",
        "amount": "100",
        "way": "origin",
        "paymentType": "WIRE_TRANSFER"
    }

    try:
        context.log("Function started")

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://www.global66.com/")
        time.sleep(5)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{api_url}?{query_string}"

        script = f"""
        return fetch("{full_url}", {{
            method: "GET",
            headers: {{
                "accept": "application/json"
            }}
        }}).then(r => r.json());
        """

        data = driver.execute_script(script)

        driver.quit()

        quote_data = data.get("quoteData", {})
        rate = quote_data.get("originToDestinationRate")

        if rate:
            context.log(f"Extraction DateTime: {now.isoformat()}")
            context.log(f"Extracted Rate: {rate}")

            client = Client()
            client.set_endpoint(APP_WRITE_URL)
            client.set_project(APP_WRITE_PROJECT_ID)
            client.set_key(APP_WRITE_KEY)

            tables_db = TablesDB(client)

            result = tables_db.create_row(
                database_id=APP_WRITE_DB_ID,
                table_id=APP_WRITE_DB_TABLE_ID,
                row_id=ID.unique(),
                data={
                    "date": now.isoformat(),
                    "in_currency": in_currency,
                    "out_currency": out_currency,
                    "exchange_rate": float(rate),
                    "source": source
                },
            )

            context.log("Row inserted successfully")
            context.log(f"status: success | rate: {rate}")

            return context.res.json({
                "status": "success",
                "rate": rate,
                "timestamp": now.isoformat()
            })

        else:
            context.log("status: error | message: Rate not found in the response.")
            return context.res.json({
                "status": "error",
                "message": "Rate not found in the response."
            })

    except Exception as e:
        context.log(f"status: error | message: An error occurred - {e}")
        return context.res.json({
            "status": "error",
            "message": f"An error occurred: {e}"
        })