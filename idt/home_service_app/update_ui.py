import re
import os

app_dir = r"c:\Users\Kiran\Desktop\home_service_app"
dash_path = os.path.join(app_dir, "dashboard.html")

with open(dash_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace Step 3 HTML
step_3_old = r"""                <!-- Step 3: Details -->
                <div class="section-card">
                    <label style="font-size:16px; font-weight:700; margin-bottom:16px; display:block;">3. Request Details</label>
                    <div class="form-group">
                        <label for="request-title">Title:</label>
                        <input type="text" id="request-title" placeholder="Brief title for your request" required>
                    </div>
                    <div class="form-group">
                        <label for="request-description">Description:</label>
                        <textarea id="request-description" placeholder="Detailed description of the service needed" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="preferred-date">Preferred Date:</label>
                        <input type="datetime-local" id="preferred-date">
                    </div>
                    <div class="form-group">
                        <label for="preferred-time">Preferred Time:</label>
                        <select id="preferred-time">
                            <option value="">Any time</option>
                            <option value="morning">Morning (9 AM - 12 PM)</option>
                            <option value="afternoon">Afternoon (12 PM - 5 PM)</option>
                            <option value="evening">Evening (5 PM - 8 PM)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="urgency">Urgency:</label>
                        <select id="urgency">
                            <option value="low">Low</option>
                            <option value="normal" selected>Normal</option>
                            <option value="high">High</option>
                            <option value="emergency">Emergency</option>
                        </select>
                    </div>
                </div>"""

step_3_new = r"""                <!-- Step 3: Details (Snabbit/Pronto Style) -->
                <div class="section-card">
                    <label style="font-size:16px; font-weight:700; margin-bottom:16px; display:block;">3. Date & Time Preferences</label>
                    
                    <div class="form-group">
                        <label style="font-size:14px; color:var(--text-light); margin-bottom:8px;">When do you need it?</label>
                        <input type="date" id="preferred-date" style="padding:12px; border-radius:12px; border:2px solid rgba(99,102,241,0.2); width:100%; font-family:inherit; font-size:15px; margin-bottom:16px; outline:none; background:rgba(255,255,255,0.8);">
                    </div>

                    <label style="font-size:14px; color:var(--text-light); margin-bottom:8px; display:block;">Preferred Time Slot</label>
                    <div class="house-size-pills" id="time-pills" style="margin-bottom:20px;">
                        <div class="size-pill selected" onclick="selectTimeSlot(this,'')">Any time</div>
                        <div class="size-pill" onclick="selectTimeSlot(this,'morning')">Morning (9 AM-12 PM)</div>
                        <div class="size-pill" onclick="selectTimeSlot(this,'afternoon')">Afternoon (12-5 PM)</div>
                        <div class="size-pill" onclick="selectTimeSlot(this,'evening')">Evening (5-8 PM)</div>
                    </div>
                    <input type="hidden" id="preferred-time" value="">

                    <label style="font-size:14px; color:var(--text-light); margin-bottom:8px; display:block;">Urgency</label>
                    <div class="house-size-pills" id="urgency-pills" style="margin-bottom:8px;">
                        <div class="size-pill selected" onclick="selectUrgency(this,'normal')">Normal</div>
                        <div class="size-pill" onclick="selectUrgency(this,'high')">High</div>
                        <div class="size-pill" onclick="selectUrgency(this,'emergency')" style="border-color:#fca5a5; color:#ef4444;">Emergency</div>
                    </div>
                    <input type="hidden" id="urgency" value="normal">
                </div>"""

content = content.replace(step_3_old, step_3_new)

# 2. Add the JS for time slot and urgency selection pills
js_pill_logic = """
        function selectTimeSlot(el, time) {
            document.querySelectorAll('#time-pills .size-pill').forEach(p => p.classList.remove('selected'));
            el.classList.add('selected');
            document.getElementById('preferred-time').value = time;
        }

        function selectUrgency(el, urgency) {
            document.querySelectorAll('#urgency-pills .size-pill').forEach(p => p.classList.remove('selected'));
            el.classList.add('selected');
            document.getElementById('urgency').value = urgency;
            if(urgency === 'emergency') {
                el.style.background = '#fee2e2';
                el.style.color = '#b91c1c';
            } else {
                document.querySelectorAll('#urgency-pills .size-pill').forEach(p => { p.style.background = ''; p.style.color = ''; });
            }
        }
"""
if "selectTimeSlot(" not in content:
    content = content.replace("function selectHouseSize(", js_pill_logic + "\n        function selectHouseSize(")

# 3. Update the submitServiceRequest JS to not crash when getElementById('request-title') is null
js_old = """                title: document.getElementById('request-title').value || (serviceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Service'),
                description: document.getElementById('request-description').value || 'Service requested via the portal.',"""

js_new = """                title: (document.getElementById('request-title') ? document.getElementById('request-title').value : '') || (serviceType.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()) + ' Service'),
                description: (document.getElementById('request-description') ? document.getElementById('request-description').value : '') || 'Service requested via the app.',"""

content = content.replace(js_old, js_new)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(content)

print("UI updated successfully")
