
import os
import hmac
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
import rag

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from vector_store import process_document


# --------------------------------------------------
# 1. Environment configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(BASE_DIR, ".env"))

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or ""
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or "HS256"

JWT_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_MINUTES", "60")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")


# --------------------------------------------------
# 2. FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Supply Chain AI Assistant API",
    description="Enterprise AI Demand Planning and Supply Chain Intelligence",
    version="1.0.0"
)

security = HTTPBearer()

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------------------------------------
# 3. Request models
# --------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


# --------------------------------------------------
# 4. User authentication
# --------------------------------------------------

def authenticate_user(username: str, password: str):

    users = [
        (
            os.getenv("ADMIN_USERNAME"),
            os.getenv("ADMIN_PASSWORD"),
            "Administrator"
        ),
        (
            os.getenv("PLANNER_USERNAME"),
            os.getenv("PLANNER_PASSWORD"),
            "Demand Planner"
        ),
        (
            os.getenv("WAREHOUSE_USERNAME"),
            os.getenv("WAREHOUSE_PASSWORD"),
            "Warehouse Manager"
        )
    ]

    for saved_username, saved_password, role in users:

        if (
            saved_username
            and saved_password
            and hmac.compare_digest(username, saved_username)
            and hmac.compare_digest(password, saved_password)
        ):
            return role

    return None


# --------------------------------------------------
# 5. JWT token generation
# --------------------------------------------------

def create_access_token(username: str, role: str):

    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=JWT_EXPIRATION_MINUTES
        )
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# --------------------------------------------------
# 6. Verify JWT token
# --------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        claims = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        return claims

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# --------------------------------------------------
# 7. Home API
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Supply Chain AI Assistant API is running"
    }


# --------------------------------------------------
# 8. Health check API
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "application": "Supply Chain AI Assistant"
    }


# --------------------------------------------------
# 9. Login API
# --------------------------------------------------

@app.post("/login")
def login(request: LoginRequest):

    username = request.username.strip()

    role = authenticate_user(
        username,
        request.password
    )

    if not role:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        username,
        role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": username,
        "role": role
    }


# --------------------------------------------------
# 10. AI Chat API
# --------------------------------------------------

@app.post("/chat")
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    try:
        answer = rag.ask_question(
            request.question.strip()
        )

        return {
            "username": current_user.get("username"),
            "role": current_user.get("role"),
            "question": request.question,
            "answer": answer,
            "intent": rag.last_intent
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process question: {str(error)}"
        )


# --------------------------------------------------
# 11. Document Upload API
# --------------------------------------------------

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    warehouse: str = Form(...),
    region: str = Form(...),
    current_user: dict = Depends(get_current_user)
):

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
        ".xls"
    }

    filename = file.filename or "uploaded_file"
    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format"
        )

    safe_filename = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        with open(file_path, "wb") as output:
            output.write(content)

        metadata = {
            "warehouse": warehouse.strip().upper(),
            "region": region.strip(),
            "department": "General"
        }

        result = process_document(
            file_path,
            metadata=metadata
        )

        if result is False:
            raise HTTPException(
                status_code=500,
                detail="Document processing failed"
            )

        return {
            "message": "Document uploaded and processed successfully",
            "filename": safe_filename,
            "warehouse": metadata["warehouse"],
            "region": metadata["region"],
            "uploaded_by": current_user.get("username")
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )

    finally:
        await file.close()
