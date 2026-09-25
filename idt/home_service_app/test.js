
        let currentUser = null;
        let currentToken = null;
        let selectedServices = [];
        let selectedHouseSize = '1BHK';
        let currentPrice = 0;

        // Base prices for each service type (in INR)
        const SERVICE_PRICES = {
            'mopping': 99,
            'cleaning_utensils': 99,
            'plumbing': 149,
            'electrician': 449,
            'general_cleaning': 199,
            'deep_cleaning': 399,
            'bathroom_cleaning': 149,
            'kitchen_cleaning': 149,
            'laundry': 149,
            'sweeping_mopping': 99,
            'window_cleaning': 149,
            'car_cleaning': 149,
            'carpentry': 199,
            'ac_repair': 299,
            'hourly_booking': 99,
            'packing_unpacking': 599,
        };

        // House size multipliers
        const SIZE_MULTIPLIERS = {
            '1BHK': 1.0,
            '2BHK': 1.5,
            '3BHK': 2.0,
            '4BHK+': 2.5,
            'Villa': 3.0
        };

        function selectServiceCard(el, serviceType) {
            if (selectedServices.includes(serviceType)) {
                selectedServices = selectedServices.filter(s => s !== serviceType);
                el.classList.remove('selected');
            } else {
                selectedServices.push(serviceType);
                el.classList.add('selected');
            }
            document.getElementById('service-type').value = selectedServices.join(', ');
            updatePriceSummary();
        }

        function selectHouseSize(el, size) {
            document.querySelectorAll('.size-pill').forEach(p => p.classList.remove('selected'));
            el.classList.add('selected');
            selectedHouseSize = size;
            document.getElementById('house-size').value = size;
            updatePriceSummary();
        }

        function updatePriceSummary() {
            if (selectedServices.length === 0) {
                const summaryEl = document.getElementById('price-summary');
                if (summaryEl) summaryEl.style.display = 'none';
                return;
            }
            const fixedServices = ['carpentry', 'ac_repair', 'electrician'];
            
            // Show/hide house size step based on if ALL services are fixed
            const allFixed = selectedServices.every(s => fixedServices.includes(s));
            const houseSizeStep = document.getElementById('step-2-house-size');
            if(houseSizeStep) {
                if(allFixed) {
                    houseSizeStep.style.display = 'none';
                } else {
                    houseSizeStep.style.display = 'block';
                }
            }

            const multiplier = SIZE_MULTIPLIERS[selectedHouseSize] || 1.0;
            let totalFinalPrice = 0;
            let totalBasePrice = 0;
            
            selectedServices.forEach(s_type => {
                const bPrice = SERVICE_PRICES[s_type] || 149;
                totalBasePrice += bPrice;
                const sMult = fixedServices.includes(s_type) ? 1.0 : multiplier;
                totalFinalPrice += Math.round(bPrice * sMult);
            });

            currentPrice = totalFinalPrice;

            // Update all card prices based on house size
            Object.keys(SERVICE_PRICES).forEach(type => {
                const el = document.getElementById('price-' + type);
                if (el) {
                    const isTypeFixed = fixedServices.includes(type);
                    const typeMultiplier = isTypeFixed ? 1.0 : multiplier;
                    const p = Math.round(SERVICE_PRICES[type] * typeMultiplier);
                    el.textContent = '₹' + p;
                }
            });

            const summaryEl = document.getElementById('price-summary');
            if (summaryEl) {
                summaryEl.style.display = 'flex';
                document.getElementById('estimated-price-display').textContent = '₹' + totalFinalPrice;
                const sizeName = selectedHouseSize === 'Villa' ? 'Villa / Bungalow' : selectedHouseSize;
                document.getElementById('price-breakdown').textContent = `Total Base ₹${totalBasePrice} (Size multiplier applied where applicable)`;
            }
        }

        // Tab switching functions

        function showDashboardTab(tabName) {
            document.querySelectorAll('.dashboard-section .tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.dashboard-section > div:not(.tabs):not(#user-summary)').forEach(section => section.style.display = 'none');

            if (tabName === 'requests') {
                document.querySelector('.dashboard-section .tab:first-child').classList.add('active');
                document.getElementById('requests-list').style.display = 'block';
                loadServiceRequests();
            } else if (tabName === 'new-request') {
                document.querySelector('.dashboard-section .tab:nth-child(2)').classList.add('active');
                document.getElementById('new-request-form').style.display = 'block';
                populateRequestForm();
            } else if (tabName === 'admin') {
                document.getElementById('admin-tab').classList.add('active');
                document.getElementById('admin-panel').style.display = 'block';
                loadAdminDashboard();
            }
        }

        // Authentication functions

        async function requestOtp() {
            const emailInput = document.getElementById('otp-email').value;
            const roleInput = document.getElementById('otp-role').value;
            
            if (!emailInput || !emailInput.includes('@')) {
                showStatus('Please enter a valid email address.', 'error');
                return;
            }

            const otpData = {
                email: emailInput,
                role: roleInput
            };

            try {
                const response = await fetch('/auth/request-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(otpData)
                });

                const data = await response.json();
                if (response.ok) {
                    if (data.otp_code) {
                        document.getElementById('otp-code-display').textContent = data.otp_code;
                        document.getElementById('otp-display').style.display = 'block';
                        showStatus(`OTP generated for ${data.email}. Check the code above.`, 'success');
                    } else {
                        alert('OTP sent via email.');
                        document.getElementById('otp-display').style.display = 'none';
                        showStatus(data.message || `OTP sent to ${data.email}. Check your email.`, 'success');
                    }
                } else {
                    let errorMessage = data.detail;
                    if (Array.isArray(errorMessage)) {
                        errorMessage = errorMessage.map(err => err.msg).join(", ");
                    }
                    alert('Server returned error: ' + errorMessage);
                    document.getElementById('otp-display').style.display = 'none';
                    showStatus(errorMessage || 'Failed to request OTP', 'error');
                }
            } catch (error) {
                alert('Network error: ' + error.message);
                document.getElementById('otp-display').style.display = 'none';
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        async function verifyOtp() {
            const otpData = {
                email: document.getElementById('otp-email').value,
                otp_code: document.getElementById('otp-code').value
            };

            try {
                const response = await fetch('/auth/verify-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(otpData)
                });

                const data = await response.json();
                if (response.ok) {
                    if (data.user_exists) {
                        // Existing user - login
                        currentToken = data.access_token;
                        localStorage.setItem('authToken', currentToken);
                        await loadCurrentUser();
                        document.getElementById('auth-section').classList.remove('show');
                        document.getElementById('dashboard-section').classList.add('show');
                        document.getElementById('logout-btn').style.display = 'block';
                        showStatus('Login successful! Welcome back.', 'success');
                    } else {
                        // New user - show registration form
                        document.getElementById('otp-step').style.display = 'none';
                        document.getElementById('registration-step').style.display = 'block';
                        showStatus('OTP verified! Please complete your profile.', 'success');
                    }
                } else {
                    showStatus(data.detail || 'OTP verification failed', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        async function completeRegistration() {
            const regData = {
                email: document.getElementById('otp-email').value,
                full_name: document.getElementById('reg-fullname').value,
                mobile_number: document.getElementById('reg-mobile').value,
                area: document.getElementById('reg-area').value,
                locality: document.getElementById('reg-locality').value,
                apartment_no: document.getElementById('reg-apartment').value,
                address: document.getElementById('reg-address').value,
                expertise: document.getElementById('reg-expertise').value,
                role: document.getElementById('otp-role').value
            };

            try {
                const response = await fetch('/auth/complete-registration', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(regData)
                });

                const data = await response.json();
                if (response.ok) {
                    currentToken = data.access_token;
                    localStorage.setItem('authToken', currentToken);
                    await loadCurrentUser();
                    document.getElementById('auth-section').classList.remove('show');
                    document.getElementById('dashboard-section').classList.add('show');
                    document.getElementById('logout-btn').style.display = 'block';
                    showStatus('Registration completed! Welcome.', 'success');
                } else {
                    let errorMsg = 'Registration failed';
                    if (data.detail) {
                        errorMsg = typeof data.detail === 'string' ? data.detail : data.detail[0].msg || JSON.stringify(data.detail);
                    }
                    showStatus(errorMsg, 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        function backToOtp() {
            document.getElementById('registration-step').style.display = 'none';
            document.getElementById('otp-step').style.display = 'block';
        }

        async function loadCurrentUser() {
            try {
                const response = await fetch('/auth/me', {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });

                if (response.ok) {
                    currentUser = await response.json();
                    if (currentUser.role === 'admin') {
                        document.getElementById('admin-tab').style.display = 'block';
                    }
                    if (currentUser.role === 'gig_worker') {
                        // Redirect gig worker to their own portal automatically
                        window.location.href = '/dashboard/gig-worker';
                        return;
                    }
                    if (currentUser.role === 'owner') {
                        // Redirect owner to their portal automatically
                        window.location.href = '/dashboard/owner';
                        return;
                    }
                    updateUserSummary();
                    populateRequestForm();
                }
            } catch (error) {
                console.error('Error loading user:', error);
            }
        }

        function updateUserSummary() {
            if (!currentUser) return;
            const userSummary = document.getElementById('user-summary');
            userSummary.innerHTML = `
                <div>
                    <h3 style="margin-bottom: 4px; font-size: 20px;">Welcome back, ${currentUser.full_name || currentUser.username}! 👋</h3>
                    <p style="margin: 0; color: var(--text-light); font-size: 14px;">${currentUser.email} | ${currentUser.area || 'Profile incomplete'}</p>
                </div>
                <button class="btn-secondary" onclick="logout()" style="margin:0; padding: 10px 20px; font-size: 14px;">Logout</button>
            `;
            userSummary.style.display = 'flex';

            // Show portal links based on role
            const portalLinks = document.getElementById('portal-links');
            portalLinks.style.display = 'block';
            
            if (currentUser.role === 'owner') {
                document.getElementById('owner-link').style.display = 'inline-block';
                document.getElementById('gig-link').style.display = 'none';
            } else if (currentUser.role === 'gig_worker') {
                document.getElementById('owner-link').style.display = 'none';
                document.getElementById('gig-link').style.display = 'inline-block';
            } else {
                document.getElementById('owner-link').style.display = 'none';
                document.getElementById('gig-link').style.display = 'none';
            }
        }

        function populateRequestForm() {
            if (!currentUser) return;
            const address = currentUser.address || '';
            const area = currentUser.area || '';
            const locality = currentUser.locality || '';
            const apartment = currentUser.apartment_no || '';
            const phone = currentUser.mobile_number || currentUser.alternate_mobile_number || '';
            const alternate = currentUser.alternate_mobile_number && currentUser.alternate_mobile_number !== currentUser.mobile_number ? currentUser.alternate_mobile_number : '';

            document.getElementById('location').value = address;
            document.getElementById('request-area').value = area;
            document.getElementById('request-locality').value = locality;
            document.getElementById('request-apartment').value = apartment;
            document.getElementById('contact-phone').value = phone;
            document.getElementById('alternate-contact').value = alternate;
        }

        function logout() {
            currentUser = null;
            currentToken = null;
            localStorage.removeItem('authToken');
            document.getElementById('auth-section').classList.add('show');
            document.getElementById('dashboard-section').classList.remove('show');
            document.getElementById('logout-btn').style.display = 'none';
            document.getElementById('admin-tab').style.display = 'none';
            document.getElementById('user-summary').style.display = 'none';
            document.getElementById('portal-links').style.display = 'none';
            // Reset forms
            document.getElementById('otp-step').style.display = 'block';
            document.getElementById('registration-step').style.display = 'none';
            document.getElementById('otp-display').style.display = 'none';
            document.getElementById('otp-email').value = '';
            document.getElementById('otp-code').value = '';
            document.getElementById('reg-fullname').value = '';
            document.getElementById('reg-mobile').value = '';
            document.getElementById('reg-area').value = '';
            document.getElementById('reg-locality').value = '';
            document.getElementById('reg-apartment').value = '';
            document.getElementById('reg-address').value = '';
            document.getElementById('reg-expertise').value = '';
            showStatus('Logged out successfully', 'success');
        }

        // Service request functions
        async function submitServiceRequest() {
            const serviceType = document.getElementById('service-type').value;
            if (!serviceType) {
                showStatus('Please select a service type first.', 'error');
                return;
            }

            const houseSize = document.getElementById('house-size').value || '1BHK';

            const titleEl = document.getElementById('request-title');
            const descEl = document.getElementById('request-description');
            
            const requestData = {
                service_type: serviceType,
                title: (titleEl && titleEl.value) ? titleEl.value : (serviceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Service'),
                description: (descEl && descEl.value) ? descEl.value : 'Service requested via the portal.',
                preferred_date: document.getElementById('preferred-date').value || null,
                preferred_time: document.getElementById('preferred-time').value || null,
                urgency: document.getElementById('urgency').value,
                location: document.getElementById('location').value,
                contact_phone: document.getElementById('contact-phone').value,
                alternate_contact: document.getElementById('alternate-contact').value || null,
                area: document.getElementById('request-area').value,
                locality: document.getElementById('request-locality').value,
                apartment_no: document.getElementById('request-apartment').value,
                house_size: houseSize,
                estimated_price: currentPrice,
                additional_notes: document.getElementById('additional-notes').value || null
            };

            try {
                const response = await fetch('/service-requests/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentToken}`
                    },
                    body: JSON.stringify(requestData)
                });

                const data = await response.json();
                if (response.ok) {
                    showStatus('Service request submitted successfully!', 'success');
                    // Clear form
                    document.querySelectorAll('#new-request-form input, #new-request-form textarea, #new-request-form select').forEach(el => el.value = '');
                    showDashboardTab('requests');
                } else {
                    showStatus(data.detail || 'Failed to submit request', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        async function loadServiceRequests() {
            try {
                const response = await fetch('/service-requests/', {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });

                if (response.ok) {
                    const requests = await response.json();
                    displayServiceRequests(requests, 'requests-container');
                } else {
                    showStatus('Failed to load requests', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        async function loadAllServiceRequests() {
            try {
                const response = await fetch('/service-requests/', {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });

                if (response.ok) {
                    const requests = await response.json();
                    displayServiceRequests(requests, 'all-requests-container', true);
                } else {
                    showStatus('Failed to load requests', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        function displayServiceRequests(requests, containerId, isAdmin = false) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            if (requests.length === 0) {
                container.innerHTML = '<p>No service requests found.</p>';
                return;
            }

            requests.forEach(request => {
                const card = document.createElement('div');
                card.className = 'request-card';

                const statusClass = `status-${request.status}`;
                const adminControls = isAdmin ? `
                    <br>
                    <select onchange="updateRequestStatus(${request.id}, this.value)">
                        <option value="pending" ${request.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="assigned" ${request.status === 'assigned' ? 'selected' : ''}>Assigned</option>
                        <option value="in_progress" ${request.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${request.status === 'completed' ? 'selected' : ''}>Completed</option>
                        <option value="cancelled" ${request.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                    </select>
                ` : '';

                card.innerHTML = `
                    <h3>${request.title}</h3>
                    <p><strong>Type:</strong> ${request.service_type}</p>
                    <p><strong>Description:</strong> ${request.description}</p>
                    <p><strong>Location:</strong> ${request.location}</p>
                    <p><strong>Status:</strong> <span class="status-badge ${statusClass}">${request.status.replace('_', ' ')}</span></p>
                    <p><strong>Urgency:</strong> ${request.urgency}</p>
                    <p><strong>Created:</strong> ${new Date(request.created_at).toLocaleDateString()}</p>
                    ${request.arrival_otp && !isAdmin && currentUser.role === 'customer' ? `
                    <div style="background:#fef3c7; padding:12px; border-radius:8px; margin-top:12px; border:1px solid #f59e0b;">
                        <strong style="color:#b45309;">👷 Worker has arrived!</strong><br>
                        Give this OTP to the worker to start the job: <span style="font-size:22px; font-weight:bold; letter-spacing:2px; color:#b45309; display:block; margin-top:5px;">${request.arrival_otp}</span>
                    </div>` : ''}
                    ${adminControls}
                `;

                container.appendChild(card);
            });
        }

        async function updateRequestStatus(requestId, newStatus) {
            try {
                const response = await fetch(`/service-requests/${requestId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentToken}`
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                if (response.ok) {
                    showStatus('Request status updated successfully!', 'success');
                    loadAllServiceRequests();
                } else {
                    const data = await response.json();
                    showStatus(data.detail || 'Failed to update status', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        async function loadAdminDashboard() {
            try {
                const response = await fetch('/admin/dashboard', {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });

                if (response.ok) {
                    const stats = await response.json();
                    document.getElementById('admin-stats').innerHTML = `
                        <div class="request-card">
                            <h3>Dashboard Statistics</h3>
                            <p><strong>Total Users:</strong> ${stats.total_users}</p>
                            <p><strong>Total Service Requests:</strong> ${stats.total_service_requests}</p>
                            <p><strong>Pending Requests:</strong> ${stats.pending_requests}</p>
                            <p><strong>Completed Requests:</strong> ${stats.completed_requests}</p>
                        </div>
                    `;
                }
            } catch (error) {
                showStatus('Failed to load admin dashboard', 'error');
            }
        }

        function showStatus(message, type) {
            const container = document.getElementById('toast-container');
            if (!container) {
                // Fallback to old status div
                const statusDiv = document.getElementById('status');
                if (statusDiv) {
                    statusDiv.textContent = message;
                    statusDiv.className = `status ${type}`;
                    statusDiv.style.display = 'block';
                    setTimeout(() => { statusDiv.style.display = 'none'; }, 5000);
                }
                return;
            }
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            const icon = type === 'success' ? '✅' : '❌';
            toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
            container.appendChild(toast);
            setTimeout(() => {
                toast.classList.add('hiding');
                setTimeout(() => toast.remove(), 400);
            }, 4000);
        }

        let notifiedJobs = new Set();
        setInterval(async () => {
            if (!currentToken || !currentUser || currentUser.role !== 'customer') return;
            try {
                const response = await fetch('/service-requests/', {
                    headers: { 'Authorization': `Bearer ${currentToken}` }
                });
                if (response.ok) {
                    const requests = await response.json();
                    displayServiceRequests(requests, 'requests-container');
                    for (let req of requests) {
                        if (req.status === 'completed' && !req.is_paid && !notifiedJobs.has(req.id)) {
                            notifiedJobs.add(req.id);
                            showPaymentPopup(req);
                        }
                    }
                }
            } catch (e) {}
        }, 5000);

        function showPaymentPopup(req) {
            const popup = document.createElement('div');
            popup.style.cssText = 'position:fixed; top:20px; left:50%; transform:translateX(-50%); background:white; padding:20px; border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,0.2); z-index:9999; text-align:center; width:90%; max-width:400px; border:2px solid #10b981; animation: slideDownToast 0.4s ease;';
            popup.innerHTML = `
                <h3 style="margin-top:0; color:#10b981; font-size:20px;">🎉 Your work is done!</h3>
                <p style="color:#475569; margin-bottom:15px; font-size:15px;">The professional has completed: <b>${req.title}</b></p>
                <button style="background:#10b981; color:white; border:none; padding:12px 20px; border-radius:12px; font-weight:bold; cursor:pointer; width:100%;" onclick="window.location.href='/payment?job_id=${req.id}'">Proceed to Payment (₹${req.estimated_price})</button>
                <p style="margin-top:10px; font-size:12px; color:#94a3b8; cursor:pointer;" onclick="this.parentElement.remove()">Dismiss</p>
            `;
            document.body.appendChild(popup);
        }

        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
    