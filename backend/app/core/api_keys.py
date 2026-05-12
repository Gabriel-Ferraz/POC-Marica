import hashlib

from fastapi import Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import hash_secret_key


async def validate_api_keys(
    request: Request,
    x_access_key: str = Header(..., alias="X-Access-Key"),
    x_secret_key: str = Header(..., alias="X-Secret-Key"),
):
    from app.db.session import SessionLocal
    from app.models.dlt import DLTCredential

    db: Session = SessionLocal()
    try:
        cred = db.query(DLTCredential).filter(
            DLTCredential.access_key == x_access_key,
            DLTCredential.is_active == True,
        ).first()

        if not cred:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API credentials")

        if cred.secret_key_hash != hash_secret_key(x_secret_key):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API credentials")

        route_path = request.url.path
        allowed = any(route_path.startswith(p) for p in (cred.allowed_routes or []))
        if cred.allowed_routes and not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Route not permitted for this key")

        return cred
    finally:
        db.close()
