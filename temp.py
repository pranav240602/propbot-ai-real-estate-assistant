import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="PropBot - Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PropBot - Real Estate AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

/* LOGIN PAGE */
.login-page {
    width: 100%;
    min-height: 100vh;
    background-color: #1e3a8a;
    background-image: 
        linear-gradient(135deg, rgba(30, 58, 138, 0.50), rgba(15, 23, 42, 0.55)),
        url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyMCIgaGVpZ2h0PSIxMDgwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0ic2t5IiB4MT0iMCUiIHkxPSIwJSIgeDI9IjAlIiB5Mj0iMTAwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3R5bGU9InN0b3AtY29sb3I6I2ZmYTU2MztzdG9wLW9wYWNpdHk6MSIvPjxzdG9wIG9mZnNldD0iNTAlIiBzdHlsZT0ic3RvcC1jb2xvcjojZmY3YTU5O3N0b3Atb3BhY2l0eToxIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojNGU1NDc1O3N0b3Atb3BhY2l0eToxIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjE5MjAiIGhlaWdodD0iMTA4MCIgZmlsbD0idXJsKCNza3kpIi8+PGcgb3BhY2l0eT0iMC44Ij48cmVjdCB4PSI1MCIgeT0iNzAwIiB3aWR0aD0iMTgyMCIgaGVpZ2h0PSIzODAiIGZpbGw9IiMyYTNiNGYiLz48cmVjdCB4PSIyMDAiIHk9IjQwMCIgd2lkdGg9IjgwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iIzFhMjUzMyIvPjxyZWN0IHg9IjMwMCIgeT0iMzUwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjM1MCIgZmlsbD0iIzFhMjUzMyIvPjxyZWN0IHg9IjQyMCIgeT0iMzAwIiB3aWR0aD0iMTIwIiBoZWlnaHQ9IjQwMCIgZmlsbD0iIzFhMjUzMyIvPjxyZWN0IHg9IjU2MCIgeT0iMjUwIiB3aWR0aD0iMTQwIiBoZWlnaHQ9IjQ1MCIgZmlsbD0iIzFhMjUzMyIvPjxyZWN0IHg9IjcyMCIgeT0iMTUwIiB3aWR0aD0iMTgwIiBoZWlnaHQ9IjU1MCIgZmlsbD0iIzJhNDA1NSIvPjxyZWN0IHg9IjkyMCIgeT0iMjAwIiB3aWR0aD0iMTYwIiBoZWlnaHQ9IjUwMCIgZmlsbD0iIzFhMjUzMyIvPjxyZWN0IHg9IjExMDAiIHk9IjI4MCIgd2lkdGg9IjEyMCIgaGVpZ2h0PSI0MjAiIGZpbGw9IiMxYTI1MzMiLz48cmVjdCB4PSIxMjQwIiB5PSIzMjAiIHdpZHRoPSIxMDAiIGhlaWdodD0iMzgwIiBmaWxsPSIjMWEyNTMzIi8+PHJlY3QgeD0iMTM2MCIgeT0iMzgwIiB3aWR0aD0iOTAiIGhlaWdodD0iMzIwIiBmaWxsPSIjMWEyNTMzIi8+PHJlY3QgeD0iMTQ3MCIgeT0iNDIwIiB3aWR0aD0iODAiIGhlaWdodD0iMjgwIiBmaWxsPSIjMWEyNTMzIi8+PHJlY3QgeD0iNzIwIiB5PSIxNTAiIHdpZHRoPSIxODAiIGhlaWdodD0iMzAiIGZpbGw9IiNmZmQwNmYiIG9wYWNpdHk9IjAuNiIvPjxyZWN0IHg9IjI1MCIgeT0iNTAwIiB3aWR0aD0iNTAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZmZkMDZmIiBvcGFjaXR5PSIwLjQiLz48cmVjdCB4PSI0NTAiIHk9IjQ1MCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI2ZmZDA2ZiIgb3BhY2l0eT0iMC40Ii8+PHJlY3QgeD0iOTUwIiB5PSI0MDAiIHdpZHRoPSI2MCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNmZmQwNmYiIG9wYWNpdHk9IjAuNCIvPjwvZz48L3N2Zz4=');
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.login-page::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.10);
    z-index: 1;
}
.login-page::after {
    content: "";
    position: absolute;
    inset: 0;
    background: transparent;
    z-index: 0;
}
.login-page > * { position: relative; z-index: 10; }

.login-container {
    background: transparent;
    backdrop-filter: blur(50px);
    -webkit-backdrop-filter: blur(50px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 24px;
    padding: 48px 40px;
    width: 90%;
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25), 
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    position: relative;
    z-index: 10;
    animation: slideUp 0.6s ease-out;
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.login-header {
    text-align: center;
    margin-bottom: 32px;
}
.login-logo {
    font-size: 56px;
    margin-bottom: 12px;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}
.login-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.login-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.form-field {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.form-field label {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.form-field input {
    padding: 14px 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    font-size: 15px;
    transition: all 0.3s;
    background: rgba(255, 255, 255, 0.9);
    color: #1e293b;
}
.form-field input::placeholder {
    color: #94a3b8;
}
.form-field input:focus {
    outline: none;
    border-color: rgba(102, 126, 234, 0.8);
    box-shadow: 0 0 0 4px rgba(102,126,234,0.2);
    background: rgba(255, 255, 255, 0.95);
}

.login-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}
.remember-me {
    display: flex;
    align-items: center;
    gap: 6px;
    color: rgba(255, 255, 255, 0.9);
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.remember-me input {
    width: 16px;
    height: 16px;
    cursor: pointer;
}
.forgot-password {
    color: #93c5fd;
    text-decoration: none;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.forgot-password:hover {
    text-decoration: underline;
    color: #bfdbfe;
}

.login-btn {
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    margin-top: 8px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.login-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.6);
}
.login-btn:active {
    transform: translateY(0);
}

.guest-btn {
    padding: 16px;
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    margin-top: 12px;
    width: 100%;
    backdrop-filter: blur(10px);
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.guest-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.6);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
}
.guest-btn:active {
    transform: translateY(0);
}

.divider {
    display: none;
}

.social-login {
    display: none;
}

.signup-link {
    display: none;
}

.error-message {
    background: rgba(254, 226, 226, 0.95);
    color: #991b1b;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 13px;
    display: none;
    margin-bottom: 16px;
    border: 1px solid rgba(239, 68, 68, 0.3);
    backdrop-filter: blur(10px);
}

/* MAIN WEBSITE */
.main-website {
    width: 100%;
    min-height: 100vh;
    background-image: url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1400&q=80');
    background-size: cover;
    background-position: center;
    position: relative;
    color: white;
    display: none;
}
.main-website::before {
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(135deg, rgba(15,23,42,0.85), rgba(30,64,175,0.85));
}
.main-website > * { position:relative; z-index:1; }

.top-nav{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:20px 60px;
}
.logo{font-size:22px;font-weight:700;letter-spacing:0.03em;}
.nav-links{display:flex;gap:16px;align-items:center;}
.nav-link{
    color:#e5e7eb;
    text-decoration:none;
    padding:8px 16px;
    border-radius:999px;
    border:1px solid transparent;
    font-size:14px;
    cursor:pointer;
}
.nav-link:hover{border-color:rgba(255,255,255,0.4);background:rgba(15,23,42,0.4);}
.nav-link.active{background:white;color:#1e3a8a;}
.user-profile {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.15);
    border-radius: 999px;
    cursor: pointer;
}
.user-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.logout-btn {
    padding: 6px 14px;
    background: rgba(239,68,68,0.2);
    border: 1px solid rgba(239,68,68,0.4);
    color: #fecaca;
    border-radius: 999px;
    font-size: 13px;
    cursor: pointer;
}
.logout-btn:hover {
    background: rgba(239,68,68,0.3);
}

.hero-section{padding:80px 60px 40px;max-width:760px;}
.hero-title{font-size:44px;font-weight:800;margin-bottom:12px;}
.hero-subtitle{font-size:16px;opacity:0.9;margin-bottom:24px;}
.search-container{
    background:rgba(15,23,42,0.9);
    border-radius:999px;
    padding:6px 8px;
    display:flex;
    gap:8px;
    align-items:center;
    box-shadow:0 18px 40px rgba(15,23,42,0.7);
}
.search-input{
    flex:1;border:none;background:transparent;color:white;
    font-size:15px;padding:10px 16px;
}
.search-input::placeholder{color:#9ca3af;}
.search-input:focus{outline:none;}
.search-btn{
    padding:10px 20px;
    border-radius:999px;
    border:none;
    background:linear-gradient(135deg,#60a5fa,#2563eb);
    color:white;
    font-weight:600;
    cursor:pointer;
    font-size:14px;
}

.hero-result{
    margin-top:18px;
    padding:16px 20px;
    background:rgba(15,23,42,0.85);
    border-radius:16px;
    border:1px solid rgba(148,163,184,0.6);
    display:none;
}
.hero-result-title{
    font-size:13px;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:#93c5fd;
    margin-bottom:6px;
}
.hero-result-body{font-size:14px;color:#e5e7eb;}

.properties-section{padding:10px 60px 60px;}
.section-title{font-size:20px;font-weight:700;margin-bottom:16px;}
.properties-grid{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:18px;
}
.property-card{
    background:rgba(15,23,42,0.9);
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 16px 32px rgba(15,23,42,0.7);
    border:1px solid rgba(148,163,184,0.7);
}
.property-image{height:160px;background-size:cover;background-position:center;}
.property-info{padding:16px 18px;}
.property-price{font-size:22px;font-weight:700;color:#bfdbfe;margin-bottom:6px;}
.property-details{font-size:13px;color:#cbd5f5;margin-bottom:4px;}
.property-actions{margin-top:8px;display:flex;gap:8px;}
.property-btn{
    flex:1;padding:8px 10px;border-radius:999px;border:none;
    font-size:12px;cursor:pointer;font-weight:500;
}
.save-btn{background:#f97316;color:white;}
.more-btn{background:#0f172a;color:#e5e7eb;border:1px solid rgba(148,163,184,0.5);}

.loading{font-size:14px;}

/* Left menu */
.menu-button{
    position:fixed;top:85px;left:20px;width:50px;height:50px;
    background:white;border:none;border-radius:50%;
    cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.15);
    z-index:1000;font-size:24px;
}
.dropdown-menu{
    position:fixed;top:145px;left:20px;width:360px;max-height:85vh;
    background:white;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.2);
    z-index:1000;display:none;overflow-y:auto;
}
.dropdown-menu.active{display:block;}

/* PropBot button */
.propbot-button{
    position:fixed;bottom:30px;right:30px;width:70px;height:70px;
    background:linear-gradient(135deg,#5b5fc7,#3b3f8f);
    border:none;border-radius:50%;cursor:pointer;
    box-shadow:0 8px 24px rgba(91,95,199,0.5);
    z-index:1100;font-size:36px;color:white;
    display:flex;align-items:center;justify-content:center;
}
.propbot-button:hover{transform:scale(1.08);}

/* Copilot overlay */
.copilot-overlay{
    position:fixed;inset:0;
    background:rgba(15,23,42,0.68);
    display:none;
    align-items:center;
    justify-content:center;
    z-index:1200;
}
.copilot-window{
    width:94vw;height:88vh;background:white;
    border-radius:18px;overflow:hidden;display:flex;
    box-shadow:0 24px 80px rgba(15,23,42,0.9);
}
.copilot-container{display:flex;flex:1;height:100%;}

/* Chat column */
.propbot-section{
    width:34%;background:white;
    display:flex;flex-direction:column;
    border-right:1px solid #e5e7eb;
}
.chat-header{
    background:linear-gradient(135deg,#5b5fc7 0%,#3b3f8f 100%);
    color:white;padding:16px 20px;
    display:flex;align-items:center;justify-content:space-between;
}
.chat-header-left{display:flex;align-items:center;gap:12px;}
.chat-avatar{
    width:44px;height:44px;background:#3b3f8f;
    border-radius:50%;display:flex;align-items:center;justify-content:center;
    font-size:24px;
}
.chat-info{display:flex;flex-direction:column;gap:4px;}
.chat-name{font-size:17px;font-weight:600;}
.online-status{display:flex;align-items:center;font-size:13px;opacity:0.9;}
.online-dot{
    width:8px;height:8px;background:#10b981;border-radius:50%;
    margin-right:6px;animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.5;}}
.header-btn{
    width:36px;height:36px;border-radius:50%;border:none;
    background:rgba(255,255,255,0.22);color:white;
    cursor:pointer;font-size:18px;
}

.chat-messages{
    flex:1;overflow-y:auto;padding:16px 20px;background:#f8fafc;
}
.message{margin-bottom:16px;display:flex;}
.message.bot{justify-content:flex-start;}
.message.user{justify-content:flex-end;}
.message-bubble{
    max-width:75%;padding:10px 14px;border-radius:14px;
    font-size:14px;line-height:1.5;white-space:pre-wrap;
}
.message.bot .message-bubble{
    background:white;color:#1e293b;
    border:1px solid #e2e8f0;
    box-shadow:0 2px 4px rgba(0,0,0,0.05);
}
.message.user .message-bubble{
    background:linear-gradient(135deg,#5b5fc7 0%,#3b3f8f 100%);
    color:white;
}

.quick-replies{
    padding:10px 16px 6px;background:white;
    border-top:1px solid #e2e8f0;display:flex;flex-wrap:wrap;gap:6px;
}
.quick-reply-btn{
    background:linear-gradient(135deg,#5b5fc7 0%,#3b3f8f 100%);
    color:white;border:none;border-radius:999px;
    padding:6px 12px;font-size:12px;cursor:pointer;
}

.search-form,.predict-form{
    padding:16px 18px;background:#f8fafc;display:none;
    overflow-y:auto;max-height:320px;
}
.search-form.active,.predict-form.active{display:block;}
.form-group{margin-bottom:14px;}
.form-label{display:block;font-size:13px;font-weight:600;color:#334155;margin-bottom:6px;}
.form-select,.form-input{
    width:100%;padding:10px;border-radius:8px;
    border:1px solid #e2e8f0;font-size:14px;
}
.form-submit{
    width:100%;padding:12px;border-radius:10px;border:none;
    background:linear-gradient(135deg,#5b5fc7 0%,#3b3f8f 100%);
    color:white;font-weight:600;cursor:pointer;
}

.chat-nav-bar{
    padding:8px 16px;background:white;
    border-top:1px solid #e2e8f0;display:flex;gap:8px;
}
.nav-icon-btn{
    flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;
    padding:8px 4px;background:#f8fafc;
    border:1px solid #e2e8f0;border-radius:12px;
    cursor:pointer;font-size:11px;color:#64748b;
}
.nav-icon-btn span{font-size:11px;}
.nav-icon-btn.active{
    background:linear-gradient(135deg,#5b5fc7 0%,#3b3f8f 100%);
    color:white;
}

.chat-input-area{
    padding:14px 16px;background:white;border-top:1px solid #e2e8f0;
}
.input-wrapper{
    display:flex;gap:8px;align-items:center;
    background:#f8fafc;border:2px solid #e2e8f0;
    border-radius:24px;padding:4px 8px 4px 14px;
}
.message-input{
    flex:1;padding:8px 4px;border:none;background:none;
    font-size:14px;outline:none;
}
.send-btn{
    width:32px;height:32px;border-radius:50%;border:none;
    background:linear-gradient(135deg,#5b5fc7,#3b3f8f);
    color:white;cursor:pointer;font-size:16px;
}

/* Listings column */
.listings-section{
    width:33%;border-right:1px solid #e5e7eb;
    display:flex;flex-direction:column;
}
.listings-header{
    padding:14px 16px;border-bottom:1px solid #e5e7eb;
    display:flex;justify-content:space-between;align-items:baseline;
}
.listings-title{font-size:15px;font-weight:600;color:#0f172a;}
.listings-count{font-size:12px;color:#6b7280;}
#propertyListings{
    flex:1;overflow-y:auto;padding:10px 14px;background:#f9fafb;
}
.listing-card{
    background:white;border-radius:12px;padding:10px 12px;
    margin-bottom:8px;border:1px solid #e5e7eb;cursor:pointer;
}
.listing-card:hover{border-color:#4f46e5;box-shadow:0 4px 10px rgba(79,70,229,0.12);}
.listing-title{font-size:14px;font-weight:600;margin-bottom:4px;}
.listing-meta{font-size:12px;color:#6b7280;margin-bottom:4px;}
.listing-score{font-size:12px;color:#16a34a;font-weight:600;}

/* Map column */
.map-section{width:33%;display:flex;flex-direction:column;}
.map-header{
    padding:14px 16px;border-bottom:1px solid #e5e7eb;
    display:flex;align-items:center;justify-content:space-between;
}
.map-title{font-size:15px;font-weight:600;color:#0f172a;}
#mapView{flex:1;}

/* scrollbars */
.chat-messages::-webkit-scrollbar,
#propertyListings::-webkit-scrollbar,
.dropdown-menu::-webkit-scrollbar{
    width:6px;
}
.chat-messages::-webkit-scrollbar-thumb,
#propertyListings::-webkit-scrollbar-thumb,
.dropdown-menu::-webkit-scrollbar-thumb{
    background:#cbd5e1;border-radius:999px;
}
</style>
</head>

<body>

<!-- LOGIN PAGE -->
<div class="login-page" id="loginPage">
    <div class="login-container">
        <div class="login-header">
            <div class="login-logo">🏠</div>
            <h1 class="login-title">Welcome to PropBot</h1>
            <p class="login-subtitle">Your AI-powered real estate companion</p>
        </div>
        
        <div class="error-message" id="errorMessage"></div>
        
        <form class="login-form" onsubmit="handleLogin(event)">
            <div class="form-field">
                <label for="loginEmail">Email or Username</label>
                <input type="text" id="loginEmail" placeholder="Enter your email" required>
            </div>
            
            <div class="form-field">
                <label for="loginPassword">Password</label>
                <input type="password" id="loginPassword" placeholder="Enter your password" required>
            </div>
            
            <div class="login-options">
                <label class="remember-me">
                    <input type="checkbox" id="rememberMe">
                    <span>Remember me</span>
                </label>
                <a href="#" class="forgot-password">Forgot password?</a>
            </div>
            
            <button type="submit" class="login-btn">Log in</button>
            <button type="button" class="guest-btn" onclick="loginAsGuest()">Continue as Guest</button>
        </form>
    </div>
</div>

<!-- MAIN WEBSITE -->
<div class="main-website" id="mainWebsite">
    <div class="top-nav">
        <div class="logo">🏠 PropBot Real Estate</div>
        <div class="nav-links">
            <a class="nav-link active" data-mode="buy" onclick="selectNav('buy')">Buy</a>
            <a class="nav-link" data-mode="rent" onclick="selectNav('rent')">Rent</a>
            <a class="nav-link" data-mode="sell" onclick="selectNav('sell')">Sell</a>
            <div class="user-profile">
                <div class="user-avatar" id="userAvatar">👤</div>
                <span id="userName">User</span>
            </div>
            <button class="logout-btn" onclick="handleLogout()">Logout</button>
        </div>
    </div>

    <div class="hero-section">
        <h1 class="hero-title">Find Your Dream Home</h1>
        <p class="hero-subtitle">Discover the perfect property in Boston with PropBot AI.</p>
        <div class="search-container">
            <input type="text" class="search-input" id="heroInput"
                   placeholder="Search homes to buy in Boston (e.g., 3 BR in Back Bay under $1M)">
            <button class="search-btn" id="heroSearchBtn">🔍 Search</button>
        </div>
        <div class="hero-result" id="heroResult">
            <div class="hero-result-title">AI Property Insight</div>
            <div class="hero-result-body" id="heroResultBody"></div>
        </div>
    </div>

    <div class="properties-section">
        <h2 class="section-title">Featured Properties</h2>
        <div class="properties-grid" id="featuredProperties">
            <div class="loading" style="text-align:center;padding:40px;color:white;">
                Loading properties from PropBot AI...
            </div>
        </div>
    </div>
</div>

<button class="menu-button" onclick="toggleMenu()">⋮</button>

<div id="dropdownMenu" class="dropdown-menu">
    <div style="padding:20px;background:linear-gradient(135deg,#1e40af,#1e3a8a);color:white;font-size:18px;font-weight:600;position:sticky;top:0;">
        PropBot Menu
    </div>
    <div style="padding:16px;">
        <div style="padding:14px;margin-bottom:8px;background:#f8fafc;border-radius:8px;cursor:pointer;"
             onclick="showDash()">📊 Market Analytics</div>
        <div style="padding:14px;margin-bottom:8px;background:#f8fafc;border-radius:8px;cursor:pointer;"
             onclick="showCalc()">🧮 Commute Calculator</div>
        <div style="padding:14px;margin-bottom:8px;background:#f8fafc;border-radius:8px;cursor:pointer;"
             onclick="showHist()">💬 Chat History</div>

        <div id="dashSection" style="display:none;margin-top:12px;"></div>

        <div id="calcSection" style="display:none;margin-top:12px;padding:20px;background:#f8fafc;border-radius:8px;">
            <input type="text" id="propAddr" placeholder="Property address"
                   style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #e2e8f0;border-radius:6px;">
            <select id="destSelect"
                    style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #e2e8f0;border-radius:6px;">
                <option value="">Select destination</option>
            </select>
            <button onclick="calcCommute()"
                    style="width:100%;padding:12px;background:#1e40af;color:white;border:none;border-radius:6px;font-weight:600;cursor:pointer;">
                Calculate
            </button>
            <div id="commuteResult" style="display:none;margin-top:12px;padding:12px;background:white;border-radius:6px;"></div>
        </div>

        <div id="histSection" style="display:none;margin-top:12px;"></div>
    </div>
</div>

<button class="propbot-button" onclick="openCopilot()">💬</button>

<div class="copilot-overlay" id="copilotOverlay">
  <div class="copilot-window">
    <div class="copilot-container">
      <div class="propbot-section">
        <div class="chat-header">
          <div class="chat-header-left">
            <div class="chat-avatar">🤖</div>
            <div class="chat-info">
              <div class="chat-name">PropBot Copilot</div>
              <div class="online-status"><span class="online-dot"></span>Online · Boston real estate</div>
            </div>
          </div>
          <div>
            <button class="header-btn" onclick="showHome()">⌂</button>
            <button class="header-btn" onclick="closeCopilot()">✕</button>
          </div>
        </div>

        <div class="chat-messages" id="chatMessages"></div>

        <div class="search-form" id="searchForm">
            <div class="form-group">
                <label class="form-label">Neighborhood</label>
                <select id="searchNeighborhood" class="form-select">
                    <option value="">Select neighborhood</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Bedrooms</label>
                <select id="searchBedrooms" class="form-select">
                    <option value="">Any</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4+</option>
                </select>
            </div>
            <button class="form-submit" onclick="submitSearch()">🔍 Search Properties</button>
        </div>

        <div class="predict-form" id="predictForm">
            <div class="form-group">
                <label class="form-label">Neighborhood</label>
                <select id="predictNeighborhood" class="form-select">
                    <option value="">Select neighborhood</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Bedrooms</label>
                <select id="predictBedrooms" class="form-select">
                    <option value="">Select</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4+</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Bathrooms</label>
                <select id="predictBathrooms" class="form-select">
                    <option value="">Select</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4+</option>
                </select>
            </div>
            <button class="form-submit" onclick="submitPredict()">💰 Predict Price</button>
        </div>

        <div class="quick-replies" id="quickReplies"></div>

        <div class="chat-nav-bar">
            <button class="nav-icon-btn active" id="homeBtn" onclick="showHome()">🏠<span>Chat</span></button>
            <button class="nav-icon-btn" id="searchBtn" onclick="showSearch()">🔍<span>Search</span></button>
            <button class="nav-icon-btn" id="predictBtn" onclick="showPredict()">💰<span>Predict</span></button>
        </div>

        <div class="chat-input-area" id="chatInputArea">
          <div class="input-wrapper">
            <input type="text" class="message-input" id="msgInput" placeholder="Ask me anything about Boston real estate..."
                   onkeypress="handleKey(event)">
            <button class="send-btn" onclick="sendMsg()">➤</button>
          </div>
        </div>
      </div>

      <div class="listings-section" id="listingsSection">
        <div class="listings-header">
          <div class="listings-title">Property Listings</div>
          <div class="listings-count" id="listingsCount">Loading recommendations...</div>
        </div>
        <div id="propertyListings"><div class="loading">Loading properties from PropBot...</div></div>
      </div>

      <div class="map-section">
        <div class="map-header">
          <div class="map-title">🗺️ Property Map</div>
        </div>
        <div id="mapView"></div>
      </div>
    </div>
  </div>
</div>

<script>
// ✅ BACKEND URL (matches uvicorn log: 127.0.0.1:8000)
const API = 'http://127.0.0.1:8000';

let map, markers = [], selectedIdx = -1, properties = [], neighborhoods = [];
let copilotInitialized = false;
let currentUser = null;

// LOGIN SYSTEM
function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const remember = document.getElementById('rememberMe').checked;
    
    // Simple validation (in production, this would be server-side)
    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }
    
    // Demo credentials (in production, validate against backend)
    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }
    
    // Extract username from email
    const username = email.split('@')[0] || email;
    
    // Store user data
    currentUser = {
        email: email,
        username: username,
        fullName: username.charAt(0).toUpperCase() + username.slice(1)
    };
    
    if (remember) {
        localStorage.setItem('propbot_user', JSON.stringify(currentUser));
    } else {
        sessionStorage.setItem('propbot_user', JSON.stringify(currentUser));
    }
    
    // Show main website
    showMainWebsite();
}

function loginAsGuest() {
    // Auto-login as guest user
    currentUser = {
        email: 'guest@propbot.com',
        username: 'guest',
        fullName: 'Guest User'
    };
    
    sessionStorage.setItem('propbot_user', JSON.stringify(currentUser));
    showMainWebsite();
}

function socialLogin(provider) {
    // Demo social login
    currentUser = {
        email: `user@${provider}.com`,
        username: `${provider}_user`,
        fullName: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`
    };
    
    sessionStorage.setItem('propbot_user', JSON.stringify(currentUser));
    showMainWebsite();
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}

function showSignup() {
    alert('Sign up feature coming soon! For demo, use any email and password (6+ characters).');
}

function showMainWebsite() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainWebsite').style.display = 'block';
    document.querySelector('.menu-button').style.display = 'block';
    document.querySelector('.propbot-button').style.display = 'flex';
    
    // Update user info in nav
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.fullName;
        document.getElementById('userAvatar').textContent = currentUser.fullName.charAt(0);
    }
    
    // Initialize main website
    selectNav('buy');
    loadFeatured();
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        currentUser = null;
        localStorage.removeItem('propbot_user');
        sessionStorage.removeItem('propbot_user');
        
        document.getElementById('mainWebsite').style.display = 'none';
        document.getElementById('loginPage').style.display = 'flex';
        document.querySelector('.menu-button').style.display = 'none';
        document.querySelector('.propbot-button').style.display = 'none';
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
        document.getElementById('rememberMe').checked = false;
    }
}

// Check for stored user on load
function checkStoredUser() {
    const storedUser = localStorage.getItem('propbot_user') || sessionStorage.getItem('propbot_user');
    if (storedUser) {
        currentUser = JSON.parse(storedUser);
        showMainWebsite();
    }
}

async function safeFetchJson(url, options = {}, context = 'request') {
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status} for ${context}: ${text}`);
        }
        return await res.json();
    } catch (e) {
        console.error(`❌ ${context} failed:`, e);
        throw e;
    }
}

/* NAV + HERO */
function selectNav(mode){
    document.querySelectorAll('.nav-link').forEach(l=>l.classList.remove('active'));
    const active = document.querySelector(`.nav-link[data-mode="${mode}"]`);
    if(active) active.classList.add('active');
}
async function heroSearch(){
    const q = document.getElementById('heroInput').value.trim();
    if(!q) return;
    const btn = document.getElementById('heroSearchBtn');
    const original = btn.innerText;
    btn.disabled = true; btn.innerText = "Searching...";
    const box = document.getElementById('heroResult');
    const body = document.getElementById('heroResultBody');
    box.style.display = 'block';
    body.innerText = "Thinking with RAG over Boston property data...";
    try{
        const data = await safeFetchJson(`${API}/search`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:q,user_id:currentUser?.username || 'default_user'})
        }, '/search');
        body.innerText = data.answer || "I couldn't find anything specific, try rephrasing your query.";
    }catch(e){
        body.innerText = "Error: " + e.message;
    }finally{
        btn.disabled = false; btn.innerText = original;
    }
}

/* LEFT MENU */
function toggleMenu(){
    document.getElementById('dropdownMenu').classList.toggle('active');
}
function hideAllMenuSections(){
    document.getElementById('dashSection').style.display='none';
    document.getElementById('calcSection').style.display='none';
    document.getElementById('histSection').style.display='none';
}
async function showDash(){
    hideAllMenuSections();
    const sec = document.getElementById('dashSection');
    sec.style.display='block';
    sec.innerHTML='<div style="text-align:center;padding:20px;color:#64748b;">Loading dashboard...</div>';
    try{
        const data = await safeFetchJson(`${API}/analytics/dashboard`,{}, '/analytics/dashboard');
        sec.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:12px;">
                <div style="padding:12px;background:#0f172a;color:white;border-radius:10px;">
                    <div style="font-size:11px;opacity:0.8;">Total Properties</div>
                    <div style="font-size:18px;font-weight:700;">${data.total_properties.toLocaleString()}</div>
                </div>
                <div style="padding:12px;background:#0f172a;color:white;border-radius:10px;">
                    <div style="font-size:11px;opacity:0.8;">Total Searches</div>
                    <div style="font-size:18px;font-weight:700;">${data.total_searches}</div>
                </div>
            </div>
            <div style="padding:12px;background:white;border-radius:10px;margin-bottom:12px;">
                <div style="font-size:13px;font-weight:600;color:#64748b;margin-bottom:8px;">Hottest Neighborhoods</div>
                ${data.hottest_neighborhoods.slice(0,3).map(h=>`
                    <div style="padding:8px;background:#f8fafc;border-radius:6px;margin-bottom:6px;">
                        <div style="font-size:13px;font-weight:600;">${h.name}</div>
                        <div style="font-size:12px;color:#64748b;">$${h.avg_price.toLocaleString()}</div>
                    </div>`).join('')}
            </div>
            <div style="padding:12px;background:white;border-radius:10px;">
                <div style="font-size:13px;font-weight:600;color:#64748b;margin-bottom:8px;">Market Insights</div>
                <div style="font-size:12px;line-height:1.6;color:#334155;">
                    🚀 ${data.market_insights.fastest_growing}<br>
                    💎 ${data.market_insights.best_value}<br>
                    🏆 ${data.market_insights.most_competitive}<br>
                    💼 ${data.market_insights.investment_opportunity}
                </div>
            </div>`;
    }catch(e){
        sec.innerHTML = `<div style="color:#ef4444;padding:20px;text-align:center;">Error loading dashboard: ${e.message}</div>`;
    }
}
async function showCalc(){
    hideAllMenuSections();
    const sec = document.getElementById('calcSection');
    sec.style.display='block';
    try{
        const data = await safeFetchJson(`${API}/commute-destinations`,{}, '/commute-destinations');
        document.getElementById('destSelect').innerHTML =
            '<option value="">Select destination</option>' +
            data.destinations.map(d=>`<option value="${d.id}">${d.name}</option>`).join('');
    }catch(e){
        // show nothing special
    }
}
async function calcCommute(){
    const prop = document.getElementById('propAddr').value.trim();
    const dest = document.getElementById('destSelect').value;
    if(!prop || !dest){alert('Fill both property address and destination');return;}
    try{
        const data = await safeFetchJson(
            `${API}/commute-time?property_address=${encodeURIComponent(prop)}&destination=${encodeURIComponent(dest)}`,
            {method:'POST',headers:{'Content-Type':'application/json'}},
            '/commute-time'
        );
        document.getElementById('commuteResult').innerHTML = `
            <div style="font-weight:600;margin-bottom:8px;">${data.from} → ${data.to}</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:8px;">Distance: ${data.distance_miles} miles</div>
            <div style="font-size:12px;">
                🚗 Driving: ${data.commute_options.driving.time_display}<br>
                🚇 Transit: ${data.commute_options.transit.time_display}<br>
                🚴 Biking: ${data.commute_options.biking.time_display}<br>
                🚶 Walking: ${data.commute_options.walking.time_display}
            </div>`;
        document.getElementById('commuteResult').style.display='block';
    }catch(e){
        alert('Error calculating commute: ' + e.message);
    }
}
async function showHist(){
    hideAllMenuSections();
    const sec = document.getElementById('histSection');
    sec.style.display='block';
    sec.innerHTML='<div style="text-align:center;padding:20px;color:#64748b;">Loading chat history...</div>';
    try{
        const data = await safeFetchJson(`${API}/chat-history/${currentUser?.username || 'default_user'}?limit=10`,{},'/chat-history');
        if(data.total_chats===0){
            sec.innerHTML='<div style="text-align:center;color:#94a3b8;padding:20px;">No chat history yet</div>';
        }else{
            sec.innerHTML = data.chats.map(chat=>`
                <div style="padding:12px;background:white;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:8px;">
                    <div style="font-weight:600;color:#1e293b;margin-bottom:4px;">📝 ${chat.query.substring(0,60)}${chat.query.length>60?'...':''}</div>
                    <div style="font-size:12px;color:#94a3b8;">${new Date(chat.timestamp).toLocaleString()}</div>
                </div>`).join('');
        }
    }catch(e){
        sec.innerHTML=`<div style="color:#ef4444;padding:20px;text-align:center;">Error loading history: ${e.message}</div>`;
    }
}

/* FEATURED */
async function loadFeatured(){
    try{
        const data = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({})
        }, '/recommendations/by-features (featured)');
        document.getElementById('featuredProperties').innerHTML =
            data.recommendations.slice(0,3).map((r,i)=>`
                <div class="property-card">
                    <div class="property-image" style="background-image:url('https://source.unsplash.com/800x600/?boston,house,${i}')"></div>
                    <div class="property-info">
                        <div class="property-price">Match: ${(r.match_score*100).toFixed(0)}%</div>
                        <div class="property-details">${r.description.substring(0,120)}...</div>
                        <div class="property-details">ID: ${r.property_id}</div>
                        <div class="property-actions">
                            <button class="property-btn save-btn" onclick="saveProp('${r.property_id}')">💾 Save</button>
                            <button class="property-btn more-btn" onclick="openCopilotFromProperty('${r.property_id}')">More like this</button>
                        </div>
                    </div>
                </div>`).join('');
    }catch(e){
        document.getElementById('featuredProperties').innerHTML =
            `<div style="color:white;text-align:center;padding:40px;">Error loading featured properties: ${e.message}</div>`;
    }
}
async function saveProp(id){
    try{
        await safeFetchJson(`${API}/save-property`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({property_id:id,property_data:{},user_id:currentUser?.username || 'default_user'})
        }, '/save-property');
        alert('Property saved!');
    }catch(e){
        alert('Error saving property: ' + e.message);
    }
}

/* COPILOT */
function openCopilot(){
    document.getElementById('copilotOverlay').style.display='flex';
    if(!copilotInitialized){
        initCopilot();
        copilotInitialized=true;
    }
}
function closeCopilot(){
    document.getElementById('copilotOverlay').style.display='none';
}
function openCopilotFromProperty(id){
    openCopilot();
    addMsg('user', `Show me similar properties to ${id}`);
    sendMessage(`Show me similar properties to ${id}`);
}

async function initCopilot(){
    initMap();
    await loadNeighborhoods();
    await loadSampleQueries();
    await loadInitialProperties();
    showHome();
    addMsg('bot',`Hi ${currentUser?.fullName || 'there'}! I'm PropBot. Ask me anything about Boston neighborhoods, prices, or commute.`);
}
function initMap(){
    map = L.map('mapView').setView([42.3601,-71.0589],12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
        attribution:'© OpenStreetMap'
    }).addTo(map);
}
async function loadNeighborhoods(){
    neighborhoods = [
        "Back Bay","Beacon Hill","South End","Dorchester",
        "Jamaica Plain","Charlestown","East Boston","Roxbury"
    ];
    const options = neighborhoods.map(h=>`<option value="${h}">${h}</option>`).join('');
    document.getElementById('searchNeighborhood').innerHTML='<option value="">Select neighborhood</option>'+options;
    document.getElementById('predictNeighborhood').innerHTML='<option value="">Select neighborhood</option>'+options;
}
async function loadSampleQueries(){
    try{
        const data = await safeFetchJson(`${API}/sample-queries`,{}, '/sample-queries');
        document.getElementById('quickReplies').innerHTML =
            data.queries.slice(0,4).map(q=>`
                <button class="quick-reply-btn" onclick="quickMsg('${q.replace(/'/g,"\\'")}')">${q}</button>`).join('');
    }catch(e){
        console.error('sample-queries error:',e);
    }
}
async function loadInitialProperties(){
    try{
        const data = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({})
        }, '/recommendations/by-features (copilot initial)');
        properties = data.recommendations.map((r,i)=>({
            id:r.property_id,
            name:"Property " + (i+1),
            description:r.description,
            score:r.match_score,
            lat:42.34 + 0.02*i,
            lng:-71.08 + 0.02*i
        }));
        renderListings();
        updateMap();
    }catch(e){
        document.getElementById('propertyListings').innerHTML =
            `<div class="loading">Error loading properties: ${e.message}</div>`;
        document.getElementById('listingsCount').innerText = '0 matches';
    }
}
function renderListings(){
    const list = document.getElementById('propertyListings');
    if(properties.length===0){
        list.innerHTML='<div class="loading">No properties yet.</div>';
        document.getElementById('listingsCount').innerText='0 matches';
        return;
    }
    list.innerHTML = properties.map((p,i)=>`
        <div class="listing-card" onclick="selectProp(${i})">
            <div class="listing-title">${p.name}</div>
            <div class="listing-meta">${p.description.substring(0,85)}...</div>
            <div class="listing-score">Match score: ${(p.score*100).toFixed(0)}%</div>
        </div>`).join('');
    document.getElementById('listingsCount').innerText = properties.length + ' matches';
}
function updateMap(){
    if(!map) return;
    markers.forEach(m=>map.removeLayer(m));
    markers=[];
    properties.forEach((p,i)=>{
        const m = L.marker([p.lat,p.lng]).addTo(map)
            .bindPopup(`<b>${p.name}</b><br>Match: ${(p.score*100).toFixed(0)}%`);
        m.on('click',()=>selectProp(i));
        markers.push(m);
    });
    if(properties.length>0){
        const bounds = L.latLngBounds(properties.map(p=>[p.lat,p.lng]));
        map.fitBounds(bounds,{padding:[40,40]});
    }
}
function selectProp(i){
    selectedIdx = i;
    const p = properties[i];
    map.setView([p.lat,p.lng],15);
    markers[i].openPopup();
}

function addMsg(type,txt){
    const c = document.getElementById('chatMessages');
    c.innerHTML += `<div class="message ${type}"><div class="message-bubble">${txt}</div></div>`;
    c.scrollTop = c.scrollHeight;
}
async function sendMsg(){
    const inp = document.getElementById('msgInput');
    const txt = inp.value.trim();
    if(!txt)return;
    addMsg('user',txt);
    inp.value='';
    document.getElementById('quickReplies').innerHTML='';
    try{
        const data = await safeFetchJson(`${API}/chat`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({query:txt,user_id:currentUser?.username || 'default_user'})
        }, '/chat');
        setTimeout(()=>addMsg('bot',data.answer),400);
        const recData = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({})
        }, '/recommendations/by-features (after chat)');
        properties = recData.recommendations.map((r,i)=>({
            id:r.property_id,
            name:"Property "+(i+1),
            description:r.description,
            score:r.match_score,
            lat:42.34+0.02*i,
            lng:-71.08+0.02*i
        }));
        renderListings();updateMap();
    }catch(e){
        setTimeout(()=>addMsg('bot','❌ Error: '+e.message),400);
    }
}
function quickMsg(txt){
    document.getElementById('msgInput').value=txt;
    sendMsg();
}
function sendMessage(txt){
    document.getElementById('msgInput').value=txt;
    sendMsg();
}
function handleKey(e){
    if(e.key==='Enter')sendMsg();
}

function showHome(){
    document.getElementById('searchForm').classList.remove('active');
    document.getElementById('predictForm').classList.remove('active');
    document.getElementById('chatMessages').style.display='block';
    document.getElementById('chatInputArea').style.display='block';
    document.querySelectorAll('.nav-icon-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('homeBtn').classList.add('active');
}
function showSearch(){
    document.getElementById('predictForm').classList.remove('active');
    document.getElementById('chatMessages').style.display='none';
    document.getElementById('chatInputArea').style.display='none';
    document.getElementById('searchForm').classList.add('active');
    document.querySelectorAll('.nav-icon-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('searchBtn').classList.add('active');
}
function showPredict(){
    document.getElementById('searchForm').classList.remove('active');
    document.getElementById('chatMessages').style.display='none';
    document.getElementById('chatInputArea').style.display='none';
    document.getElementById('predictForm').classList.add('active');
    document.querySelectorAll('.nav-icon-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('predictBtn').classList.add('active');
}
async function submitSearch(){
    const hood=document.getElementById('searchNeighborhood').value;
    const beds=document.getElementById('searchBedrooms').value;
    if(!hood||!beds){alert('Fill all fields');return;}
    showHome();
    addMsg('user',`Search ${beds}BR properties in ${hood}`);
    try{
        const data = await safeFetchJson(`${API}/search`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood,bedrooms:parseInt(beds),user_id:currentUser?.username || 'default_user'})
        }, '/search (copilot)');
        setTimeout(()=>addMsg('bot',data.answer),400);
        const recData = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood,bedrooms:parseInt(beds)})
        }, '/recommendations-by-features (search results)');
        properties = recData.recommendations.map((r,i)=>({
            id:r.property_id,
            name:`Property ${i+1} - ${hood}`,
            description:r.description,
            score:r.match_score,
            lat:42.34+0.02*i,
            lng:-71.08+0.02*i
        }));
        renderListings();updateMap();
    }catch(e){
        setTimeout(()=>addMsg('bot','❌ Error running property search: '+e.message),400);
    }
    document.getElementById('searchNeighborhood').value='';
    document.getElementById('searchBedrooms').value='';
}
async function submitPredict(){
    const hood=document.getElementById('predictNeighborhood').value;
    const beds=document.getElementById('predictBedrooms').value;
    const baths=document.getElementById('predictBathrooms').value;
    if(!hood||!beds||!baths){alert('Fill all fields');return;}
    showHome();
    addMsg('user',`Predict price for a ${beds}BR ${baths}BA home in ${hood}`);
    try{
        const data = await safeFetchJson(`${API}/predict-price`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood,bedrooms:parseInt(beds),bathrooms:parseInt(baths)})
        }, '/predict-price');
        setTimeout(()=>{
            addMsg('bot',
                `💰 Estimated Price: $${data.predicted_price.toLocaleString()}\n`+
                `📊 Confidence: ${(data.confidence*100).toFixed(0)}%\n`+
                `📈 Range: $${data.price_range.min.toLocaleString()} - $${data.price_range.max.toLocaleString()}`
            );
        },400);
    }catch(e){
        setTimeout(()=>addMsg('bot','❌ Error running price prediction: '+e.message),400);
    }
    document.getElementById('predictNeighborhood').value='';
    document.getElementById('predictBedrooms').value='';
    document.getElementById('predictBathrooms').value='';
}

/* onload */
window.addEventListener('load',()=>{
    // Hide buttons initially
    document.querySelector('.menu-button').style.display = 'none';
    document.querySelector('.propbot-button').style.display = 'none';
    
    checkStoredUser();
    document.getElementById('heroSearchBtn').addEventListener('click',heroSearch);
    document.getElementById('heroInput').addEventListener('keypress',e=>{if(e.key==='Enter')heroSearch();});
});
</script>

</body>
</html>
"""

components.html(html, height=900, scrolling=True)

st.markdown("""
<style>
    .main > div { padding: 0 !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)