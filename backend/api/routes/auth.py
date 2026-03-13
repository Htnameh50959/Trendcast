from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from api.firebase_admin_init import get_firebase_app, get_db, verify_token
from firebase_admin import auth as firebase_auth

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    user: dict


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(req: SignUpRequest):
    try:
        get_firebase_app()
        user_record = firebase_auth.create_user(
            email=req.email,
            password=req.password,
            display_name=req.full_name or req.email.split("@")[0],
        )

        db = get_db()
        db.collection("users").document(user_record.uid).set({
            "id": user_record.uid,
            "email": req.email,
            "full_name": req.full_name or req.email.split("@")[0],
        })

        return AuthResponse(
            access_token="",
            user={
                "id": user_record.uid,
                "email": req.email,
                "full_name": req.full_name or req.email.split("@")[0],
            }
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        print("[auth.signup] exception:", repr(e))
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")


@router.post("/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    raise HTTPException(
        status_code=400,
        detail="Login is handled client-side via Firebase Auth. Use the Firebase SDK to sign in and obtain an ID token."
    )


@router.post("/auth/logout")
async def logout(request: Request):
    return {"message": "Logged out successfully"}


@router.get("/auth/me")
async def get_current_user(request: Request):
    try:
        token = getattr(request.state, "token", None)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            raise HTTPException(status_code=401, detail="No token provided")

        uid = verify_token(token)
        db = get_db()
        doc = db.collection("users").document(uid).get()

        if doc.exists:
            return {"user": doc.to_dict()}

        user_record = firebase_auth.get_user(uid)
        return {
            "user": {
                "id": uid,
                "email": user_record.email,
                "full_name": user_record.display_name or "",
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[auth.me] exception: {repr(e)}")
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_current_user_id(request: Request) -> str:
    token = getattr(request.state, "token", None)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        return verify_token(token)
    except Exception as e:
        print(f"[get_current_user_id] exception: {repr(e)}")
        raise HTTPException(status_code=401, detail="Unauthorized")
