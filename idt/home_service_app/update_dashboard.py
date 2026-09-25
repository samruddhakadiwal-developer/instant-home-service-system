import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    r'id="price-grooming">.*?</': 'id="price-grooming">\u20b9149</',
    r'id="price-mopping">.*?</': 'id="price-mopping">\u20b999</',
    r'id="price-cleaning_utensils">.*?</': 'id="price-cleaning_utensils">\u20b999</',
    r'id="price-plumbing">.*?</': 'id="price-plumbing">\u20b9149</',
    r'id="price-electrician">.*?</': 'id="price-electrician">\u20b9149</',
    r'id="price-general_cleaning">.*?</': 'id="price-general_cleaning">\u20b9199</',
    r'id="price-deep_cleaning">.*?</': 'id="price-deep_cleaning">\u20b9399</',
    r'id="price-bathroom_cleaning">.*?</': 'id="price-bathroom_cleaning">\u20b9149</',
    r'id="price-kitchen_cleaning">.*?</': 'id="price-kitchen_cleaning">\u20b9149</',
    r'id="price-laundry">.*?</': 'id="price-laundry">\u20b9149</',
}

for pat, repl in replacements.items():
    content = re.sub(pat, repl, content)

js_replacements = {
    r"'grooming': 299,": "'grooming': 149,",
    r"'mopping': 199,": "'mopping': 99,",
    r"'cleaning_utensils': 149,": "'cleaning_utensils': 99,",
    r"'plumbing': 499,": "'plumbing': 149,",
    r"'kitchen_cleaning': 399,": "'kitchen_cleaning': 149,",
    r"'laundry': 249,": "'laundry': 149,",
    r"'sweeping_mopping': 199,": "'sweeping_mopping': 99,",
    r"'window_cleaning': 299,": "'window_cleaning': 149,",
    r"'car_cleaning': 399,": "'car_cleaning': 149,",
    r"'hourly_booking': 249,": "'hourly_booking': 99,",
    r"'general_cleaning': 349,": "'general_cleaning': 199,",
    r"'deep_cleaning': 799,": "'deep_cleaning': 399,",
    r"'bathroom_cleaning': 349,": "'bathroom_cleaning': 149,",
    r"SERVICE_PRICES\[serviceType\] \|\| 299": "SERVICE_PRICES[serviceType] || 149",
    r"SERVICE_PRICES\[selectedServiceType\] \|\| 299": "SERVICE_PRICES[selectedServiceType] || 149"
}

for old, new in js_replacements.items():
    content = re.sub(old, new, content)

# Add cache buster to images
content = re.sub(r'(/static/images/[^"]+\.png)', r'\1?v=2', content)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
