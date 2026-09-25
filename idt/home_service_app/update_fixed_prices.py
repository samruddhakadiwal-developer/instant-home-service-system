import re
import shutil
import os

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
img_dir = os.path.join(app_dir, "static", "images")
brain_dir = r"C:\Users\Kiran\.gemini\antigravity\brain\e91aee10-3d63-4bc1-bd8d-ffce257a1c88"

# 1. Copy image
ac_repair_src = os.path.join(brain_dir, "ac_repair_indian_1780590580522.png")
if os.path.exists(ac_repair_src):
    shutil.copy(ac_repair_src, os.path.join(img_dir, "ac_repair.png"))

# 2. Update models.py
models_path = os.path.join(app_dir, "models.py")
with open(models_path, "r", encoding="utf-8") as f:
    models_content = f.read()
if 'AC_REPAIR = "ac_repair"' not in models_content:
    models_content = models_content.replace('CARPENTRY = "carpentry"', 'CARPENTRY = "carpentry"\n    AC_REPAIR = "ac_repair"')
with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_content)

# 3. Update main.py
main_path = os.path.join(app_dir, "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# Add ac_repair to SERVICE_PRICES
if '"ac_repair": 299.0,' not in main_content:
    main_content = main_content.replace('"carpentry": 199.0,', '"carpentry": 199.0,\n    "ac_repair": 299.0,')

# Fix BHK pricing logic in backend
backend_logic_old = """        size_multiplier = {
            "1BHK": 1.0,
            "2BHK": 1.5,
            "3BHK": 2.0,
            "4BHK+": 2.5,
            "Villa": 3.0
        }.get(request.house_size, 1.0)
        base_price *= size_multiplier"""
backend_logic_new = """        size_multiplier = {
            "1BHK": 1.0,
            "2BHK": 1.5,
            "3BHK": 2.0,
            "4BHK+": 2.5,
            "Villa": 3.0
        }.get(request.house_size, 1.0)
        
        # Fixed price for specific services (no BHK multiplier)
        if service_type_str in ['carpentry', 'ac_repair', 'electrician']:
            size_multiplier = 1.0
            
        base_price *= size_multiplier"""
if "Fixed price for specific services" not in main_content:
    main_content = main_content.replace(backend_logic_old, backend_logic_new)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

# 4. Update dashboard.html
dash_path = os.path.join(app_dir, "dashboard.html")
with open(dash_path, "r", encoding="utf-8") as f:
    dash_content = f.read()

# Add step-2 id to house size section
if 'id="step-2-house-size"' not in dash_content:
    dash_content = dash_content.replace(
        '<!-- Step 2: House Size -->\n                <div class="section-card">',
        '<!-- Step 2: House Size -->\n                <div class="section-card" id="step-2-house-size">'
    )

# Remove grooming card
grooming_pattern = r'<div class="service-card" onclick="selectServiceCard\(this,\'grooming\'\)".*?</div>\s*</div>'
dash_content = re.sub(grooming_pattern, '', dash_content, flags=re.DOTALL)

# Remove grooming from prices
dash_content = re.sub(r"\s*'grooming': 149,", '', dash_content)

# Add ac_repair to JS SERVICE_PRICES
if "'ac_repair': 299," not in dash_content:
    dash_content = dash_content.replace("'carpentry': 199,", "'carpentry': 199,\n            'ac_repair': 299,")

# Add AC repair card
ac_card = """
                        <div class="service-card" onclick="selectServiceCard(this,'ac_repair')">
                            <img src="/static/images/ac_repair.png" alt="AC Repair" class="card-image">
                            <div class="card-name">AC Repair</div>
                            <div class="card-price" id="price-ac_repair">₹299</div>
                            <span class="card-check">✅</span>
                        </div>"""
if "selectServiceCard(this,'ac_repair')" not in dash_content:
    dash_content = re.sub(
        r'(<div class="service-card" onclick="selectServiceCard\(this,\'carpentry\'\)".*?</div>\s*</div>)',
        r'\1' + ac_card,
        dash_content,
        flags=re.DOTALL
    )

# Note: carpentry onclick in dashboard.html is actually selectService('carpentry') from the previous script?
# Wait! In the previous script I wrote `selectService('carpentry')` instead of `selectServiceCard(this,'carpentry')`!
# Let me fix carpentry card to use `selectServiceCard(this,'carpentry')` as well.
dash_content = dash_content.replace("selectService('carpentry')", "selectServiceCard(this,'carpentry')")

# If carpentry card is there, let's insert ac_repair after it
if "selectServiceCard(this,'ac_repair')" not in dash_content:
    dash_content = re.sub(
        r'(<div class="service-card" onclick="selectServiceCard\(this,\'carpentry\'\)">.*?</div>\s*</div>)',
        r'\1' + ac_card,
        dash_content,
        flags=re.DOTALL
    )

# Update price calculation logic in JS
js_calc_old = """        function updatePriceSummary() {
            if (!selectedServiceType) return;
            const basePrice = SERVICE_PRICES[selectedServiceType] || 149;
            const multiplier = SIZE_MULTIPLIERS[selectedHouseSize] || 1.0;
            const finalPrice = Math.round(basePrice * multiplier);"""
js_calc_new = """        function updatePriceSummary() {
            if (!selectedServiceType) return;
            const fixedServices = ['carpentry', 'ac_repair', 'electrician'];
            const isFixed = fixedServices.includes(selectedServiceType);
            
            const basePrice = SERVICE_PRICES[selectedServiceType] || 149;
            const multiplier = isFixed ? 1.0 : (SIZE_MULTIPLIERS[selectedHouseSize] || 1.0);
            const finalPrice = Math.round(basePrice * multiplier);
            
            // Show/hide house size step based on service
            const houseSizeStep = document.getElementById('step-2-house-size');
            if(houseSizeStep) {
                if(isFixed) {
                    houseSizeStep.style.display = 'none';
                } else {
                    houseSizeStep.style.display = 'block';
                }
            }"""
if "const fixedServices = ['carpentry', 'ac_repair', 'electrician'];" not in dash_content:
    dash_content = dash_content.replace(js_calc_old, js_calc_new)

# In the update loop for price updates on cards, we shouldn't apply multiplier to fixed services
card_price_old = """            // Update all card prices based on house size
            Object.keys(SERVICE_PRICES).forEach(type => {
                const el = document.getElementById('price-' + type);
                if (el) {
                    const p = Math.round(SERVICE_PRICES[type] * multiplier);
                    el.textContent = '₹' + p;
                }
            });"""
card_price_new = """            // Update all card prices based on house size
            Object.keys(SERVICE_PRICES).forEach(type => {
                const el = document.getElementById('price-' + type);
                if (el) {
                    const isTypeFixed = fixedServices.includes(type);
                    const typeMultiplier = isTypeFixed ? 1.0 : multiplier;
                    const p = Math.round(SERVICE_PRICES[type] * typeMultiplier);
                    el.textContent = '₹' + p;
                }
            });"""
if "const isTypeFixed = fixedServices.includes(type);" not in dash_content:
    dash_content = dash_content.replace(card_price_old, card_price_new)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(dash_content)

print("Update completed")
