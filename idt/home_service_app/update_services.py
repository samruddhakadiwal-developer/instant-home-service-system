import re
import shutil
import os

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
img_dir = os.path.join(app_dir, "static", "images")
brain_dir = r"C:\Users\Kiran\.gemini\antigravity\brain\e91aee10-3d63-4bc1-bd8d-ffce257a1c88"

# 1. Copy images
shutil.copy(os.path.join(brain_dir, "deep_cleaning_indian_1780589683324.png"), os.path.join(img_dir, "deep_cleaning.png"))
shutil.copy(os.path.join(brain_dir, "deep_cleaning_indian_1780589683324.png"), os.path.join(img_dir, "deep_cleaning_real_1779817929626.png"))
shutil.copy(os.path.join(brain_dir, "bathroom_cleaning_indian_1780589699640.png"), os.path.join(img_dir, "bathroom_cleaning.png"))
shutil.copy(os.path.join(brain_dir, "kitchen_cleaning_indian_1780589715634.png"), os.path.join(img_dir, "kitchen_cleaning.png"))
shutil.copy(os.path.join(brain_dir, "carpentry_indian_1780589734217.png"), os.path.join(img_dir, "carpentry.png"))

# 2. Update models.py
models_path = os.path.join(app_dir, "models.py")
with open(models_path, "r", encoding="utf-8") as f:
    models_content = f.read()
if 'CARPENTRY = "carpentry"' not in models_content:
    models_content = models_content.replace('CAR_CLEANING = "car_cleaning"', 'CAR_CLEANING = "car_cleaning"\n    CARPENTRY = "carpentry"')
with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_content)

# 3. Update main.py
main_path = os.path.join(app_dir, "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()
if '"carpentry": 199.0,' not in main_content:
    main_content = main_content.replace('"car_cleaning": 149.0,', '"car_cleaning": 149.0,\n    "carpentry": 199.0,')
with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

# 4. Update dashboard.html
dash_path = os.path.join(app_dir, "dashboard.html")
with open(dash_path, "r", encoding="utf-8") as f:
    dash_content = f.read()

# Add carpentry to prices dict
if "'carpentry': 199," not in dash_content:
    dash_content = dash_content.replace("'car_cleaning': 149,", "'car_cleaning': 149,\n            'carpentry': 199,")

# Add carpentry card if not exists
carpentry_card = """
                        <div class="service-card" onclick="selectService('carpentry')">
                            <img src="/static/images/carpentry.png?v=3" alt="Carpentry" class="card-image">
                            <div class="card-content">
                                <h3 class="card-title">Carpentry</h3>
                                <div class="card-price" id="price-carpentry">\u20b9199</div>
                            </div>
                        </div>"""

if "price-carpentry" not in dash_content:
    # Insert after laundry card
    dash_content = re.sub(
        r'(<div class="service-card"[^>]*onclick="selectService\(\'laundry\'\)"[^>]*>.*?</div>\s*</div>)',
        r'\1' + carpentry_card,
        dash_content,
        flags=re.DOTALL
    )

# Increment cache buster to v=3 for deep cleaning, bathroom cleaning, kitchen cleaning
dash_content = dash_content.replace("deep_cleaning_real_1779817929626.png?v=2", "deep_cleaning_real_1779817929626.png?v=3")
dash_content = dash_content.replace("deep_cleaning.png?v=2", "deep_cleaning.png?v=3")
dash_content = dash_content.replace("bathroom_cleaning.png?v=2", "bathroom_cleaning.png?v=3")
dash_content = dash_content.replace("kitchen_cleaning.png?v=2", "kitchen_cleaning.png?v=3")

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(dash_content)

print("Updated perfectly")
