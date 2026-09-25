import re

def update_css(filename, new_css):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the style block
    new_content = re.sub(r'<style>.*?</style>', f'<style>\n{new_css}\n    </style>', content, flags=re.DOTALL)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {filename}")

dashboard_css = """
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        :root {
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --secondary: #8b5cf6;
            --bg-gradient: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
            --card-bg: rgba(255, 255, 255, 0.85);
            --text-dark: #1e293b;
            --text-light: #64748b;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: var(--bg-gradient);
            min-height: 100vh;
            margin: 0;
            padding: 40px 20px;
            color: var(--text-dark);
        }
        
        h1, h2, h3 {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 0;
        }

        .container {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.08);
            border: 1px solid rgba(255, 255, 255, 0.6);
            max-width: 1000px;
            margin: 0 auto 20px;
            animation: fadeIn 0.6s ease-out;
        }

        .auth-section, .request-section, .dashboard-section { display: none; }
        .auth-section.show, .request-section.show, .dashboard-section.show { display: block; }

        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; }
        input, select, textarea {
            width: 100%; padding: 14px 16px;
            border: 2px solid rgba(255,255,255,0.8);
            border-radius: 12px; font-size: 15px; font-family: 'Poppins', sans-serif;
            background: rgba(255,255,255,0.6);
            transition: var(--transition);
            box-sizing: border-box;
        }
        textarea { height: 120px; resize: vertical; }
        input:focus, select:focus, textarea:focus {
            outline: none; border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
            background: white;
        }

        button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white; padding: 14px 24px; border: none; border-radius: 12px;
            cursor: pointer; font-size: 16px; font-weight: 600;
            margin-right: 10px; margin-top: 10px;
            transition: var(--transition);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            font-family: 'Poppins', sans-serif;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        }
        .btn-secondary { background: linear-gradient(135deg, #64748b, #475569); box-shadow: 0 4px 15px rgba(100, 116, 139, 0.3); }
        .btn-secondary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(100, 116, 139, 0.4); }
        .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
        .btn-danger:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4); }

        .status {
            margin-top: 20px; padding: 16px; border-radius: 12px;
            display: none; font-weight: 500; text-align: center;
            animation: slideDown 0.3s ease-out;
        }
        .success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
        .error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

        .request-card {
            background: rgba(255, 255, 255, 0.7);
            border-left: 5px solid var(--primary); padding: 20px;
            border-radius: 16px; margin-bottom: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            border-top: 1px solid rgba(255,255,255,0.5);
            border-right: 1px solid rgba(255,255,255,0.5);
            border-bottom: 1px solid rgba(255,255,255,0.5);
            transition: var(--transition);
        }
        .request-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.06); }
        .request-card p { margin: 8px 0; font-size: 14px; }
        .request-card strong { color: var(--text-dark); }

        .otp-display {
            margin: 20px 0; padding: 20px; background: rgba(255,255,255,0.6);
            border-radius: 16px; border: 1px solid rgba(255,255,255,0.8);
            text-align: center; box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
        }
        .otp-code {
            font-size: 32px; font-weight: 700; color: var(--primary);
            letter-spacing: 5px; font-family: monospace; margin: 10px 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        }

        .status-badge {
            display: inline-block; padding: 6px 12px; border-radius: 20px;
            font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .status-pending { background-color: #fef3c7; color: #b45309; }
        .status-assigned { background-color: #e0e7ff; color: #4338ca; }
        .status-in_progress { background-color: #dbeafe; color: #1d4ed8; }
        .status-completed { background-color: #d1fae5; color: #047857; }
        .status-cancelled { background-color: #fee2e2; color: #b91c1c; }

        .section-card {
            background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px; padding: 25px; margin-bottom: 25px;
        }

        .tabs {
            display: flex; gap: 10px; margin-bottom: 30px;
            background: rgba(255,255,255,0.5); padding: 8px; border-radius: 16px;
        }
        .tab {
            padding: 12px 24px; cursor: pointer; border-radius: 12px;
            font-weight: 600; font-size: 14px; transition: var(--transition);
            flex: 1; text-align: center; color: var(--text-light);
        }
        .tab:hover { background: rgba(255,255,255,0.8); color: var(--text-dark); }
        .tab.active {
            background: white; color: var(--primary);
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
"""

gig_worker_css = """
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        :root {
            --primary: #0ea5e9;
            --primary-hover: #0284c7;
            --secondary: #38bdf8;
            --card-bg: rgba(255, 255, 255, 0.75);
            --text-dark: #0f172a;
            --text-light: #64748b;
            --success: #10b981;
            --danger: #ef4444;
            --border-radius: 20px;
            --shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
            --transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(45deg, #e0f2fe, #bae6fd, #f0f9ff, #e0f2fe);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            min-height: 100vh;
            padding: 30px 20px;
            color: var(--text-dark);
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container { max-width: 1200px; margin: 0 auto; }

        .header {
            background: rgba(255,255,255,0.4);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 24px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.8);
        }

        .header h1 {
            color: var(--text-dark);
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-actions { display: flex; gap: 15px; align-items: center; }

        button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white; border: none; padding: 12px 24px; border-radius: 14px;
            cursor: pointer; font-size: 15px; font-weight: 700;
            transition: var(--transition);
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
            font-family: 'Outfit', sans-serif;
        }

        button:hover {
            transform: translateY(-2px); box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
        }

        .logout-btn { background: linear-gradient(135deg, var(--danger), #f87171); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
        .logout-btn:hover { background: linear-gradient(135deg, #b91c1c, var(--danger)); box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4); }

        .tabs {
            display: flex; gap: 10px; margin-bottom: 25px;
            background: rgba(255,255,255,0.4);
            padding: 8px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.6);
        }
        
        .tab {
            padding: 14px 20px;
            background: transparent;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: var(--transition);
            font-weight: 600;
            flex: 1; text-align: center; color: var(--text-light);
        }
        
        .tab:hover { background: rgba(255,255,255,0.6); color: var(--text-dark); }
        
        .tab.active {
            background: white;
            color: var(--primary);
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .content-section { display: none; animation: fadeIn 0.4s ease-out; }
        .content-section.active { display: block; }

        .card, .form-container {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 30px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.6);
            margin-bottom: 25px;
        }

        .card h3, .form-container h3 {
            color: var(--text-dark); margin-bottom: 20px; font-size: 22px; font-weight: 700;
            display: flex; align-items: center; gap: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.5); padding-bottom: 15px;
        }

        .badge {
            display: inline-block; padding: 6px 14px; border-radius: 20px;
            font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px;
        }
        .badge-assigned { background: #e0f2fe; color: #0284c7; }
        .badge-in-progress { background: #dbeafe; color: #1d4ed8; }
        .badge-completed { background: #d1fae5; color: #047857; }

        .job-item {
            background: rgba(255,255,255,0.8);
            border-left: 5px solid var(--primary); padding: 20px; border-radius: 16px;
            margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            transition: var(--transition); border: 1px solid rgba(255,255,255,0.5);
        }
        .job-item:hover { transform: translateY(-4px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }
        
        .job-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
        .job-header h4 { font-size: 18px; font-weight: 700; color: var(--text-dark); }
        
        .job-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 15px 0; }
        .detail-item { display: flex; flex-direction: column; gap: 4px; }
        .detail-label { font-weight: 700; color: var(--primary); font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;}
        .detail-value { color: var(--text-dark); font-weight: 500; }

        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: var(--text-dark); font-size: 14px;}
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 14px 16px; border: 2px solid rgba(255,255,255,0.8);
            border-radius: 14px; font-size: 15px; font-family: 'Outfit', sans-serif;
            background: rgba(255,255,255,0.6); transition: var(--transition);
        }
        .form-group textarea { min-height: 120px; resize: vertical; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
            background: white;
        }

        .form-actions { display: flex; gap: 15px; margin-top: 10px; }
        .btn-submit, .btn-accept, .btn-update { flex: 1; background: linear-gradient(135deg, var(--primary), var(--secondary)); }
        .btn-reject { flex: 1; background: linear-gradient(135deg, var(--danger), #f87171); }

        .status-message {
            padding: 16px 24px; border-radius: 16px; margin-bottom: 25px;
            display: none; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1); border-left: 5px solid;
        }
        .status-message.success { background: white; border-left-color: var(--success); color: #064e3b; }
        .status-message.error { background: white; border-left-color: var(--danger); color: #7f1d1d; }
        .status-message.show { display: block; }

        .worker-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px; }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white; padding: 25px; border-radius: 20px; text-align: center;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.25); position: relative; overflow: hidden;
        }
        .stat-card::after {
            content: ''; position: absolute; top: -50%; right: -50%; bottom: -50%; left: -50%;
            background: linear-gradient(to bottom right, rgba(255,255,255,0.2), rgba(255,255,255,0));
            transform: rotate(30deg);
        }
        .stat-number { font-size: 42px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-label { font-size: 15px; font-weight: 600; opacity: 0.9; }

        .empty-message { text-align: center; padding: 40px; color: var(--text-light); font-weight: 600; background: rgba(255,255,255,0.5); border-radius: 16px; border: 2px dashed rgba(255,255,255,0.8); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-15px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 768px) {
            body { padding: 15px 10px; }
            .header { flex-direction: column; text-align: center; gap: 20px; }
            .header-actions { width: 100%; justify-content: center; }
            .tabs { flex-direction: column; }
            .stat-card { padding: 15px; }
            .stat-number { font-size: 28px; }
        }
"""

update_css('dashboard.html', dashboard_css)
update_css('gig_worker_dashboard.html', gig_worker_css)
