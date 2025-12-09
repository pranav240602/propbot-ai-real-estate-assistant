// ✅ BACKEND URL
const API = 'http://127.0.0.1:8002';

let map, markers = [], selectedIdx = -1, properties = [], neighborhoods = [];
let copilotInitialized = false;
let currentUser = null;
let conversationHistory = [];
let currentMode = 'buy';
let autoScrollInterval = null;

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (!response.ok) {
            const error = await response.json();
            showError(error.detail || 'Login failed');
            return;
        }
        
        const data = await response.json();
        
        currentUser = {
            user_id: data.user_id,
            email: email,
            username: email.split('@')[0],
            fullName: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
            access_token: data.access_token,
            is_guest: false
        };
        
        localStorage.setItem('propbot_user', JSON.stringify(currentUser));
        showMainWebsite();
        
    } catch (e) {
        showError('Connection error: ' + e.message);
    }
}

async function loginAsGuest() {
    try {
        const response = await fetch(`${API}/auth/guest`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (!response.ok) {
            throw new Error('Guest login failed');
        }
        
        const data = await response.json();
        
        currentUser = {
            user_id: data.user_id,
            email: 'guest@propbot.com',
            username: 'guest',
            fullName: 'Guest User',
            access_token: data.access_token,
            is_guest: true,
            guest_id: data.guest_id
        };
        
        sessionStorage.setItem('propbot_user', JSON.stringify(currentUser));
        showMainWebsite();
        
    } catch (e) {
        showError('Guest login error: ' + e.message);
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupPasswordConfirm').value;
    
    if (!email || !password || !confirmPassword) {
        showSignupError('Please fill in all fields');
        return;
    }
    
    if (password.length < 6) {
        showSignupError('Password must be at least 6 characters');
        return;
    }
    
    if (password !== confirmPassword) {
        showSignupError('Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch(`${API}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (!response.ok) {
            const error = await response.json();
            showSignupError(error.detail || 'Registration failed');
            return;
        }
        
        showSignupSuccess('Account created successfully! Redirecting to login...');
        
        document.getElementById('signupEmail').value = '';
        document.getElementById('signupPassword').value = '';
        document.getElementById('signupPasswordConfirm').value = '';
        
        setTimeout(() => {
            showLoginForm();
            document.getElementById('loginEmail').value = email;
        }, 2000);
        
    } catch (e) {
        showSignupError('Connection error: ' + e.message);
    }
}

function showSignupForm() {
    document.getElementById('loginFormSection').style.display = 'none';
    document.getElementById('signupFormSection').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('signupFormSection').style.display = 'none';
    document.getElementById('loginFormSection').style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}

function showSignupError(message) {
    const errorDiv = document.getElementById('signupErrorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}

function showSignupSuccess(message) {
    const successDiv = document.getElementById('signupSuccessMessage');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 2000);
}

function showMainWebsite() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainWebsite').style.display = 'block';
    document.querySelector('.menu-button').style.display = 'block';
    document.querySelector('.propbot-button').style.display = 'flex';
    
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.fullName;
        document.getElementById('userAvatar').textContent = currentUser.fullName.charAt(0);
    }
    
    selectNav('buy');
    loadFeatured('buy');
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        currentUser = null;
        conversationHistory = [];
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

async function geocodeAddress(address) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address + ', Boston, MA')}&format=json&limit=1`,
            {headers: {'User-Agent': 'PropBotApp/1.0'}}
        );
        const data = await response.json();
        
        if (data && data.length > 0) {
            return {
                lat: parseFloat(data[0].lat),
                lng: parseFloat(data[0].lon)
            };
        }
    } catch (e) {
        console.error('Geocoding error:', e);
    }
    
    return {
        lat: 42.3601 + (Math.random() - 0.5) * 0.05,
        lng: -71.0589 + (Math.random() - 0.5) * 0.05
    };
}

function selectNav(mode){
    currentMode = mode;
    document.querySelectorAll('.nav-link').forEach(l=>l.classList.remove('active'));
    const active = document.querySelector(`.nav-link[data-mode="${mode}"]`);
    if(active) active.classList.add('active');
    
    stopAutoScroll();
    loadFeatured(mode);
}

async function heroSearch(){
    const q = document.getElementById('heroInput').value.trim();
    if(!q) return;
    const btn = document.getElementById('heroSearchBtn');
    const original = btn.innerText;
    btn.disabled = true;
    btn.innerText = "Searching...";
    const box = document.getElementById('heroResult');
    const body = document.getElementById('heroResultBody');
    box.style.display = 'block';
    body.innerText = "Searching with AI...";
    
    try{
        const data = await safeFetchJson(`${API}/search`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:q, user_id: currentUser?.user_id || 1})
        }, '/search');
        body.innerText = data.answer || "No results found.";
    }catch(e){
        body.innerText = "Error: " + e.message;
    }finally{
        btn.disabled = false;
        btn.innerText = original;
    }
}

function toggleMenu(){
    document.getElementById('dropdownMenu').classList.toggle('active');
}

function hideAllMenuSections(){
    document.getElementById('dashSection').style.display='none';
    document.getElementById('calcSection').style.display='none';
    document.getElementById('histSection').style.display='none';
    document.getElementById('savedPropsSection').style.display='none';
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
        sec.innerHTML = `<div style="color:#ef4444;padding:20px;text-align:center;">Error: ${e.message}</div>`;
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
        console.error('Commute destinations error:', e);
    }
}

async function calcCommute(){
    const prop = document.getElementById('propAddr').value.trim();
    const dest = document.getElementById('destSelect').value;
    if(!prop || !dest){
        alert('Please fill both property address and destination');
        return;
    }
    
    const resultDiv = document.getElementById('commuteResult');
    resultDiv.innerHTML = '<div style="text-align:center;padding:20px;color:#64748b;">Calculating...</div>';
    resultDiv.style.display='block';
    
    try{
        const data = await safeFetchJson(
            `${API}/commute-time?property_address=${encodeURIComponent(prop)}&destination=${encodeURIComponent(dest)}`,
            {method:'POST',headers:{'Content-Type':'application/json'}},
            '/commute-time'
        );
        
        console.log('✅ Commute data received:', data);
        
        resultDiv.innerHTML = `
            <div style="font-weight:600;margin-bottom:8px;font-size:14px;color:#1e293b;">${data.from} → ${data.to}</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #e2e8f0;">
                📍 Distance: ${data.distance_miles} miles
            </div>
            <div style="font-size:13px;line-height:2;color:#1e293b;">
                <div style="display:flex;align-items:center;margin-bottom:6px;">
                    <span style="width:30px;">🚗</span>
                    <span style="flex:1;"><strong>Driving:</strong> ${data.commute_options.driving.time_display}</span>
                </div>
                <div style="display:flex;align-items:center;margin-bottom:6px;">
                    <span style="width:30px;">🚇</span>
                    <span style="flex:1;"><strong>Transit:</strong> ${data.commute_options.transit.time_display}</span>
                </div>
                <div style="display:flex;align-items:center;margin-bottom:6px;">
                    <span style="width:30px;">🚴</span>
                    <span style="flex:1;"><strong>Biking:</strong> ${data.commute_options.biking.time_display}</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <span style="width:30px;">🚶</span>
                    <span style="flex:1;"><strong>Walking:</strong> ${data.commute_options.walking.time_display}</span>
                </div>
            </div>`;
        
        setTimeout(() => resultDiv.scrollIntoView({behavior: 'smooth', block: 'nearest'}), 100);
            
    }catch(e){
        resultDiv.innerHTML = `<div style="color:#ef4444;padding:20px;text-align:center;">Error: ${e.message}</div>`;
    }
}

async function showHist(){
    hideAllMenuSections();
    const sec = document.getElementById('histSection');
    sec.style.display='block';
    sec.innerHTML='<div style="text-align:center;padding:20px;color:#64748b;">Loading chat history...</div>';
    try{
        const userId = currentUser?.user_id || 1;
        const data = await safeFetchJson(`${API}/chat/history/${userId}`,{},'/chat/history');
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
        sec.innerHTML=`<div style="color:#ef4444;padding:20px;text-align:center;">Error: ${e.message}</div>`;
    }
}

async function showSavedProps(){
    hideAllMenuSections();
    const sec = document.getElementById('savedPropsSection');
    sec.style.display='block';
    sec.innerHTML='<div style="text-align:center;padding:20px;color:#ffffff;">Loading saved properties...</div>';
    
    try{
        const userId = currentUser?.user_id || 1;
        const data = await safeFetchJson(`${API}/saved-properties/${userId}`,{},'/saved-properties');
        
        if(data.total === 0){
            sec.innerHTML='<div style="text-align:center;color:#94a3b8;padding:20px;">No saved properties yet</div>';
        } else {
            sec.innerHTML = data.saved_properties.map((prop, idx) => `
                <div style="padding:14px;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);border-radius:8px;margin-bottom:10px;">
                    <div style="font-weight:700;color:#bfdbfe;margin-bottom:6px;font-size:16px;">Property ${prop.property_id}</div>
                    <div style="font-size:11px;color:#94a3b8;">Saved: ${new Date(prop.timestamp).toLocaleDateString()}</div>
                </div>
            `).join('');
        }
    } catch(e) {
        sec.innerHTML=`<div style="color:#ef4444;padding:20px;text-align:center;">Error: ${e.message}</div>`;
    }
}

async function loadFeatured(mode = 'buy'){
    currentMode = mode;
    
    try{
        const data = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({mode: mode})
        }, '/recommendations/by-features (featured)');
        
        const carousel = document.getElementById('featuredProperties');
        
        if(data.recommendations && data.recommendations.length > 0) {
            carousel.innerHTML = data.recommendations.map((p, i) => `
                <div class="property-card">
                    <div class="property-image" style="background-image:url('${p.image}')"></div>
                    <div class="property-info">
                        <div class="property-price">$${p.price.toLocaleString()}</div>
                        <div class="property-details">${p.beds} beds | ${p.baths} baths | ${p.sqft.toLocaleString()} sqft</div>
                        <div class="property-address">${p.address}</div>
                        <div class="property-details">${p.description.substring(0,80)}...</div>
                        <div class="property-actions">
                            <button class="property-btn save-btn" onclick='saveProp("${p.property_id}")'>💾 Save</button>
                            <button class="property-btn more-btn" onclick='openCopilotFromProperty("${p.property_id}", "${p.address}", ${p.price}, ${p.beds}, ${p.baths})'>More Info</button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            carousel.innerHTML = '<div style="color:white;text-align:center;padding:40px;">No properties found</div>';
        }
        
        startAutoScroll();
        
    }catch(e){
        document.getElementById('featuredProperties').innerHTML =
            `<div style="color:white;text-align:center;padding:40px;">Error loading properties: ${e.message}</div>`;
    }
}

function startAutoScroll() {
    if(autoScrollInterval) {
        clearInterval(autoScrollInterval);
    }
    
    const carousel = document.getElementById('featuredProperties');
    if (!carousel) return;
    
    let scrollAmount = 0;
    
    autoScrollInterval = setInterval(() => {
        scrollAmount += 370;
        
        if(scrollAmount >= carousel.scrollWidth - carousel.clientWidth) {
            scrollAmount = 0;
        }
        
        carousel.scrollTo({
            left: scrollAmount,
            behavior: 'smooth'
        });
    }, 3000);
}

function stopAutoScroll() {
    if(autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
    }
}

function openCopilotFromProperty(id, address, price, beds, baths){
    openCopilot();
    
    const propertyInfo = `Tell me more about the property at ${address}. It's listed at $${price.toLocaleString()} with ${beds} bedrooms and ${baths} bathrooms. What similar properties are available?`;
    
    conversationHistory = [{role: 'system', content: 'You are PropBot, a helpful Boston real estate assistant.'}];
    conversationHistory.push({role: 'user', content: propertyInfo});
    
    addMsg('user', propertyInfo);
    sendMessageDirect(propertyInfo);
}

async function saveProp(id){
    try{
        const userId = currentUser?.user_id || 1;
        await safeFetchJson(`${API}/save-property`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({property_id:id, property_data:{}, user_id: userId})
        }, '/save-property');
        
        alert('Property saved! ✅');
    }catch(e){
        alert('Error saving: ' + e.message);
    }
}

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

async function initCopilot(){
    initMap();
    await loadNeighborhoods();
    await loadSampleQueries();
    await loadInitialProperties();
    showHome();
    
    conversationHistory = [
        {role: 'system', content: 'You are PropBot, a helpful Boston real estate assistant.'}
    ];
    
    addMsg('bot',`Hi ${currentUser?.fullName || 'there'}! 👋 I'm PropBot. Ask me anything about Boston neighborhoods, prices, or commute.`);
}

function initMap(){
    if(map) return;
    map = L.map('mapView').setView([42.3601,-71.0589],12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
        attribution:'© OpenStreetMap',
        maxZoom: 19
    }).addTo(map);
}

async function loadNeighborhoods(){
    neighborhoods = [
        "Back Bay","Beacon Hill","South End","Dorchester",
        "Jamaica Plain","Charlestown","East Boston","Roxbury",
        "North End","Fenway","Allston","Brighton"
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
                <button class="quick-reply-btn" onclick="quickMsg(\`${q}\`)">${q.substring(0,40)}...</button>`).join('');
    }catch(e){
        console.error('Sample queries error:',e);
    }
}

async function loadInitialProperties(){
    try{
        const data = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({})
        }, '/recommendations/by-features (copilot initial)');
        
        const propertiesWithCoords = await Promise.all(
            data.recommendations.map(async (r, i) => {
                const coords = await geocodeAddress(r.address);
                return {
                    id: r.property_id,
                    name: `Property ${i+1}`,
                    description: r.description,
                    score: r.match_score,
                    address: r.address,
                    lat: coords.lat,
                    lng: coords.lng
                };
            })
        );
        
        properties = propertiesWithCoords;
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
        list.innerHTML='<div class="loading">No properties yet. Try searching!</div>';
        document.getElementById('listingsCount').innerText='0 matches';
        return;
    }
    list.innerHTML = properties.map((p,i)=>`
        <div class="listing-card" onclick="selectProp(${i})">
            <div class="listing-title">${p.name}</div>
            <div class="listing-meta">${p.description.substring(0,85)}...</div>
        </div>
    `).join('');
    document.getElementById('listingsCount').innerText = properties.length + ' matches';
}

function updateMap(){
    if(!map) return;
    
    markers.forEach(m=>map.removeLayer(m));
    markers=[];
    
    properties.forEach((p,i)=>{
        const marker = L.marker([p.lat, p.lng]).addTo(map);
        marker.bindPopup(`
            <b>${p.name}</b><br>
            <div style="font-size:12px;color:#64748b;margin-top:4px;">${p.address || ''}</div>
        `);
        marker.on('click', ()=>selectProp(i));
        markers.push(marker);
    });
    
    if(properties.length > 0){
        const bounds = L.latLngBounds(properties.map(p=>[p.lat, p.lng]));
        map.fitBounds(bounds, {padding:[40,40]});
    }
}

function selectProp(i){
    selectedIdx = i;
    const p = properties[i];
    if(map && p.lat && p.lng) {
        map.setView([p.lat, p.lng], 15, {animate: true});
        if(markers[i]) {
            markers[i].openPopup();
        }
    }
}

function addMsg(type, txt){
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `<div class="message-bubble">${txt}</div>`;
    container.appendChild(messageDiv);
    
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
}

async function sendMsg(){
    const inp = document.getElementById('msgInput');
    const txt = inp.value.trim();
    if(!txt) return;
    
    addMsg('user', txt);
    inp.value='';
    document.getElementById('quickReplies').innerHTML='';
    
    conversationHistory.push({role: 'user', content: txt});
    
    const recentContext = conversationHistory
        .slice(-5)
        .map(m => `${m.role}: ${m.content}`)
        .join('\n');
    
    const contextualQuery = `Previous conversation:\n${recentContext}\n\nCurrent question: ${txt}`;
    
    try{
        const userId = currentUser?.user_id || 1;
        const data = await safeFetchJson(`${API}/chat`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                query: contextualQuery,
                user_id: userId
            })
        }, '/chat');
        
        const answer = data.answer;
        setTimeout(()=>addMsg('bot', answer), 400);
        
        conversationHistory.push({role: 'assistant', content: answer});
        
        const searchCriteria = extractSearchCriteria(txt);
        
        console.log('🔍 Extracted search criteria:', searchCriteria);
        
        if(Object.keys(searchCriteria).length > 0) {
            try {
                const recData = await safeFetchJson(`${API}/recommendations/by-features`,{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify(searchCriteria)
                }, '/recommendations/by-features (update)');
                
                console.log('✅ Got recommendations:', recData);
                
                if(recData.recommendations && recData.recommendations.length > 0) {
                    const newProps = await Promise.all(
                        recData.recommendations.map(async (r, i) => {
                            const coords = await geocodeAddress(r.address);
                            return {
                                id: r.property_id,
                                name: `Property ${i+1}`,
                                description: r.description,
                                score: r.match_score,
                                address: r.address,
                                lat: coords.lat,
                                lng: coords.lng
                            };
                        })
                    );
                    
                    properties = newProps;
                    renderListings();
                    updateMap();
                    
                    console.log('✅ Updated properties on map!');
                }
            } catch(err) {
                console.error('❌ Property update failed:', err);
            }
        } else {
            console.log('⚠️ No search criteria found, keeping existing properties');
        }
        
    }catch(e){
        setTimeout(()=>addMsg('bot', '❌ Error: '+e.message), 400);
    }
}

function extractSearchCriteria(query) {
    const criteria = {};
    const lowerQuery = query.toLowerCase();
    
    const neighborhoods = [
        "back bay", "beacon hill", "south end", "dorchester",
        "jamaica plain", "charlestown", "east boston", "roxbury",
        "north end", "fenway", "allston", "brighton", "seaport",
        "south boston", "west end", "financial district"
    ];
    
    for(const hood of neighborhoods) {
        const patterns = [
            `in ${hood}`,
            `near ${hood}`,
            `around ${hood}`,
            `at ${hood}`,
            hood
        ];
        
        if(patterns.some(pattern => lowerQuery.includes(pattern))) {
            criteria.neighborhood = hood.split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            break;
        }
    }
    
    const bedroomMatch = lowerQuery.match(/(\d+)\s*(bed|bedroom|br)/);
    if(bedroomMatch) {
        criteria.bedrooms = parseInt(bedroomMatch[1]);
    }
    
    const bathroomMatch = lowerQuery.match(/(\d+)\s*(bath|bathroom|ba)/);
    if(bathroomMatch) {
        criteria.bathrooms = parseInt(bathroomMatch[1]);
    }
    
    const priceMatch = lowerQuery.match(/under\s*\$?(\d+)k?/i);
    if(priceMatch) {
        const price = parseInt(priceMatch[1]);
        criteria.max_price = price > 1000 ? price : price * 1000;
    }
    
    if(lowerQuery.includes('rent') || lowerQuery.includes('rental')) {
        criteria.mode = 'rent';
    } else if(lowerQuery.includes('buy') || lowerQuery.includes('purchase') || lowerQuery.includes('sale')) {
        criteria.mode = 'buy';
    }
    
    return criteria;
}

function quickMsg(txt){
    document.getElementById('msgInput').value = txt;
    sendMsg();
}

function sendMessage(txt){
    document.getElementById('msgInput').value = txt;
    sendMsg();
}

function sendMessageDirect(txt){
    conversationHistory.push({role: 'user', content: txt});
    
    const userId = currentUser?.user_id || 1;
    safeFetchJson(`${API}/chat`,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({query: txt, user_id: userId})
    }, '/chat').then(data => {
        setTimeout(()=>addMsg('bot', data.answer), 400);
        conversationHistory.push({role: 'assistant', content: data.answer});
    }).catch(e => {
        setTimeout(()=>addMsg('bot', '❌ Error: '+e.message), 400);
    });
}

function handleKey(e){
    if(e.key==='Enter') {
        e.preventDefault();
        sendMsg();
    }
}

function showHome(){
    document.getElementById('searchForm').classList.remove('active');
    document.getElementById('predictForm').classList.remove('active');
    document.getElementById('chatMessages').style.display='flex';
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
    const hood = document.getElementById('searchNeighborhood').value;
    const beds = document.getElementById('searchBedrooms').value;
    if(!hood || !beds){
        alert('Please fill all fields');
        return;
    }
    
    showHome();
    const queryText = `Search ${beds}BR properties in ${hood}`;
    addMsg('user', queryText);
    
    conversationHistory.push({role: 'user', content: queryText});
    
    try{
        const userId = currentUser?.user_id || 1;
        const data = await safeFetchJson(`${API}/search`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood, bedrooms:parseInt(beds), user_id: userId})
        }, '/search (copilot)');
        
        setTimeout(()=>addMsg('bot', data.answer), 400);
        conversationHistory.push({role: 'assistant', content: data.answer});
        
        const recData = await safeFetchJson(`${API}/recommendations/by-features`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood, bedrooms:parseInt(beds)})
        }, '/recommendations-by-features (search)');
        
        const propertiesWithCoords = await Promise.all(
            recData.recommendations.map(async (r, i) => {
                const coords = await geocodeAddress(r.address);
                return {
                    id: r.property_id,
                    name: `Property ${i+1} - ${hood}`,
                    description: r.description,
                    score: r.match_score,
                    address: r.address,
                    lat: coords.lat,
                    lng: coords.lng
                };
            })
        );
        
        properties = propertiesWithCoords;
        renderListings();
        updateMap();
        
    }catch(e){
        setTimeout(()=>addMsg('bot', '❌ Error: '+e.message), 400);
    }
    
    document.getElementById('searchNeighborhood').value='';
    document.getElementById('searchBedrooms').value='';
}

async function submitPredict(){
    const hood = document.getElementById('predictNeighborhood').value;
    const beds = document.getElementById('predictBedrooms').value;
    const baths = document.getElementById('predictBathrooms').value;
    if(!hood || !beds || !baths){
        alert('Please fill all fields');
        return;
    }
    
    showHome();
    const queryText = `Predict price for a ${beds}BR ${baths}BA home in ${hood}`;
    addMsg('user', queryText);
    
    conversationHistory.push({role: 'user', content: queryText});
    
    try{
        const data = await safeFetchJson(`${API}/predict-price`,{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({neighborhood:hood, bedrooms:parseInt(beds), bathrooms:parseInt(baths)})
        }, '/predict-price');
        
        const response = `💰 Estimated Price: $${data.predicted_price.toLocaleString()}\n📈 Price Range: $${data.price_range.min.toLocaleString()} - $${data.price_range.max.toLocaleString()}`;
        
        setTimeout(()=>{
            addMsg('bot', response);
        }, 400);
        
        conversationHistory.push({role: 'assistant', content: response});
        
    }catch(e){
        setTimeout(()=>addMsg('bot', '❌ Error: '+e.message), 400);
    }
    
    document.getElementById('predictNeighborhood').value='';
    document.getElementById('predictBedrooms').value='';
    document.getElementById('predictBathrooms').value='';
}

window.addEventListener('load',()=>{
    document.querySelector('.menu-button').style.display = 'none';
    document.querySelector('.propbot-button').style.display = 'none';
    
    checkStoredUser();
    document.getElementById('heroSearchBtn').addEventListener('click', heroSearch);
    document.getElementById('heroInput').addEventListener('keypress', e=>{
        if(e.key==='Enter') heroSearch();
    });
    
    setTimeout(() => {
        const carousel = document.getElementById('featuredProperties');
        if(carousel) {
            carousel.addEventListener('mouseenter', stopAutoScroll);
            carousel.addEventListener('mouseleave', () => startAutoScroll());
        }
    }, 1000);
});

document.addEventListener('DOMContentLoaded', function() {
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
});
