from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from random import sample
from uuid import uuid4

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows access from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory databases
users_db = []
blogs_db = []
sessions = {}
next_blog_id = 0

# Define models
class User(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    city: Optional[str] = None

class LoginRequest(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

class Blog(BaseModel):
    title: str
    content: str
    author: str
    image: Optional[str] = None
    created_at: Optional[str] = None

@app.post("/register/")
async def register_user(user: User):
    if any(u['email'] == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    users_db.append(user.dict())
    return {"message": "User registered successfully", "user": user.dict()}

@app.post("/login/")
async def login_user(login_request: LoginRequest):
    for user in users_db:
        if (user['name'] == login_request.name and
            user['surname'] == login_request.surname and
            user['email'] == login_request.email and
            user['password'] == login_request.password):
            session_id = str(uuid4())
            sessions[session_id] = user
            return {"success": True, "message": "Login successful", "session_id": session_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/logout/")
async def logout_user(request: Request):
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        session_id = authorization.split(" ")[1]
        if session_id in sessions:
            del sessions[session_id]
            return {"message": "Logout successful"}
    raise HTTPException(status_code=401, detail="Invalid session")

@app.get("/users/")
async def get_users():
    return {"users": users_db}

@app.post("/blogs/")
async def create_blog(blog: Blog):
    global next_blog_id
    blog_dict = blog.dict()
    blog_dict['id'] = next_blog_id
    next_blog_id += 1
    blogs_db.append(blog_dict)
    return {"message": "Blog created successfully", "blog": blog_dict}

@app.get("/blogs/")
async def get_blogs():
    return {"blogs": blogs_db}

@app.get("/blogs/{id}")
async def get_blog(id: int):
    for blog in blogs_db:
        if blog['id'] == id:
            return {"blog": blog}
    raise HTTPException(status_code=404, detail="Blog not found")

@app.put("/blogs/{id}")
async def update_blog(id: int, updated_blog: Blog):
    for i, blog in enumerate(blogs_db):
        if blog['id'] == id:
            blog_dict = updated_blog.dict()
            blog_dict['id'] = id
            blogs_db[i] = blog_dict
            return {"message": "Blog updated successfully", "blog": blog_dict}
    raise HTTPException(status_code=404, detail="Blog not found")

@app.delete("/blogs/{id}")
async def delete_blog(id: int):
    global blogs_db
    blogs_db = [blog for blog in blogs_db if blog['id'] != id]
    return {"message": "Blog deleted successfully"}

@app.get("/featured-blogs/")
async def get_featured_blogs():
    if len(blogs_db) < 3:
        raise HTTPException(status_code=404, detail="Not enough blogs to display")
    featured_blogs = sample(blogs_db, 3)
    return {"featured_blogs": featured_blogs}
