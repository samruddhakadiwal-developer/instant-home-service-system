try:
	from sqlalchemy import create_engine
	from sqlalchemy.orm import sessionmaker, declarative_base
except Exception:
	# Fallback stubs when SQLAlchemy is not installed (lets the file be imported/analyzed)
	def create_engine(*args, **kwargs):
		return None

	def sessionmaker(bind=None):
		def _session():
			return None
		return _session

	def declarative_base():
		class _Base:
			pass
		return _Base

DATABASE_URL = "sqlite:///./home_service.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()