from fastapi  import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os, httpx 


load_dotenv()

app = FastAPI()
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client["smsviewer"]
message = db["messages"]


FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")
FIVESIM_HEADERS = {"Authorization": f"Bearer {FIVESIM_API_KEY}"}


@app.post("/api/request-number")
async def request_number():
    url = "https://5sim.net/v1/user/buy/activation/any/any/whatsapp"
    async with httpx.AsyncClient() as client:
        response =  await client.get(url,headers=FIVESIM_HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=400,detail="Error getting number")
        return response.text()
        # return{
        #     "number":data["phone"],
        #     "id":data["id"]
        # }


@app.get("/api/v1/fetch-msg/{order_id}")
async def fetch_sms(order_id: str):
    url = f"https//5sim.net/v1/user/check/{order_id}"
    async with httpx.AsyncClient as client:
        response = await client.get(url,headers=FIVESIM_HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error fetching message")
        data = response.json()
        for sms in data.get("sms", []):
            message.update_one(
                {"id": sms["id"]},
                {"$set":sms},
                upsert=True   
            )
        return data.get("sms", [])