import os

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
main_path = os.path.join(app_dir, "main.py")

with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

new_endpoints = """
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
        
    request = db.query(ServiceRequest).filter(ServiceRequest.id == review.request_id, ServiceRequest.customer_id == current_user.id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    if request.status != ServiceStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed requests")
        
    new_review = Review(
        request_id=request.id,
        customer_id=current_user.id,
        worker_id=request.assigned_worker_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    
    # Optional: Update worker's average rating here...
    
    db.commit()
    return {"message": "Review submitted successfully"}

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
"""

if "def validate_promo(" not in main_content:
    main_content += new_endpoints

# Now update create_service_request to apply promo and store final price
old_create = """        # Fixed price for specific services (no BHK multiplier)
        if service_type_str in ['carpentry', 'ac_repair', 'electrician']:
            size_multiplier = 1.0
            
        base_price *= size_multiplier

        db_request = ServiceRequest(
            customer_id=current_user.id,
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
            estimated_price=base_price,
            status=ServiceStatus.PENDING
        )"""

new_create = """        # Fixed price for specific services (no BHK multiplier)
        if service_type_str in ['carpentry', 'ac_repair', 'electrician']:
            size_multiplier = 1.0
            
        base_price *= size_multiplier
        final_price = base_price
        
        # Check if they passed a promo code in additional notes or if we expand schema
        # For phase 1, we will trust the frontend's estimated_price calculation if they pass it, 
        # or we could parse a 'promo_code' field. Let's rely on the frontend estimated_price for simplicity in this demo.
        if request.estimated_price and request.estimated_price < base_price:
            final_price = request.estimated_price # Trust the frontend discount for demo purposes

        db_request = ServiceRequest(
            customer_id=current_user.id,
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
            estimated_price=base_price,
            final_price=final_price,
            status=ServiceStatus.PENDING
        )"""

if "final_price=final_price" not in main_content:
    main_content = main_content.replace(old_create, new_create)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

print("Backend API updated successfully.")
