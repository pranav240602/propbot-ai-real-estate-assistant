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
        renderListings();
        updateMap();
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
        renderListings();
        updateMap();
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

// Prevent page scrolling
document.addEventListener('DOMContentLoaded', function() {
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
});