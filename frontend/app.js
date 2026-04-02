const API_BASE = 'http://localhost:8000';

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

async function sendChatMessage(message) {
    try {
        const response = await fetch(`${API_BASE}/v1/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        return await response.json();
    } catch (error) {
        console.error('Chat error:', error);
        return { answer: "I'm sorry, I'm having trouble connecting to the concierge service right now.", sources: [] };
    }
}

// Render Rooms
async function renderRooms() {
    const roomsData = await fetchData('/v1/hotel/rooms');
    const roomsGrid = document.getElementById('rooms-grid');
    if (!roomsData || !roomsGrid) return;

    // The API might return a list of rooms or a dict with "rooms" key
    const rooms = Array.isArray(roomsData) ? roomsData : (roomsData.rooms || []);

    roomsGrid.innerHTML = rooms.map(room => `
        <div class="card">
            <div class="card-img" style="background: linear-gradient(45deg, var(--secondary), var(--primary)); display: flex; align-items: center; justify-content: center; font-family: 'Playfair Display', serif; color: var(--accent); font-size: 1.5rem; text-align: center; padding: 20px;">
                ${room.room_type}
            </div>
            <div class="card-content">
                <h3>${room.room_type}</h3>
                <p class="price">€${room.price_per_night_eur} / Night</p>
                <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 10px;">${room.view} View • Capacity: ${room.capacity} guests</p>
                <p style="font-size: 0.8rem; color: var(--teal);">${room.breakfast_included ? '✓ Breakfast Included' : 'Breakfast Available'}</p>
            </div>
        </div>
    `).join('');
}

// Render Services
async function renderServices() {
    const servicesData = await fetchData('/v1/hotel/services');
    const servicesGrid = document.getElementById('services-grid');
    if (!servicesData || !servicesGrid) return;

    const services = Array.isArray(servicesData) ? servicesData : (servicesData.services || []);

    servicesGrid.innerHTML = services.map(service => `
        <div class="card" style="background: var(--primary);">
            <div class="card-content">
                <h3>${service.service_name}</h3>
                <p class="price">€${service.price_eur}</p>
                <p style="color: var(--text-dim); font-size: 0.85rem;">${service.description}</p>
            </div>
        </div>
    `).join('');
}

// Chat Logic
const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const chatQuery = document.getElementById('chat-query');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatQuery.value.trim();
    if (!query) return;

    // Add User Message
    addMessage(query, 'user');
    chatQuery.value = '';

    // Typing indicator
    const typingId = addMessage('Thinking...', 'ai typing');

    // Get AI Response
    const response = await sendChatMessage(query);
    
    // Remove typing indicator and add response
    const typingMsg = document.getElementById(typingId);
    if (typingMsg) typingMsg.remove();

    addMessage(response.answer, 'ai', response.sources);
});

function addMessage(text, type, sources = []) {
    const id = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = `message ${type}`;
    
    let content = `<div>${text}</div>`;
    if (sources && sources.length > 0) {
        content += `<div style="font-size: 0.7rem; color: var(--teal); margin-top: 8px; border-top: 1px solid var(--glass); padding-top: 4px;">Sources: ${sources.join(', ')}</div>`;
    }
    
    messageDiv.innerHTML = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    renderRooms();
    renderServices();
});
