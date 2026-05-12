from app.db.session import engine
import app.db.registry  # noqa — registers all models with Base
from app.db.base import Base

Base.metadata.create_all(bind=engine)
print("✔ Tables created (or already exist)")
