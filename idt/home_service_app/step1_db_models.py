import re
import os
import sqlite3

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
models_path = os.path.join(app_dir, "models.py")
schemas_path = os.path.join(app_dir, "schemas.py")
db_path = os.path.join(app_dir, "home_service.db")

# 1. Update models.py
with open(models_path, "r", encoding="utf-8") as f:
    models_content = f.read()

new_models = """

# --- PHASE 1 MODELS ---

class PromoCode(Base):
    __tablename__ = "promo_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_percentage = Column(Integer, default=0)
    max_discount_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"))
    customer_id = Column(Integer, ForeignKey("users.id"))
    worker_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer, default=5) # 1 to 5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    free_services_count = Column(Integer, default=0)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    credits_remaining = Column(Integer, default=0)
    active_until = Column(DateTime(timezone=True))
"""

if "class PromoCode(Base):" not in models_content:
    models_content += new_models

# Add discount and final_price to ServiceRequest if not there
if "final_price =" not in models_content:
    # ServiceRequest model modification
    old_sr = """    estimated_price = Column(Float, nullable=True)
    assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)"""
    new_sr = """    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    promo_code = Column(String, nullable=True)
    assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)"""
    models_content = models_content.replace(old_sr, new_sr)

with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_content)

# 2. Update schemas.py
with open(schemas_path, "r", encoding="utf-8") as f:
    schemas_content = f.read()

new_schemas = """

# --- PHASE 1 SCHEMAS ---

class PromoValidateRequest(BaseModel):
    code: str
    amount: float

class ReviewCreate(BaseModel):
    request_id: int
    rating: int
    comment: Optional[str] = None

class SubscriptionBuyRequest(BaseModel):
    plan_id: int
"""
if "class PromoValidateRequest(BaseModel):" not in schemas_content:
    schemas_content += new_schemas

# Update ServiceRequestResponse
if "final_price: Optional[float] = None" not in schemas_content:
    schemas_content = schemas_content.replace(
        "estimated_price: Optional[float] = None",
        "estimated_price: Optional[float] = None\n    final_price: Optional[float] = None\n    promo_code: Optional[str] = None"
    )

with open(schemas_path, "w", encoding="utf-8") as f:
    f.write(schemas_content)


# 3. Alter existing SQLite Database to add new columns to ServiceRequest
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE service_requests ADD COLUMN final_price FLOAT;")
        cursor.execute("ALTER TABLE service_requests ADD COLUMN promo_code VARCHAR;")
        conn.commit()
    except sqlite3.OperationalError:
        # Columns likely already exist
        pass
    conn.close()

print("Models, schemas, and DB updated successfully.")
