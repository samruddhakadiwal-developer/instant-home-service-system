from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import ServiceType, BookingStatus, PaymentStatus, PaymentMethod, UserRole, ServiceRequestStatus

class ServiceCreate(BaseModel):
    name: str
    type: ServiceType
    description: str
    price: float
    duration_hours: float
    is_available: bool = True

class ServiceResponse(ServiceCreate):
    id: int
    
    class Config:
        from_attributes = True

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str

class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    customer_id: int
    service_id: int
    booking_date: datetime
    notes: Optional[str] = None

class BookingUpdate(BaseModel):
    status: BookingStatus
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    customer_id: int
    service_id: int
    booking_date: datetime
    status: BookingStatus
    notes: Optional[str]
    total_price: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceProviderCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    specialization: ServiceType
    is_available: bool = True

class ServiceProviderResponse(ServiceProviderCreate):
    id: int
    rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    currency: str = "usd"

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    currency: str
    payment_method: PaymentMethod
    payment_reference: Optional[str]
    status: PaymentStatus
    stripe_client_secret: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentIntentCreate(BaseModel):
    booking_id: int
    payment_method: PaymentMethod
    upi_id: Optional[str] = None

class OTPRequest(BaseModel):
    email: EmailStr
    role: UserRole

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str

class CompleteRegistration(BaseModel):
    email: EmailStr
    full_name: str
    mobile_number: str
    area: str
    locality: str
    apartment_no: str
    address: str
    expertise: Optional[str] = None
    role: UserRole

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    mobile_number: Optional[str] = None
    alternate_mobile_number: Optional[str] = None
    area: str
    locality: str
    apartment_no: str
    address: str
    expertise: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    mobile_number: Optional[str]
    alternate_mobile_number: Optional[str]
    area: Optional[str]
    locality: Optional[str]
    apartment_no: Optional[str]
    address: Optional[str]
    expertise: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ServiceRequestCreate(BaseModel):
    service_type: str
    title: str
    description: str
    preferred_date: Optional[datetime] = None
    preferred_time: Optional[str] = None
    urgency: str = "normal"
    location: str
    contact_phone: str
    alternate_contact: str
    area: str
    locality: str
    apartment_no: str
    house_size: Optional[str] = None
    car_size: Optional[str] = None
    carpentry_size: Optional[str] = None
    photo_data: Optional[str] = None
    additional_notes: Optional[str] = None
    estimated_price: Optional[float] = None
    final_price: Optional[float] = None
    promo_code: Optional[str] = None

class ServiceRequestUpdate(BaseModel):
    status: Optional[ServiceRequestStatus] = None
    assigned_worker_id: Optional[int] = None
    estimated_price: Optional[float] = None
    final_price: Optional[float] = None
    promo_code: Optional[str] = None
    is_paid: Optional[bool] = None

class ServiceRequestResponse(BaseModel):
    id: int
    user_id: int
    service_type: str
    title: str
    description: str
    preferred_date: Optional[datetime]
    preferred_time: Optional[str]
    urgency: str
    location: str
    contact_phone: str
    alternate_contact: Optional[str]
    area: Optional[str]
    locality: Optional[str]
    apartment_no: Optional[str]
    house_size: Optional[str]
    car_size: Optional[str] = None
    carpentry_size: Optional[str] = None
    photo_data: Optional[str] = None
    additional_notes: Optional[str]
    status: ServiceRequestStatus
    assigned_worker_id: Optional[int]
    worker_name: Optional[str] = None
    worker_phone: Optional[str] = None
    worker_expertise: Optional[str] = None
    worker_rating: Optional[float] = None
    estimated_price: Optional[float]
    arrival_otp: Optional[str] = None
    is_paid: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# --- PHASE 1 SCHEMAS ---

class PromoValidateRequest(BaseModel):
    code: str
    amount: float

class ReviewCreate(BaseModel):
    request_id: int
    rating: int
    comment: Optional[str] = None

class AppReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class SubscriptionBuyRequest(BaseModel):
    plan_id: int
