// ═══════════════════════════════════════════════════════════════════════════
// Setup
// ═══════════════════════════════════════════════════════════════════════════

// ── Current logged-in user ID (passed from Flask/Jinja2 via data attribute) ──
const currentUserId = Number(document.body.dataset.userId);

// ── Date display ──────────────────────────────────────────────────────────────
const now    = new Date();
const days   = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const months = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"];

document.getElementById("todayDay").textContent   = days[now.getDay()];
document.getElementById("todayDate").textContent  = now.getDate();
document.getElementById("todayMonth").textContent = months[now.getMonth()] + " " + now.getFullYear();


// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}
const formatDate = d => d.toLocaleDateString("en-IN", { day:"numeric", month:"short", year:"numeric" });
const formatTime = d => d.toLocaleTimeString("en-GB", { hour:"2-digit", minute:"2-digit" });


// ═══════════════════════════════════════════════════════════════════════════
// Stats
// ═══════════════════════════════════════════════════════════════════════════

async function loadStats() {
    try {
        const res  = await fetch("/api/stats");
        const data = await res.json();
        if (data.success) {
            document.getElementById("statTotal").textContent    = data.total;
            document.getElementById("statUpcoming").textContent = data.upcoming;
            document.getElementById("statToday").textContent    = data.today;
        }
    } catch (e) { console.error("Stats error:", e); }
}


// ═══════════════════════════════════════════════════════════════════════════
// Events
// ═══════════════════════════════════════════════════════════════════════════

async function loadEvents() {
    const container = document.getElementById("eventsList");
    try {
        const res  = await fetch("/api/events");
        const data = await res.json();

        if (!data.success) {
            container.innerHTML = `<div class="empty-state">Could not load events.</div>`;
            return;
        }
        if (data.events.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span>📭</span>
                    <p>No events yet. Create your first one!</p>
                </div>`;
            return;
        }

        container.innerHTML = data.events.map(ev => {
            const start   = new Date(ev.start_time);
            const end     = new Date(ev.end_time);
            const isPast  = end < new Date();
            const isOwner = ev.created_by == currentUserId;

            // Show "(invited)" tag on events the user joined but didn't create
            const tag = !isOwner ? `<span class="event-tag">(invited)</span>` : "";

            // Only show Invite + Delete buttons if the user owns the event
            const actionBtns = isOwner ? `
                <button class="btn-invite" onclick="openInviteModal(${ev.event_id})">✉ Invite</button>
                <button class="btn-delete" onclick="deleteEvent(${ev.event_id})">🗑</button>
            ` : "";

            return `
            <div class="event-card ${isPast ? "past" : ""}">
                <div class="event-dot ${isPast ? "dot-past" : "dot-upcoming"}"></div>
                <div class="event-info">
                    <div class="event-title">${escapeHtml(ev.title)}${tag}</div>
                    <div class="event-time">
                        📅 ${formatDate(start)} &nbsp;
                        🕐 ${formatTime(start)} → ${formatTime(end)}
                    </div>
                </div>
                ${actionBtns}
            </div>`;
        }).join("");

    } catch (e) {
        container.innerHTML = `<div class="empty-state">Server error loading events.</div>`;
    }
}

// ── Delete event ──────────────────────────────────────────────────────────────
async function deleteEvent(id) {
    if (!confirm("Delete this event?")) return;
    try {
        const res  = await fetch(`/api/events/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) { loadEvents(); loadStats(); }
        else alert(data.message);
    } catch (e) { alert("Could not delete event."); }
}


// ═══════════════════════════════════════════════════════════════════════════
// Event Modal
// ═══════════════════════════════════════════════════════════════════════════

function openModal() {
    document.getElementById("eventModal").classList.remove("hidden");
    document.getElementById("createError").classList.add("hidden");
    document.getElementById("createSuccess").classList.add("hidden");
    document.getElementById("createEventForm").reset();
}
function closeModal() {
    document.getElementById("eventModal").classList.add("hidden");
}
document.getElementById("eventModal").addEventListener("click", function(e) {
    if (e.target === this) closeModal();
});

// ── Populate HH / MM selects (runs once on page load) ────────────────────────
(function() {
    ["eventStartHH","eventEndHH"].forEach(id => {
        const sel = document.getElementById(id);
        for (let h = 0; h < 24; h++) {
            const opt = document.createElement("option");
            opt.value = opt.textContent = String(h).padStart(2,"0");
            sel.appendChild(opt);
        }
        sel.value = "08";
    });
    ["eventStartMM","eventEndMM"].forEach(id => {
        const sel = document.getElementById(id);
        ["00","15","30","45"].forEach(m => {
            const opt = document.createElement("option");
            opt.value = opt.textContent = m;
            sel.appendChild(opt);
        });
    });
})();

// ── Submit new event ──────────────────────────────────────────────────────────
document.getElementById("createEventForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const btn        = document.getElementById("createBtn");
    const errorDiv   = document.getElementById("createError");
    const successDiv = document.getElementById("createSuccess");

    const title     = document.getElementById("eventTitle").value.trim();
    const startDate = document.getElementById("eventStartDate").value;
    const startHH   = document.getElementById("eventStartHH").value;
    const startMM   = document.getElementById("eventStartMM").value;
    const endDate   = document.getElementById("eventEndDate").value;
    const endHH     = document.getElementById("eventEndHH").value;
    const endMM     = document.getElementById("eventEndMM").value;

    if (!startDate || !endDate) {
        errorDiv.textContent = "❌ Please fill in both dates.";
        errorDiv.classList.remove("hidden");
        return;
    }

    const start = `${startDate}T${startHH}:${startMM}`;
    const end   = `${endDate}T${endHH}:${endMM}`;

    btn.textContent = "Creating...";
    btn.disabled    = true;
    errorDiv.classList.add("hidden");
    successDiv.classList.add("hidden");

    try {
        const res  = await fetch("/api/events", {
            method:  "POST",
            headers: {"Content-Type":"application/json"},
            body:    JSON.stringify({ title, start, end })
        });
        const data = await res.json();
        if (data.success) {
            successDiv.textContent = "✅ " + data.message;
            successDiv.classList.remove("hidden");
            loadEvents(); loadStats();
            setTimeout(closeModal, 1500);
        } else {
            errorDiv.textContent = "❌ " + data.message;
            errorDiv.classList.remove("hidden");
        }
    } catch (err) {
        errorDiv.textContent = "❌ Could not connect to server.";
        errorDiv.classList.remove("hidden");
    }
    btn.textContent = "Create Event";
    btn.disabled    = false;
});


// ═══════════════════════════════════════════════════════════════════════════
// Invitation Search
// ═══════════════════════════════════════════════════════════════════════════

let currentInviteEventId = null;
let selectedUserId       = null;
let searchDebounceTimer  = null;

function openInviteModal(eventId) {
    currentInviteEventId = eventId;
    document.getElementById("inviteModal").classList.remove("hidden");
    document.getElementById("inviteError").classList.add("hidden");
    document.getElementById("inviteSuccess").classList.add("hidden");

    // Reset search state
    selectedUserId = null;
    document.getElementById("inviteSearch").value = "";
    hideSearchResults();
}

function hideSearchResults() {
    const results = document.getElementById("searchResults");
    results.classList.add("hidden");
    results.innerHTML = "";
}

function renderSearchResults(users) {
    const results = document.getElementById("searchResults");

    if (users.length === 0) {
        results.innerHTML = `<div class="search-result-empty">No users found.</div>`;
        results.classList.remove("hidden");
        return;
    }

    results.innerHTML = users.map(u => `
        <div class="search-result-item" data-user-id="${u.user_id}" data-email="${escapeHtml(u.email)}">
            <div class="search-result-name">${escapeHtml(u.name)}</div>
            <div class="search-result-email">${escapeHtml(u.email)}</div>
        </div>
    `).join("");
    results.classList.remove("hidden");

    results.querySelectorAll(".search-result-item").forEach(item => {
        item.addEventListener("click", function() {
            selectedUserId = Number(this.dataset.userId);
            document.getElementById("inviteSearch").value = this.dataset.email;
            hideSearchResults();
        });
    });
}

// Searches by email only — email is the unique identifier in this app
async function performUserSearch(query) {
    try {
        const res  = await fetch(`/api/users/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.success) {
            renderSearchResults(data.users);
        } else {
            hideSearchResults();
        }
    } catch (e) {
        hideSearchResults();
    }
}

document.getElementById("inviteSearch").addEventListener("input", function() {
    selectedUserId = null; // typing invalidates any previous selection
    const query = this.value.trim();

    clearTimeout(searchDebounceTimer);

    if (query.length < 2) {
        hideSearchResults();
        return;
    }

    searchDebounceTimer = setTimeout(() => performUserSearch(query), 250);
});

// Close results when clicking outside the search box / results list
document.addEventListener("click", function(e) {
    const results = document.getElementById("searchResults");
    const input   = document.getElementById("inviteSearch");
    if (e.target !== input && !results.contains(e.target)) {
        hideSearchResults();
    }
});

function closeInviteModal() {
    document.getElementById("inviteModal").classList.add("hidden");
}
document.getElementById("inviteModal").addEventListener("click", function(e) {
    if (e.target === this) closeInviteModal();
});

async function sendInvite() {
    const receiver_id = selectedUserId;
    const errDiv      = document.getElementById("inviteError");
    const okDiv       = document.getElementById("inviteSuccess");

    if (!receiver_id) {
        errDiv.textContent = "❌ Please select a user.";
        errDiv.classList.remove("hidden");
        return;
    }
    errDiv.classList.add("hidden");
    okDiv.classList.add("hidden");

    try {
        const res  = await fetch("/api/invite", {
            method:  "POST",
            headers: {"Content-Type":"application/json"},
            body:    JSON.stringify({ event_id: currentInviteEventId, receiver_id })
        });
        const data = await res.json();
        if (data.success) {
            okDiv.textContent = "✅ " + data.message;
            okDiv.classList.remove("hidden");
            setTimeout(() => {
                closeInviteModal();
                // Reset search state so the next invite starts clean
                selectedUserId = null;
                document.getElementById("inviteSearch").value = "";
                hideSearchResults();
            }, 1500);
        } else {
            errDiv.textContent = "❌ " + data.message;
            errDiv.classList.remove("hidden");
        }
    } catch(e) {
        errDiv.textContent = "❌ Could not connect.";
        errDiv.classList.remove("hidden");
    }
}


// ═══════════════════════════════════════════════════════════════════════════
// Invitations
// ═══════════════════════════════════════════════════════════════════════════

async function loadInvitations() {
    try {
        const res   = await fetch("/api/invitations");
        const data  = await res.json();
        const panel = document.getElementById("invitationsPanel");
        const list  = document.getElementById("invitationsList");
        const badge = document.getElementById("inviteBadge");

        if (!data.success || data.invitations.length === 0) {
            panel.style.display = "none";
            return;
        }

        panel.style.display = "block";
        badge.textContent   = data.invitations.length;

        list.innerHTML = data.invitations.map(inv => {
            const start = new Date(inv.start_time);
            return `
            <div class="event-card">
                <div class="event-dot dot-upcoming"></div>
                <div class="event-info">
                    <div class="event-title">${escapeHtml(inv.event_title)}</div>
                    <div class="event-time">
                        From: <strong>${escapeHtml(inv.sender_name)}</strong>
                        &nbsp;📅 ${formatDate(start)}
                        &nbsp;🕐 ${formatTime(start)}
                    </div>
                </div>
                <button class="btn-accept"  onclick="respondInvite(${inv.invitation_id}, 'accept')">✓ Accept</button>
                <button class="btn-decline" onclick="respondInvite(${inv.invitation_id}, 'decline')">✗ Decline</button>
            </div>`;
        }).join("");

    } catch(e) { console.error("Invitations error:", e); }
}

async function respondInvite(invId, action) {
    try {
        const res  = await fetch(`/api/invitations/${invId}`, {
            method:  "POST",
            headers: {"Content-Type":"application/json"},
            body:    JSON.stringify({ action })
        });
        const data = await res.json();
        if (data.success) {
            loadInvitations();
            if (action === "accept") { loadEvents(); loadStats(); }
        } else {
            alert(data.message);
        }
    } catch(e) { alert("Could not respond to invitation."); }
}


// ═══════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════

loadStats();
loadEvents();
loadInvitations();