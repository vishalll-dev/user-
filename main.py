import asyncio
import os
import urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
KEEP_ALIVE_SECONDS = 10 * 60  # har 10 minute


async def keep_alive():
    """Render free plan 15 min baad sleep hota hai, isliye har 10 min self-ping."""
    base_url = os.getenv("RENDER_EXTERNAL_URL")  # Render khud set karta hai
    if not base_url:
        return  # local run par ping nahi
    while True:
        await asyncio.sleep(KEEP_ALIVE_SECONDS)
        try:
            await asyncio.to_thread(urllib.request.urlopen, f"{base_url}/health", None, 15)
            print("keep-alive ping ok")
        except Exception as e:
            print("keep-alive ping failed:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(keep_alive())
    yield
    task.cancel()


app = FastAPI(title="Fake Users API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class User(BaseModel):
    id: int
    name: str
    age: int
    contact: str
    email: str
    address: str
    note: str


class UserCreate(BaseModel):
    name: str
    age: int
    contact: str
    email: str
    address: str
    note: str = ""


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None


# ---- Fake data (10 users) ----
data = [
    {"id": 1, "name": "Aarav Sharma", "age": 28, "contact": "+91 98765 43210", "email": "aarav.sharma@example.com", "address": "12 Rajpur Road, Dehradun, Uttarakhand", "note": "Prefers email communication."},
    {"id": 2, "name": "Priya Verma", "age": 34, "contact": "+91 91234 56789", "email": "priya.verma@example.com", "address": "45 MG Marg, Mumbai, Maharashtra", "note": "VIP customer."},
    {"id": 3, "name": "Rohan Mehta", "age": 22, "contact": "+91 99887 76655", "email": "rohan.mehta@example.com", "address": "7 Park Street, Kolkata, West Bengal", "note": "Student, interested in internships."},
    {"id": 4, "name": "Sneha Iyer", "age": 30, "contact": "+91 90123 45678", "email": "sneha.iyer@example.com", "address": "88 Anna Salai, Chennai, Tamil Nadu", "note": "Call after 6 PM."},
    {"id": 5, "name": "Vikram Singh", "age": 41, "contact": "+91 98111 22233", "email": "vikram.singh@example.com", "address": "23 Civil Lines, Jaipur, Rajasthan", "note": "Requested product demo."},
    {"id": 6, "name": "Ananya Gupta", "age": 26, "contact": "+91 97000 11122", "email": "ananya.gupta@example.com", "address": "5 Sector 17, Chandigarh", "note": "Newsletter subscriber."},
    {"id": 7, "name": "Karan Malhotra", "age": 37, "contact": "+91 96543 21098", "email": "karan.malhotra@example.com", "address": "19 Connaught Place, New Delhi", "note": "Pending invoice."},
    {"id": 8, "name": "Meera Nair", "age": 29, "contact": "+91 94470 33344", "email": "meera.nair@example.com", "address": "31 MG Road, Kochi, Kerala", "note": "Referred by Priya Verma."},
    {"id": 9, "name": "Arjun Reddy", "age": 33, "contact": "+91 98480 55566", "email": "arjun.reddy@example.com", "address": "62 Banjara Hills, Hyderabad, Telangana", "note": "Interested in premium plan."},
    {"id": 10, "name": "Kavya Joshi", "age": 24, "contact": "+91 95555 77788", "email": "kavya.joshi@example.com", "address": "14 FC Road, Pune, Maharashtra", "note": "Feedback: loves the app."},
]


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


@app.get("/users", response_model=List[User])
def get_users(search: Optional[str] = None):
    if search:
        s = search.lower()
        return [u for u in data if s in u["name"].lower() or s in u["email"].lower()]
    return data


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for u in data:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    new_id = max((u["id"] for u in data), default=0) + 1
    new_user = {"id": new_id, **user.model_dump()}
    data.append(new_user)
    return new_user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, changes: UserUpdate):
    for u in data:
        if u["id"] == user_id:
            u.update(changes.model_dump(exclude_unset=True))
            return u
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(data):
        if u["id"] == user_id:
            data.pop(i)
            return {"message": f"User {user_id} deleted"}
    raise HTTPException(status_code=404, detail="User not found")


# ---- Frontend ----
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")
