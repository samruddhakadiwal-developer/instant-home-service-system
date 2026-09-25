from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import engine, get_db, Base
from models import (
    Service,
    Customer,
    Booking,
    ServiceProvider,
    ServiceType,
    BookingStatus,
    Payment,
    PaymentStatus,
    PaymentMethod,
    User,
    UserRole,
    AuthOTP,
    ServiceRequest,
    ServiceRequestStatus,
    PromoCode,
    Review,
    SubscriptionPlan,
    UserSubscription,
    AppReview,
)
from schemas import (
    ServiceCreate,
    ServiceResponse,
    CustomerCreate,
    CustomerResponse,
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    ServiceProviderCreate,
    ServiceProviderResponse,
    PaymentResponse,
    PaymentIntentCreate,
    OTPRequest,
    OTPVerify,
    CompleteRegistration,
    UserCreate,
    UserResponse,
    Token,
    TokenData,
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestResponse,
    PromoValidateRequest,
    ReviewCreate,
    SubscriptionBuyRequest,
    AppReviewCreate,
)

import stripe
try:
    from twilio.rest import Client
except ImportError:
    Client = None

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key_here")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_your_stripe_publishable_key_here")
stripe.api_key = STRIPE_SECRET_KEY

# Twilio SMS configuration (optional)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_ENABLED = all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, Client is not None])

# Email configuration (optional)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
EMAIL_ENABLED = all([SMTP_USERNAME, SMTP_PASSWORD])

# Authentication configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def send_otp_email(email: str, otp_code: str) -> bool:
    if not EMAIL_ENABLED:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "Your OTP Code - Home Service System"

        body = f"""
        Hello,

        Your OTP code for Home Service System is: {otp_code}

        This code expires in 5 minutes. Please use it to complete your authentication.

        If you didn't request this code, please ignore this email.

        Best regards,
        Home Service System Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, email, text)
        server.quit()

        print(f"Sent OTP email to {email}")
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Authentication utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.hashed_password:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()

def generate_otp_code() -> str:
    return f"{random.randint(100000, 999999)}"


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Home Service Application", version="1.0.0")

# Ensure static directory exists
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        # Maps request_id to a list of active websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, request_id: int):
        await websocket.accept()
        if request_id not in self.active_connections:
            self.active_connections[request_id] = []
        self.active_connections[request_id].append(websocket)

    def disconnect(self, websocket: WebSocket, request_id: int):
        if request_id in self.active_connections:
            if websocket in self.active_connections[request_id]:
                self.active_connections[request_id].remove(websocket)
            if not self.active_connections[request_id]:
                del self.active_connections[request_id]

    async def broadcast_location(self, request_id: int, message: dict):
        if request_id in self.active_connections:
            for connection in self.active_connections[request_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# ==================== FRONTEND ROUTES ====================

@app.get("/")
def get_dashboard():
    return FileResponse("dashboard.html")

@app.get("/dashboard/owner")
def get_owner_dashboard():
    return FileResponse("owner_dashboard.html")

@app.get("/dashboard/gig-worker")
def get_gig_worker_dashboard():
    return FileResponse("gig_worker_dashboard.html")

@app.get("/payment")
def get_payment():
    return FileResponse("payment.html")

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/request-otp")
def request_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Request an OTP for email login or registration"""
    email = otp_request.email.lower()
    if otp_request.role == UserRole.OWNER and email != "samruddhakadiwal@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to login as Owner")
        
    otp_code = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    auth_otp = AuthOTP(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False,
    )
    db.add(auth_otp)
    db.commit()
    db.refresh(auth_otp)

    print(f"\n{'='*40}")
    print(f"[SECURITY] DEVELOPMENT OTP CODE: {otp_code}")
    print(f"[EMAIL] For Email: {email}")
    print(f"{'='*40}\n")

    email_sent = send_otp_email(email, otp_code)

    message = "OTP generated. "
    if email_sent:
        message += "Sent via email to your email address."
    else:
        message += "Email delivery is not configured. Use the OTP code returned in the response."

    response_payload = {
        "email": email,
        "expires_at": expires_at.isoformat(),
        "message": message,
        "email_sent": email_sent,
        "otp_code": otp_code  # Force returning OTP for local development
    }
    
    return response_payload

@app.post("/auth/verify-otp")
def verify_otp(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and check if user exists"""
    email = otp_verify.email.lower()
    auth_record = db.query(AuthOTP).filter(
        AuthOTP.email == email,
        AuthOTP.otp_code == otp_verify.otp_code,
    ).order_by(AuthOTP.expires_at.desc()).first()

    if not auth_record or auth_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    auth_record.is_verified = True
    db.commit()

    user = get_user_by_email(db, email)
    if user:
        if user.role == UserRole.OWNER and user.email.lower() != "samruddhakadiwal@gmail.com":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to login as Owner")
            
        # Existing user - login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user_exists": True}
    else:
        # New user - needs registration
        return {"user_exists": False, "message": "OTP verified. Please provide your details to complete registration."}

@app.post("/auth/complete-registration", response_model=Token)
def complete_registration(registration: CompleteRegistration, db: Session = Depends(get_db)):
    """Complete registration for new user after OTP verification"""
    email = registration.email.lower()
    if registration.role == UserRole.OWNER and email != "samruddhakadiwal@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to register as Owner")
        
    # Check if OTP was verified recently
    auth_record = db.query(AuthOTP).filter(
        AuthOTP.email == email,
        AuthOTP.is_verified == True,
    ).order_by(AuthOTP.expires_at.desc()).first()

    if not auth_record or auth_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP verification expired. Please request a new OTP.")

    # Check if user already exists
    existing_user = get_user_by_email(db, registration.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    # Check if mobile number already exists
    if registration.mobile_number:
        existing_mobile = db.query(User).filter(User.mobile_number == registration.mobile_number).first()
        if existing_mobile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number already in use by another user")

    username = f"{registration.role.value}_{registration.email.split('@')[0]}"
    if db.query(User).filter(User.username == username).first():
        username = f"{username}_{random.randint(100, 999)}"

    user = User(
        email=registration.email,
        username=username,
        hashed_password=None,
        full_name=registration.full_name,
        mobile_number=registration.mobile_number,
        alternate_mobile_number=None,
        area=registration.area,
        locality=registration.locality,
        apartment_no=registration.apartment_no,
        address=registration.address,
        expertise=registration.expertise,
        role=registration.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# ==================== SERVICE PRICING ====================

SERVICE_PRICES = {
    "grooming": 149.0,
    "mopping": 99.0,
    "cleaning_utensils": 99.0,
    "plumbing": 149.0,
    "electrician": 149.0,
    "general_cleaning": 199.0,
    "deep cleaning": 399.0,
    "bathroom cleaning": 149.0,
    "kitchen cleaning": 149.0,
    "hourly_booking": 99.0,
    "sweeping_mopping": 99.0,
    "laundry": 149.0,
    "window_cleaning": 149.0,
    "packing_unpacking": 299.0,
    "car_cleaning": 149.0,
    "carpentry": 199.0,
    "ac_repair": 299.0,
}

# ==================== SERVICE REQUEST ENDPOINTS ====================

@app.post("/service-requests/", response_model=ServiceRequestResponse)
def create_service_request(
    request: ServiceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new service request with auto-assignment and pricing"""
    # Auto-assign to a matching available gig worker
    service_type_str = request.service_type.value if hasattr(request.service_type, 'value') else str(request.service_type)
    
    # Dictionary of synonyms to match worker expertise flexibly
    EXPERTISE_SYNONYMS = {
        "plumbing": ["plumber", "plumbing", "pipe", "leak", "drain"],
        "electrician": ["electrician", "electrical", "wire", "wiring"],
        "cleaning_utensils": ["maid", "cleaner", "utensil", "washing"],
        "general_cleaning": ["cleaner", "maid", "sweeping", "cleaning"],
        "deep cleaning": ["cleaner", "maid", "deep"],
        "bathroom cleaning": ["cleaner", "maid", "bathroom"],
        "kitchen cleaning": ["cleaner", "maid", "kitchen"],
        "car_cleaning": ["car wash", "car cleaner", "detailing"],
        "carpentry": ["carpenter", "carpentry", "wood"],
        "ac_repair": ["ac technician", "ac repair", "hvac", "cooling"],
        "mopping": ["cleaner", "maid", "mopping", "sweeping"],
        "grooming": ["groomer", "salon", "beautician", "hair", "spa"],
        "laundry": ["washer", "laundry", "dry clean", "ironing"],
        "window_cleaning": ["cleaner", "window cleaner", "glass"],
        "packing_unpacking": ["packer", "mover", "packing", "shifting"],
    }
    
    # Extract the first service to try to auto-assign a worker
    first_service = [s.strip().lower() for s in service_type_str.split(',')][0] if service_type_str else ""
    
    # Get keywords for this service, falling back to the service name itself
    keywords = EXPERTISE_SYNONYMS.get(first_service, [first_service])
    if first_service and first_service not in keywords:
        keywords.append(first_service)
        
    # Build OR conditions for all keywords
    conditions = [User.expertise.ilike(f"%{kw}%") for kw in keywords]
    
    if conditions:
        capable_workers = db.query(User).filter(
            User.role == UserRole.GIG_WORKER,
            or_(*conditions)
        ).all()
    else:
        capable_workers = []
    
    assigned_worker = None
    if capable_workers:
        # Load balance: pick the worker with the fewest active jobs
        min_jobs = float('inf')
        for worker in capable_workers:
            active_jobs_count = db.query(ServiceRequest).filter(
                ServiceRequest.assigned_worker_id == worker.id,
                ServiceRequest.status.in_([ServiceRequestStatus.ASSIGNED, ServiceRequestStatus.IN_PROGRESS])
            ).count()
            
            if active_jobs_count < min_jobs:
                min_jobs = active_jobs_count
                assigned_worker = worker

    status = ServiceRequestStatus.ASSIGNED if assigned_worker else ServiceRequestStatus.PENDING
    assigned_worker_id = assigned_worker.id if assigned_worker else None

    # Calculate price based on house size and multiple services
    services_list = [s.strip() for s in service_type_str.split(',')]
    total_base_price = 0.0
    
    size_multiplier = 1.0
    if request.house_size:
        size_multiplier = {
            "1BHK": 1.0,
            "2BHK": 1.5,
            "3BHK": 2.0,
            "4BHK+": 2.5,
            "Villa": 3.0
        }.get(request.house_size, 1.0)
        
    for s_type in services_list:
        p = SERVICE_PRICES.get(s_type, 50.0)
        # Fixed price for specific services (no BHK multiplier)
        if s_type in ['carpentry', 'ac_repair', 'electrician']:
            total_base_price += p
        else:
            total_base_price += (p * size_multiplier)

    final_price = request.estimated_price if request.estimated_price is not None else total_base_price

    db_request = ServiceRequest(
        user_id=current_user.id,
        service_type=request.service_type,
        title=request.title,
        description=request.description,
        preferred_date=request.preferred_date,
        preferred_time=request.preferred_time,
        urgency=request.urgency,
        location=request.location,
        contact_phone=request.contact_phone,
        alternate_contact=request.alternate_contact,
        area=request.area,
        locality=request.locality,
        apartment_no=request.apartment_no,
        house_size=request.house_size,
        additional_notes=request.additional_notes,
        estimated_price=final_price,
        status=status,
        assigned_worker_id=assigned_worker_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Send email notification if worker was auto-assigned
    if assigned_worker and assigned_worker.email:
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        if sender_email and sender_password:
            try:
                from email.mime.multipart import MIMEMultipart as MM
                from email.mime.text import MIMEText as MT
                msg = MM()
                msg['From'] = sender_email
                msg['To'] = assigned_worker.email
                msg['Subject'] = f"New Job Assigned: {request.title}"
                body = f"Hello {assigned_worker.full_name},\n\nYou have been assigned a new service request:\n\nService: {service_type_str}\nTitle: {request.title}\nLocation: {request.location}\nEstimated Price: \u20b9{final_price:.0f}\nHouse Size: {request.house_size or 'Not specified'}\n\nPlease check your Gig Worker dashboard for details.\n\nThank you!"
                msg.attach(MT(body, 'plain'))
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
                print(f"Assignment email sent to {assigned_worker.email}")
            except Exception as e:
                print(f"Failed to send assignment email: {e}")

    return db_request

@app.get("/service-requests/", response_model=list[ServiceRequestResponse])
def get_service_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get service requests for the current user role"""
    if current_user.role in [UserRole.ADMIN, UserRole.OWNER]:
        return db.query(ServiceRequest).offset(skip).limit(limit).all()
    if current_user.role == UserRole.GIG_WORKER:
        all_worker_reqs = db.query(ServiceRequest).filter(
            or_(
                ServiceRequest.assigned_worker_id == current_user.id,
                and_(ServiceRequest.status == ServiceRequestStatus.PENDING, ServiceRequest.assigned_worker_id == None)
            )
        ).all()
        
        filtered_reqs = []
        worker_expertise = (current_user.expertise or "").lower()
        worker_words = [w.strip() for w in worker_expertise.replace(',', ' ').split() if len(w.strip()) > 3]
        
        for req in all_worker_reqs:
            if req.status == ServiceRequestStatus.PENDING and req.assigned_worker_id is None:
                if not worker_expertise:
                    # If worker hasn't set expertise, do not show any jobs.
                    # They must set their expertise in the profile first.
                    continue
                    
                req_types = [s.strip().lower() for s in (req.service_type or "").split(",")]
                matched = False
                for t in req_types:
                    if not t: continue
                    if t in worker_expertise or worker_expertise in t:
                        matched = True
                        break
                    for w in worker_words:
                        if w in t or t in w:
                            matched = True
                            break
                    if matched: break
                
                if matched:
                    filtered_reqs.append(req)
            else:
                filtered_reqs.append(req)
        return filtered_reqs[skip:skip+limit]
    return db.query(ServiceRequest).filter(ServiceRequest.user_id == current_user.id).offset(skip).limit(limit).all()

@app.get("/service-requests/{request_id}", response_model=ServiceRequestResponse)
def get_service_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get service request by ID"""
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    # Users can only see their own requests, admins and owners can see all, and gig workers can view assigned requests
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER] and request.user_id != current_user.id and request.assigned_worker_id != current_user.id:
        if current_user.role == UserRole.GIG_WORKER and request.status == ServiceRequestStatus.PENDING and request.assigned_worker_id is None:
            pass # Allow gig workers to view pending requests
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view this request")
    
    return request

@app.put("/service-requests/{request_id}", response_model=ServiceRequestResponse)
def update_service_request(
    request_id: int,
    request_update: ServiceRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update service request (admin only for status updates)"""
    db_request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    is_gig_worker_accepting = (
        current_user.role == UserRole.GIG_WORKER and
        db_request.status == ServiceRequestStatus.PENDING and
        db_request.assigned_worker_id is None and
        request_update.status == ServiceRequestStatus.ASSIGNED and
        request_update.assigned_worker_id == current_user.id
    )
    
    is_gig_worker_updating_own_job = (
        current_user.role == UserRole.GIG_WORKER and
        db_request.assigned_worker_id == current_user.id and
        request_update.status in [ServiceRequestStatus.IN_PROGRESS, ServiceRequestStatus.COMPLETED]
    )
    
    is_customer_paying = (
        current_user.role == UserRole.CUSTOMER and
        db_request.user_id == current_user.id and
        request_update.is_paid == True
    )

    if request_update.status or request_update.assigned_worker_id is not None or request_update.estimated_price is not None or request_update.is_paid is not None:
        if current_user.role not in [UserRole.ADMIN, UserRole.OWNER] and not is_gig_worker_accepting and not is_gig_worker_updating_own_job and not is_customer_paying:
            raise HTTPException(status_code=403, detail="Not authorized to update request status")
    
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER] and db_request.user_id != current_user.id and not is_gig_worker_accepting and not is_gig_worker_updating_own_job:
        raise HTTPException(status_code=403, detail="Not authorized to update this request")
    
    for key, value in request_update.dict(exclude_unset=True).items():
        setattr(db_request, key, value)
    
    db_request.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_request)
    return db_request

@app.delete("/service-requests/{request_id}")
def delete_service_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete service request"""
    db_request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    # Users can only delete their own requests; admins and owners can delete any
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER] and db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this request")
    
    db.delete(db_request)
    db.commit()
    return {"message": "Service request deleted successfully"}

# ==================== ADMIN DASHBOARD ENDPOINTS ====================

@app.get("/admin/dashboard")
def get_admin_dashboard(current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    total_users = db.query(User).count()
    total_requests = db.query(ServiceRequest).count()
    pending_requests = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceRequestStatus.PENDING).count()
    completed_requests = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceRequestStatus.COMPLETED).count()
    
    return {
        "total_users": total_users,
        "total_service_requests": total_requests,
        "pending_requests": pending_requests,
        "completed_requests": completed_requests
    }

@app.get("/admin/users", response_model=list[UserResponse])
def get_all_users(current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    return db.query(User).all()

# ==================== SERVICES ENDPOINTS ====================

@app.post("/services/", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Create a new service"""
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.get("/services/", response_model=list[ServiceResponse])
def get_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all services"""
    return db.query(Service).offset(skip).limit(limit).all()

@app.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get service by ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@app.get("/services/type/{service_type}", response_model=list[ServiceResponse])
def get_services_by_type(service_type: ServiceType, db: Session = Depends(get_db)):
    """Get services by type (grooming, mopping, plumbing, electrician, etc.)"""
    return db.query(Service).filter(Service.type == service_type).all()

@app.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    """Update a service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    for key, value in service.dict().items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Delete a service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    db.delete(db_service)
    db.commit()
    return {"message": "Service deleted successfully"}

# ==================== CUSTOMERS ENDPOINTS ====================

@app.post("/customers/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    db_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers/", response_model=list[CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers"""
    return db.query(Customer).offset(skip).limit(limit).all()

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    """Update customer information"""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    for key, value in customer.dict().items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# ==================== BOOKINGS ENDPOINTS ====================

@app.post("/bookings/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """Create a new booking"""
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    # Validate service exists
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    if not service.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service is not available")
    
    db_booking = Booking(
        customer_id=booking.customer_id,
        service_id=booking.service_id,
        booking_date=booking.booking_date,
        notes=booking.notes,
        total_price=service.price,
        status=BookingStatus.PENDING
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=list[BookingResponse])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all bookings"""
    return db.query(Booking).offset(skip).limit(limit).all()

@app.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get booking by ID"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking

@app.get("/customers/{customer_id}/bookings", response_model=list[BookingResponse])
def get_customer_bookings(customer_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return db.query(Booking).filter(Booking.customer_id == customer_id).all()

@app.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    """Update booking status"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    db_booking.status = booking_update.status
    if booking_update.notes:
        db_booking.notes = booking_update.notes
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancel a booking"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    db_booking.status = BookingStatus.CANCELLED
    db.commit()
    return {"message": "Booking cancelled successfully"}

# ==================== PAYMENT ENDPOINTS ====================

@app.post("/payments/create-intent", response_model=dict)
def create_payment_intent(payment_intent: PaymentIntentCreate, db: Session = Depends(get_db)):
    """Create a payment record for a booking and optionally create a Stripe payment intent"""
    booking = db.query(Booking).filter(Booking.id == payment_intent.booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    existing_payment = db.query(Payment).filter(Payment.booking_id == payment_intent.booking_id).first()
    if existing_payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already exists for this booking")
    
    if payment_intent.payment_method != PaymentMethod.CARD:
        db_payment = Payment(
            booking_id=booking.id,
            amount=booking.total_price,
            currency="usd",
            payment_method=payment_intent.payment_method,
            status=PaymentStatus.PENDING,
            payment_reference=payment_intent.upi_id if payment_intent.payment_method == PaymentMethod.UPI else None,
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        message = "Payment recorded. Please complete the transaction using the selected method."
        if payment_intent.payment_method == PaymentMethod.UPI and payment_intent.upi_id:
            message = f"UPI payment requested. Please transfer payment to UPI ID {payment_intent.upi_id}."
        elif payment_intent.payment_method == PaymentMethod.CASH:
            message = "Cash payment selected. Please pay the provider in person at service delivery."
        elif payment_intent.payment_method == PaymentMethod.NETBANKING:
            message = "Netbanking selected. Please transfer the amount using your bank’s netbanking facility."

        return {
            "payment_id": db_payment.id,
            "amount": booking.total_price,
            "currency": "usd",
            "payment_method": payment_intent.payment_method,
            "message": message,
        }

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(booking.total_price * 100),
            currency="usd",
            metadata={"booking_id": str(booking.id)}
        )

        db_payment = Payment(
            booking_id=booking.id,
            amount=booking.total_price,
            currency="usd",
            payment_method=PaymentMethod.CARD,
            status=PaymentStatus.PENDING,
            stripe_payment_intent_id=intent.id,
            stripe_client_secret=intent.client_secret,
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return {
            "client_secret": intent.client_secret,
            "payment_id": db_payment.id,
            "amount": booking.total_price,
            "currency": "usd",
            "payment_method": PaymentMethod.CARD,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment intent creation failed: {str(e)}")

@app.post("/payments/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for payment status updates"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature (you should set up webhook endpoint secret)
        # event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        # For now, we'll trust the payload (in production, verify signature)
        import json
        event = json.loads(payload)
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            booking_id = payment_intent['metadata']['booking_id']
            
            # Update payment status
            payment = db.query(Payment).filter(
                Payment.stripe_payment_intent_id == payment_intent['id']
            ).first()
            
            if payment:
                payment.status = PaymentStatus.COMPLETED
                # Update booking status
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking:
                    booking.status = BookingStatus.CONFIRMED
                db.commit()
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment = db.query(Payment).filter(
                Payment.stripe_payment_intent_id == payment_intent['id']
            ).first()
            
            if payment:
                payment.status = PaymentStatus.FAILED
                db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Webhook error: {str(e)}")

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get payment details by ID"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment

@app.get("/bookings/{booking_id}/payment", response_model=PaymentResponse)
def get_booking_payment(booking_id: int, db: Session = Depends(get_db)):
    """Get payment for a specific booking"""
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found for this booking")
    return payment

# ==================== SERVICE PROVIDERS ENDPOINTS ====================

@app.post("/providers/", response_model=ServiceProviderResponse)
def create_provider(provider: ServiceProviderCreate, db: Session = Depends(get_db)):
    """Create a new service provider"""
    db_provider = db.query(ServiceProvider).filter(ServiceProvider.email == provider.email).first()
    if db_provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    db_provider = ServiceProvider(**provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@app.get("/providers/", response_model=list[ServiceProviderResponse])
def get_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all service providers"""
    return db.query(ServiceProvider).offset(skip).limit(limit).all()

@app.get("/providers/{provider_id}", response_model=ServiceProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get provider by ID"""
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return provider

@app.get("/providers/specialization/{specialization}", response_model=list[ServiceProviderResponse])
def get_providers_by_specialization(specialization: ServiceType, db: Session = Depends(get_db)):
    """Get providers by specialization"""
    return db.query(ServiceProvider).filter(
        ServiceProvider.specialization == specialization,
        ServiceProvider.is_available == True
    ).all()

@app.put("/providers/{provider_id}", response_model=ServiceProviderResponse)
def update_provider(provider_id: int, provider: ServiceProviderCreate, db: Session = Depends(get_db)):
    """Update provider information"""
    db_provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    
    for key, value in provider.dict().items():
        setattr(db_provider, key, value)
    db.commit()
    db.refresh(db_provider)
    return db_provider

# ==================== GIG WORKER ENDPOINTS ====================

@app.get("/gig-workers/", response_model=list[UserResponse])
def get_gig_workers(db: Session = Depends(get_db)):
    """Get all gig workers"""
    return db.query(User).filter(User.role == "gig_worker").all()

@app.get("/gig-workers/{worker_id}", response_model=UserResponse)
def get_gig_worker(worker_id: int, db: Session = Depends(get_db)):
    """Get gig worker by ID"""
    worker = db.query(User).filter(User.id == worker_id, User.role == "gig_worker").first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gig worker not found")
    return worker

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile"""
    # Only allow users to update their own profile or admins to update anyone
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update only allowed fields
    allowed_fields = ['full_name', 'mobile_number', 'expertise', 'area', 'locality', 'address', 'alternate_mobile_number']
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# ==================== TRACKING & OTP ENDPOINTS ====================

@app.websocket("/ws/tracking/{request_id}")
async def websocket_tracking(websocket: WebSocket, request_id: int):
    await manager.connect(websocket, request_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast the received location data to everyone listening on this request_id
            await manager.broadcast_location(request_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, request_id)

@app.post("/service-requests/{request_id}/arrive")
def worker_arrived(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    if request.assigned_worker_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this request")

    # Generate OTP
    otp_code = str(random.randint(1000, 9999))
    request.arrival_otp = otp_code
    db.commit()
    
    print(f"\n{'='*40}")
    print(f"[SECURITY] ARRIVAL OTP FOR REQUEST {request_id}: {otp_code}")
    print(f"{'='*40}\n")
    
    # Send email to the customer
    customer = request.user
    if customer and customer.email:
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        if sender_email and sender_password:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = customer.email
                msg['Subject'] = f"Your Gig Worker has Arrived! OTP: {otp_code}"
                
                body = f"Hello {customer.full_name},\n\nYour assigned worker has arrived at the location. Please provide them with the following OTP to verify their arrival and start the job:\n\nOTP: {otp_code}\n\nThank you for using Home Service Application."
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(f"Failed to send email: {e}")
                
    return {"message": "Arrival OTP generated and sent to customer"}

@app.post("/service-requests/{request_id}/verify-arrival")
def verify_worker_arrival(request_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    if request.assigned_worker_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this request")
        
    otp_code = payload.get("otp_code")
    if not otp_code or request.arrival_otp != otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    # Successfully verified, update status
    request.status = ServiceRequestStatus.IN_PROGRESS
    request.arrival_otp = None # Clear the OTP
    db.commit()
    
    return {"message": "Arrival verified. Job is now in progress."}

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_customers = db.query(Customer).count()
    total_services = db.query(Service).count()
    total_providers = db.query(ServiceProvider).count()
    pending_bookings = db.query(Booking).filter(Booking.status == BookingStatus.PENDING).count()
    completed_bookings = db.query(Booking).filter(Booking.status == BookingStatus.COMPLETED).count()
    
    return {
        "total_customers": total_customers,
        "total_services": total_services,
        "total_providers": total_providers,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings
    }

@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Home Service Application",
        "version": "1.0.0",
        "services": ["grooming", "mopping", "cleaning_utensils", "plumbing", "electrician"],
        "payment_page": "/payment",
        "user_dashboard": "/dashboard/user",
        "owner_dashboard": "/dashboard/owner",
        "gig_worker_dashboard": "/dashboard/gig-worker"
    }

@app.get("/payment")
def payment_page():
    """Serve the payment page"""
    return FileResponse("payment.html", media_type="text/html")

@app.get("/dashboard")
def dashboard_page():
    """Serve the user dashboard page"""
    return FileResponse("dashboard.html", media_type="text/html")

@app.get("/login")
def login_page():
    """Serve the login page (dashboard.html) with fresh cache"""
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    return FileResponse("dashboard.html", media_type="text/html", headers=headers)

@app.get("/dashboard/user")
def user_dashboard_page():
    """Serve the customer dashboard page"""
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    return FileResponse("user_dashboard.html", media_type="text/html", headers=headers)

@app.get("/dashboard/owner")
def owner_dashboard_page():
    """Serve the owner dashboard page"""
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    return FileResponse("owner_dashboard.html", media_type="text/html", headers=headers)

@app.get("/dashboard/gig-worker")
def gig_worker_dashboard_page():
    """Serve the gig worker dashboard page"""
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    return FileResponse("gig_worker_dashboard.html", media_type="text/html", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

# ==================== PHASE 1 ENDPOINTS ====================

@app.post("/promos/validate")
def validate_promo(request: PromoValidateRequest, db: Session = Depends(get_db)):
    # Hardcode a demo promo for now if DB is empty
    if request.code.upper() == "FIRST50":
        discount = request.amount * 0.50
        return {"valid": True, "discount_amount": min(discount, 500.0)} # Max ₹500 off
    
    promo = db.query(PromoCode).filter(PromoCode.code == request.code, PromoCode.is_active == True).first()
    if not promo:
        raise HTTPException(status_code=400, detail="Invalid or expired promo code")
    
    discount = (promo.discount_percentage / 100.0) * request.amount
    if promo.max_discount_amount > 0:
        discount = min(discount, promo.max_discount_amount)
        
    return {"valid": True, "discount_amount": discount}

@app.post("/reviews/")
def submit_review(review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can submit reviews")
        
    request = db.query(ServiceRequest).filter(ServiceRequest.id == review.request_id, ServiceRequest.user_id == current_user.id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    if request.status != ServiceRequestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed requests")
        
    new_review = Review(
        request_id=request.id,
        customer_id=current_user.id,
        worker_id=request.assigned_worker_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    
    # Update worker's average rating
    if request.assigned_worker_id:
        worker = db.query(User).filter(User.id == request.assigned_worker_id).first()
        if worker:
            current_total = worker.average_rating * worker.total_reviews if worker.total_reviews else 0
            worker.total_reviews += 1
            worker.average_rating = (current_total + review.rating) / worker.total_reviews
            db.add(worker)
            
    db.commit()
    return {"message": "Review submitted successfully"}

@app.post("/app-reviews/")
def submit_app_review(review: AppReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_app_review = AppReview(
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_app_review)
    db.commit()
    return {"message": "App feedback submitted successfully"}

@app.post("/subscriptions/buy")
def buy_subscription(sub: SubscriptionBuyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simplified mock purchase
    new_sub = UserSubscription(
        user_id=current_user.id,
        plan_id=sub.plan_id,
        credits_remaining=4 # Mock: 4 free services
    )
    db.add(new_sub)
    db.commit()
    return {"message": "Subscription purchased successfully"}
