from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import enum

class ServiceType(str, enum.Enum):
    GROOMING = "grooming"
    MOPPING = "mopping"
    CLEANING_UTENSILS = "cleaning_utensils"
    PLUMBING = "plumbing"
    ELECTRICIAN ="electrician"
    GENERAL_CLEANING = "general_cleaning"
    DEEP_CLEANING = "deep cleaning"
    BATHROOM_CLEANING ="bathroom cleaning"
    KITCHEN_CLEANING="kitchen cleaning"
    HOURLY_BOOKING = "hourly_booking"
    SWEEPING_MOPPING = "sweeping_mopping"
    LAUNDRY = "laundry"
    WINDOW_CLEANING = "window_cleaning"
    PACKING_UNPACKING = "packing_unpacking"
    CAR_CLEANING = "car_cleaning"
    CARPENTRY = "carpentry"
    AC_REPAIR = "ac_repair"
    
class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CASH = "cash"
    NETBANKING = "netbanking"
    CARD = "card"

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    OWNER = "owner"
    GIG_WORKER = "gig_worker"
    ADMIN = "admin"

class ServiceRequestStatus(str, enum.Enum):
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum(ServiceType), index=True)
    description = Column(String)
    price = Column(Float)
    duration_hours = Column(Float)
    is_available = Column(Boolean, default=True)
    
    bookings = relationship("Booking", back_populates="service")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bookings = relationship("Booking", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    booking_date = Column(DateTime, index=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(String, nullable=True)
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)

class ServiceProvider(Base):
    __tablename__ = "service_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    specialization = Column(Enum(ServiceType))
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Float)
    currency = Column(String, default="usd")
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CARD)
    payment_reference = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    stripe_payment_intent_id = Column(String, unique=True, nullable=True)
    stripe_client_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="payment")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String)
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    alternate_mobile_number = Column(String)
    area = Column(String)
    locality = Column(String)
    apartment_no = Column(String)
    address = Column(String, nullable=True)
    expertise = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    service_requests = relationship("ServiceRequest", back_populates="user", foreign_keys="ServiceRequest.user_id")

class AuthOTP(Base):
    __tablename__ = "auth_otps_email"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    expires_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String)
    title = Column(String)
    description = Column(String)
    preferred_date = Column(DateTime, nullable=True)
    preferred_time = Column(String, nullable=True)  # e.g., "morning", "afternoon", "evening"
    urgency = Column(String, default="normal")  # "low", "normal", "high", "emergency"
    location = Column(String)
    contact_phone = Column(String)
    alternate_contact = Column(String, nullable=True)
    area = Column(String)
    locality = Column(String)
    apartment_no = Column(String, nullable=True)
    house_size = Column(String, nullable=True) # e.g., 1BHK, 2BHK
    car_size = Column(String, nullable=True)
    carpentry_size = Column(String, nullable=True)
    photo_data = Column(String, nullable=True) # Base64 encoded image
    additional_notes = Column(String, nullable=True)
    status = Column(Enum(ServiceRequestStatus), default=ServiceRequestStatus.PENDING)
    assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    estimated_price = Column(Float, nullable=True)
    arrival_otp = Column(String, nullable=True)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="service_requests", foreign_keys=[user_id])
    assigned_worker = relationship("User", foreign_keys=[assigned_worker_id])

    @property
    def worker_name(self):
        return self.assigned_worker.full_name if self.assigned_worker else None

    @property
    def worker_phone(self):
        return self.assigned_worker.mobile_number if self.assigned_worker else None

    @property
    def worker_expertise(self):
        return self.assigned_worker.expertise if self.assigned_worker else None

    @property
    def worker_rating(self):
        return self.assigned_worker.average_rating if self.assigned_worker else None


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

class AppReview(Base):
    __tablename__ = "app_reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
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
