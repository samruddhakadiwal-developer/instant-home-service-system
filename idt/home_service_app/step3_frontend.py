import re
import os

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
dash_path = os.path.join(app_dir, "dashboard.html")

with open(dash_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Subscriptions Tab
if '<div class="tab" onclick="showDashboardTab(\'subscriptions\')">Subscriptions</div>' not in content:
    content = content.replace(
        '<div class="tab" onclick="showDashboardTab(\'new-request\')">New Request</div>',
        '<div class="tab" onclick="showDashboardTab(\'new-request\')">New Request</div>\n                <div class="tab" onclick="showDashboardTab(\'subscriptions\')">Subscriptions</div>'
    )

# 2. Add Promo Code input to Price Summary
promo_html = """                    <!-- Dynamic Price Summary -->
                    <div class="price-summary" id="price-summary" style="display:none; flex-direction:column; gap:12px;">
                        <div style="display:flex; justify-content:space-between; width:100%;">
                            <div>
                                <div class="price-label">Estimated Price</div>
                                <div class="price-note" id="price-breakdown">Base rate</div>
                            </div>
                            <div class="price-value" id="estimated-price-display">₹0</div>
                        </div>
                        
                        <div style="display:flex; gap:10px; width:100%; border-top:1px solid rgba(0,0,0,0.05); padding-top:12px;">
                            <input type="text" id="promo-code" placeholder="Have a Promo Code?" style="flex:1; padding:8px 12px; border-radius:8px; border:1px solid #ddd; outline:none;">
                            <button onclick="applyPromoCode()" style="padding:8px 16px; border-radius:8px; background:var(--primary); color:white; font-weight:600; cursor:pointer;">Apply</button>
                        </div>
                        <div id="promo-message" style="font-size:12px; font-weight:600;"></div>
                    </div>"""
content = re.sub(
    r'<div class="price-summary" id="price-summary".*?</div>\s*</div>',
    promo_html,
    content,
    flags=re.DOTALL
)

# 3. Add Rating Modal and Subscriptions Section
extra_sections_html = """
            <!-- Subscriptions Section -->
            <div id="subscriptions-section" style="display: none;">
                <h2>Home Care Subscriptions</h2>
                <div class="section-card" style="text-align:center; background: linear-gradient(135deg, #fef3c7, #fde68a); border-color:#fbbf24;">
                    <h3 style="color:#b45309; font-size:24px; margin-bottom:10px;">Monthly Cleaning Pro 🧹</h3>
                    <p style="color:#92400e; margin-bottom:20px;">Get 4 free cleaning services every month. Priority support and zero surge pricing!</p>
                    <div style="font-size:32px; font-weight:800; color:#b45309; margin-bottom:20px;">₹999 <span style="font-size:14px; font-weight:500;">/ month</span></div>
                    <button onclick="buySubscription(1)" style="background:#b45309; color:white; padding:12px 30px; font-size:16px; border-radius:30px;">Subscribe Now</button>
                </div>
            </div>
            
            <!-- Rating Modal Overlay -->
            <div id="rating-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
                <div class="section-card" style="background:white; max-width:400px; width:90%; padding:30px; text-align:center;">
                    <h2 style="margin-bottom:10px;">Rate Your Service</h2>
                    <p style="color:var(--text-light); margin-bottom:20px;">How was your experience with the professional?</p>
                    
                    <div id="star-rating" style="font-size:36px; color:#ddd; cursor:pointer; margin-bottom:20px; display:flex; justify-content:center; gap:10px;">
                        <span onclick="setRating(1)">★</span><span onclick="setRating(2)">★</span><span onclick="setRating(3)">★</span><span onclick="setRating(4)">★</span><span onclick="setRating(5)">★</span>
                    </div>
                    <input type="hidden" id="current-rating" value="5">
                    
                    <textarea id="rating-comment" placeholder="Leave a comment (optional)" style="width:100%; padding:12px; border:1px solid #eee; border-radius:8px; margin-bottom:20px; min-height:80px;"></textarea>
                    
                    <div style="display:flex; gap:10px;">
                        <button class="btn-secondary" onclick="closeRatingModal()" style="flex:1;">Skip</button>
                        <button onclick="submitReview()" style="flex:1;">Submit</button>
                    </div>
                </div>
            </div>
"""
if 'id="subscriptions-section"' not in content:
    content = content.replace(
        '<!-- Admin Panel -->',
        extra_sections_html + '\n            <!-- Admin Panel -->'
    )

# 4. Add JS for Tabs, Promos, Rating, Subscriptions
js_logic = """
        // --- PHASE 1 JS ---
        let currentPrice = 0;
        let appliedPromo = null;
        let activeReviewRequestId = null;

        async function applyPromoCode() {
            const code = document.getElementById('promo-code').value.trim();
            if(!code) return;
            
            try {
                const response = await fetch('/promos/validate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code, amount: currentPrice })
                });
                
                const data = await response.json();
                if(response.ok && data.valid) {
                    appliedPromo = code;
                    const newPrice = currentPrice - data.discount_amount;
                    document.getElementById('estimated-price-display').innerHTML = `<span style="text-decoration:line-through; font-size:14px; color:#999; margin-right:8px;">₹${currentPrice}</span>₹${Math.round(newPrice)}`;
                    const msg = document.getElementById('promo-message');
                    msg.textContent = `Promo applied! You saved ₹${Math.round(data.discount_amount)}`;
                    msg.style.color = 'green';
                    
                    // Update currentPrice state so submitServiceRequest sends the right final_price (mapped to estimated_price field for Phase 1 demo)
                    currentPrice = newPrice;
                } else {
                    const msg = document.getElementById('promo-message');
                    msg.textContent = data.detail || "Invalid promo code";
                    msg.style.color = 'red';
                }
            } catch (error) {
                console.error(error);
            }
        }

        function setRating(stars) {
            document.getElementById('current-rating').value = stars;
            const starSpans = document.querySelectorAll('#star-rating span');
            starSpans.forEach((span, i) => {
                span.style.color = i < stars ? '#fbbf24' : '#ddd';
            });
        }
        
        function openRatingModal(requestId) {
            activeReviewRequestId = requestId;
            document.getElementById('rating-modal').style.display = 'flex';
            setRating(5); // Default 5 stars
        }
        
        function closeRatingModal() {
            document.getElementById('rating-modal').style.display = 'none';
        }

        async function submitReview() {
            if(!activeReviewRequestId) return;
            const rating = parseInt(document.getElementById('current-rating').value);
            const comment = document.getElementById('rating-comment').value;
            
            try {
                const response = await fetch('/reviews/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentToken}`
                    },
                    body: JSON.stringify({ request_id: activeReviewRequestId, rating: rating, comment: comment })
                });
                if(response.ok) {
                    showStatus('Review submitted successfully! Thank you.', 'success');
                    closeRatingModal();
                } else {
                    showStatus('Failed to submit review', 'error');
                }
            } catch (error) {
                showStatus('Network error', 'error');
            }
        }
        
        async function buySubscription(planId) {
            try {
                const response = await fetch('/subscriptions/buy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentToken}`
                    },
                    body: JSON.stringify({ plan_id: planId })
                });
                if(response.ok) {
                    showStatus('Subscription purchased successfully! (Mock Payment)', 'success');
                }
            } catch (error) {
                showStatus('Network error', 'error');
            }
        }
"""
if "applyPromoCode()" not in content:
    content = content.replace(
        'let selectedHouseSize = \'1BHK\';',
        'let selectedHouseSize = \'1BHK\';\n' + js_logic
    )

# Fix Tab switching logic to include subscriptions
if "} else if (tabName === 'subscriptions') {" not in content:
    content = content.replace(
        "} else if (tabName === 'admin') {",
        "} else if (tabName === 'subscriptions') {\n                document.querySelector('.dashboard-section .tab:nth-child(3)').classList.add('active');\n                document.getElementById('subscriptions-section').style.display = 'block';\n            } else if (tabName === 'admin') {"
    )

# Update price calculation logic to save currentPrice globally
old_calc = """            const finalPrice = Math.round(basePrice * multiplier);"""
new_calc = """            const finalPrice = Math.round(basePrice * multiplier);
            currentPrice = finalPrice;
            appliedPromo = null; // Reset promo when service/size changes
            
            const msgEl = document.getElementById('promo-message');
            if (msgEl) msgEl.textContent = '';
            
            const codeEl = document.getElementById('promo-code');
            if (codeEl) codeEl.value = '';"""
if "currentPrice = finalPrice;" not in content:
    content = content.replace(old_calc, new_calc)

# Ensure estimated_price submitted is currentPrice
old_submit = "estimated_price: estimatedPrice,"
new_submit = "estimated_price: currentPrice,"
content = content.replace(old_submit, new_submit)


# We also need to add a "Rate" button to completed requests in `loadServiceRequests`
# But loadServiceRequests is dynamic. Let's see if we can just append it via JS hack or assume it's created dynamically.
# Looking at dashboard.html, loadServiceRequests creates a card. We don't have its source here directly in view, but we can replace the HTML string.
old_completed = "if (r.status === 'completed' || r.status === 'cancelled')"
new_completed = """let rateButton = (r.status === 'completed' && currentUser.role === 'customer') ? `<button style="margin-top:10px; background:#fbbf24; color:#fff;" onclick="openRatingModal(${r.id})">⭐ Rate Service</button>` : '';
                    if (r.status === 'completed' || r.status === 'cancelled')"""

# We don't actually see loadServiceRequests in our previous slice, it's further down. Let's do a targeted replace.
if "rateButton" not in content:
    content = re.sub(
        r'(\<div class="request-card"\>.*?\</div\>.*?)(?=const reqsHtml)',
        r'\1' + '\n// Note: Rating button injection logic needs to be inside the map function. Let\'s replace the card HTML generation.',
        content, flags=re.DOTALL
    )
    # Actually, replacing inside the JS template literal is tricky without exact string.
    # Let's just do:
    content = content.replace(
        """<span class="status-badge status-${r.status.toLowerCase()}">${r.status}</span>
                            </div>
                        </div>`,
                    })
                    .join('');""",
        """<span class="status-badge status-${r.status.toLowerCase()}">${r.status}</span>
                            </div>
                            ${(r.status.toLowerCase() === 'completed' && currentUser.role === 'customer') ? `<button style="margin-top:10px; width:100%; background:#fbbf24; color:#fff; padding:8px; border-radius:8px;" onclick="openRatingModal(${r.id})">⭐ Rate Service</button>` : ''}
                        </div>`,
                    })
                    .join('');"""
    )


with open(dash_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Frontend UI updated successfully.")
