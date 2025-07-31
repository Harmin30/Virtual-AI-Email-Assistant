
window.addEventListener('load', () => {
    loadVoicesAndSetEVA();
});

// Sidebar and dark mode
window.toggleSidebar = () => document.getElementById('sidebar').classList.toggle('collapsed');
window.toggleDarkMode = () => document.body.classList.toggle('dark-mode');

// Email details toggle
window.toggleDetails = (btn) => {
    const details = btn.closest('.email').querySelector('.email-details');
    const isVisible = details.style.display === 'block';
    details.style.display = isVisible ? 'none' : 'block';
    btn.textContent = isVisible ? '▼ View Details' : '▲ Hide';
};

// Mark as Read
window.markAsRead = (button, subject) => {
    fetch('/mark_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject })
    }).then(res => {
        if (res.ok) {
            const emailCard = button.closest('.email');
            button.remove();
            const unreadBadge = emailCard.querySelector('.badge.unread');
            if (unreadBadge) {
                unreadBadge.textContent = '✅ Read';
                unreadBadge.classList.remove('unread');
                unreadBadge.classList.add('read');
            }
        }
    });
};

// Delete Email button for SENT Section
window.deleteEmail = (subject) => {
    fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject })
    }).then(res => {
        if (res.ok) {
            const emailCard = document.querySelector(`.email:has(button[onclick*="${subject}"])`);
            if (emailCard) emailCard.remove();
        }
    });
};




function deleteEmail(subject, id) {
    fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove ALL blocks with the matching data-id
                document.querySelectorAll(`.email[data-id="${id}"]`).forEach(el => {
                    el.remove();
                });
            }
        })
        .catch(error => console.error('Delete error:', error));
}


// =============================EVA VOICE AI=====================================

let isListening = false;
let recognition = null;
let evaToast = null;
let selectedVoice = null;
let isReading = false; // 👈 Controls auto-refresh during TTS

loadVoicesAndSetEVA();

// EVA Speak Function
let evaVoice = null;

function evaSpeak(text) {
    if (!speechSynthesis) {
        showEVAToast("🔇 Your browser does not support speech synthesis.");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);

    if (evaVoice) {
        utterance.voice = evaVoice;
    }

    utterance.rate = 1;
    utterance.pitch = 1.1;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}


// Load and select preferred female voice
// function loadVoicesAndSetEVA() {
//     return new Promise(resolve => {
//         let voices = speechSynthesis.getVoices();

//         if (voices.length) {
//             resolve(voices);
//         } else {
//             speechSynthesis.onvoiceschanged = () => {
//                 voices = speechSynthesis.getVoices();
//                 resolve(voices);
//             };
//         }
//     }).then(voices => {
//         evaVoice =
//             voices.find(v => v.name.toLowerCase().includes("google uk english female")) ||
//             voices.find(v => v.name.toLowerCase().includes("zira")) ||
//             voices.find(v => v.name.toLowerCase().includes("samantha")) ||
//             voices.find(v => v.name.toLowerCase().includes("female")) ||
//             voices.find(v => v.lang === "en-IN") ||
//             voices.find(v => v.lang === "en-US") ||
//             voices[0];

//         if (evaVoice) {
//             console.log(`✅ EVA voice set to: ${evaVoice.name} (${evaVoice.lang})`);
//         } else {
//             console.warn("⚠️ EVA voice not found, using default.");
//         }
//     });
// }

function loadVoicesAndSetEVA() {
    return new Promise(resolve => {
        let voices = speechSynthesis.getVoices();

        function setVoices() {
            voices = speechSynthesis.getVoices();
            if (voices.length > 0) {
                resolve(voices);
            } else {
                // Try again after short delay if voices not loaded yet
                setTimeout(setVoices, 100);
            }
        }

        if (voices.length > 0) {
            resolve(voices);
        } else {
            speechSynthesis.onvoiceschanged = setVoices;
            setVoices(); // initial attempt
        }
    }).then(voices => {
        evaVoice =
            voices.find(v => v.name.toLowerCase().includes("samantha")) ||
            voices.find(v => v.name.toLowerCase().includes("google uk english female")) ||
            voices.find(v => v.name.toLowerCase().includes("zira")) ||
            voices.find(v => v.name.toLowerCase().includes("female")) ||
            voices.find(v => v.lang === "en-IN") ||
            voices.find(v => v.lang === "en-US") ||
            voices[0];

        if (evaVoice) {
            console.log(`✅ EVA voice set to: ${evaVoice.name} (${evaVoice.lang})`);
        } else {
            console.warn("⚠️ EVA voice not found, using default.");
        }
    });
}




// Toast messages
function showEVAToast(message, sticky = false) {
    if (evaToast) evaToast.remove();
    evaToast = document.createElement('div');
    evaToast.className = 'eva-toast';
    evaToast.innerText = message;
    document.body.appendChild(evaToast);
    setTimeout(() => evaToast.classList.add('visible'), 100);

    if (!sticky) {
        setTimeout(() => {
            evaToast.classList.remove('visible');
            setTimeout(() => evaToast.remove(), 500);
        }, 3000);
    }
}

// 🕒 Get greeting based on time
function getTimeGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning! ";
    if (hour < 18) return "Good afternoon! ";
    return "Good evening! ";
}

// Start voice recognition
function startVoiceRecognition() {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    const transcriptBox = document.getElementById('evaLiveTranscript');
    transcriptBox.style.display = 'block';
    transcriptBox.innerText = '';

    evaSpeak(getTimeGreeting() + " How can I help you today?");
    showEVAToast("🎙 EVA is listening...", true);

    recognition.onresult = (event) => {
        const interimTranscript = Array.from(event.results)
            .map(r => r[0].transcript)
            .join('');
        transcriptBox.innerText = `🎧 EVA: ${interimTranscript}`;

        if (event.results[0].isFinal) {
            const command = event.results[0][0].transcript.toLowerCase().trim();
            transcriptBox.innerText = '';

            // 🔁 Send command to backend for processing
            fetch(`/eva-listen?query=${encodeURIComponent(command)}`)
                .then(res => res.json())
                .then(data => {
                    const reply = data.reply || data.message || "Sorry, I didn’t understand.";
                    evaSpeak(reply);

                    // Optional: redirect if backend gives an action URL
                    if (data.action) {
                        const routeMap = {
                            "inbox": "/",                            // ✅ home dashboard
                            "unread": "/?filter=unread",             // ✅ filtered
                            "read_latest": "/?filter=read",          // ✅ filtered
                            "archive": "/?filter=archived",          // ✅ filtered
                            "sent": "/sent",                         // ✅ works
                            "compose": "/compose",                   // ✅ works
                            "logout": "/logout"                      // ✅ works
                        };
                        const url = routeMap[data.action];
                        if (data.redirect) {
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 1800);
                        } else if (url) {
                            setTimeout(() => {
                                window.location.href = url;
                            }, 1800);
                        }
                    }

                })
                .catch(err => {
                    console.error("EVA error:", err);
                    evaSpeak("Something went wrong.");
                });
        }
    };

    recognition.onerror = (event) => {
        showEVAToast(`⚠️ Voice error: ${event.error}`);
        evaSpeak("There was a problem with voice recognition.");
    };

    recognition.onend = () => {
        if (isListening) recognition.start(); // Auto-restart
    };

    recognition.start();
    const btn = document.getElementById("evaBtn");
    btn.classList.add("listening");
    btn.innerHTML = `Stop EVA <i class="fa-solid fa-microphone-slash"></i>`;
}

// Stop voice recognition
function stopVoiceRecognition() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
    isListening = false;
    showEVAToast("🛑 EVA stopped listening");

    const btn = document.getElementById("evaBtn");
    btn.classList.remove("listening");
    btn.innerHTML = `Talk to EVA <i class="fa-solid fa-robot"></i>`;
    document.getElementById('evaLiveTranscript').style.display = 'none';
}

// Toggle voice command
window.startVoiceCommand = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        showEVAToast("❌ Browser doesn't support voice recognition.");
        return;
    }

    isListening ? stopVoiceRecognition() : (isListening = true, startVoiceRecognition());
};


// TTS Reader
let voices = [];
function populateVoices() {
    voices = speechSynthesis.getVoices();
    document.querySelectorAll(".voiceSelect").forEach(select => {
        select.innerHTML = "";
        voices.forEach((voice, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang}) ${voice.default ? "[default]" : ""}`;
            select.appendChild(option);
        });
        const indianVoice = voices.find(v => v.lang.includes("en-IN") && v.name.toLowerCase().includes("female"));
        if (indianVoice) select.value = voices.indexOf(indianVoice);
    });
}
if (typeof speechSynthesis !== "undefined") {
    speechSynthesis.onvoiceschanged = populateVoices;
    populateVoices();
}

document.querySelectorAll(".read-aloud-btn").forEach(button => {
    button.addEventListener("click", () => {
        const container = button.closest(".email-details");
        const bodyElement = container.querySelector(".email-read-body");
        const voiceSelect = container.querySelector(".voiceSelect");

        if (speechSynthesis.speaking || speechSynthesis.pending) {
            speechSynthesis.cancel();
            isReading = false; // 👈 Reset if stopped early
            restoreOriginalHTML(bodyElement);
            button.innerHTML = `<i class="fas fa-volume-up"></i> Read Aloud`;
            return;
        }

        const originalHTML = bodyElement.innerHTML.trim();
        const plainText = bodyElement.textContent.trim();
        if (!plainText) {
            alert("No email body available to read.");
            return;
        }

        bodyElement.setAttribute("data-original-html", originalHTML);

        const newHTML = [];
        bodyElement.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
                const words = node.textContent.split(/\s+/).filter(w => w);
                words.forEach((word, i) => {
                    newHTML.push(`<span class="word">${word}</span>${i < words.length - 1 ? ' ' : ''}`);
                });
            } else if (node.nodeName === "BR") {
                newHTML.push("<br>");
            } else {
                newHTML.push(node.outerHTML);
            }
        });
        bodyElement.innerHTML = newHTML.join(" ");

        const utterance = new SpeechSynthesisUtterance(plainText);
        utterance.rate = 1;
        utterance.pitch = 1;

        const selectedIndex = voiceSelect.value;
        if (selectedIndex !== "") {
            utterance.voice = voices[selectedIndex];
        }

        const spans = bodyElement.querySelectorAll(".word");
        let wordIndex = 0;

        button.innerHTML = `<i class="fas fa-stop"></i> Stop`;

        // ✅ Mark reading in progress
        isReading = true;

        utterance.onboundary = function (event) {
            if (event.name === "word") {
                if (wordIndex > 0 && spans[wordIndex - 1]) spans[wordIndex - 1].classList.remove("highlight");
                if (wordIndex < spans.length && spans[wordIndex]) spans[wordIndex].classList.add("highlight");
                wordIndex++;
            }
        };

        utterance.onend = () => {
            restoreOriginalHTML(bodyElement);
            button.innerHTML = `<i class="fas fa-volume-up"></i> Read Aloud`;
            isReading = false; // ✅ Resume refresh after reading
        };

        utterance.onerror = () => {
            restoreOriginalHTML(bodyElement);
            button.innerHTML = `<i class="fas fa-volume-up"></i> Read Aloud`;
            isReading = false; // ✅ Resume even on error
        };

        speechSynthesis.speak(utterance);
    });
});


function restoreOriginalHTML(bodyElement) {
    const original = bodyElement.getAttribute("data-original-html");
    if (original) {
        bodyElement.innerHTML = original;
        bodyElement.removeAttribute("data-original-html");
    }
}


// Refresh 

const emailContainer = document.getElementById('email-container');
const spinner = document.getElementById('spinner');
const refreshBtn = document.getElementById('refreshBtn');

// ✅ Only run the logic if emailContainer exists (i.e., we are on the dashboard page)
if (emailContainer) {
    let autoRefreshPaused = false;

    function showSpinner() {
        if (spinner) spinner.style.display = 'inline-block';
    }

    function hideSpinner() {
        if (spinner) spinner.style.display = 'none';
    }

    function updateEmailList() {
        if (typeof isReading !== "undefined" && isReading) {
            console.log("🔇 Skipped refresh — read aloud in progress");
            return;
        }

        showSpinner();
        const start = Date.now();
        const minTime = 800;

        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('query') || '';
        const filter = urlParams.get('filter') || 'inbox';

        fetch(`/refresh-emails?filter=${filter}&query=${query}`)
            .then(res => {
                const delay = Math.max(0, minTime - (Date.now() - start));
                if (res.status === 204) {
                    console.log("✅ No new emails");
                    setTimeout(hideSpinner, delay);
                    return null;
                } else if (res.ok) {
                    return res.text().then(html => {
                        setTimeout(() => {
                            if (emailContainer.innerHTML.trim() !== html.trim()) {
                                emailContainer.innerHTML = html;
                                console.log("✅ Email list updated");
                            } else {
                                console.log("ℹ️ No DOM changes, skipped update");
                            }
                            hideSpinner();
                        }, delay);
                    });
                } else {
                    throw new Error("Refresh failed");
                }
            })
            .catch(err => {
                console.error("❌ Refresh error:", err);
                hideSpinner();
            });
    }

    // Manual Refresh
    if (refreshBtn) {
        refreshBtn.addEventListener('click', updateEmailList);
    } else {
        console.warn("⚠️ Refresh button not found");
    }

    // Auto Refresh every 60 seconds
    setInterval(() => {
        if (!autoRefreshPaused && !(typeof isReading !== "undefined" && isReading)) {
            updateEmailList();
        } else if (typeof isReading !== "undefined" && isReading) {
            console.log("⏸️ Skipped refresh — read aloud active");
        } else {
            console.log("⏸️ Skipped refresh — user is typing");
        }
    }, 60000);

    // Pause on input focus
    emailContainer.addEventListener('focusin', (e) => {
        const tag = e.target.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea') {
            autoRefreshPaused = true;
            console.log("✋ Auto-refresh paused while typing...");
        }
    });

    // Resume when focus is lost
    emailContainer.addEventListener('focusout', (e) => {
        setTimeout(() => {
            if (!emailContainer.querySelector(':focus')) {
                autoRefreshPaused = false;
                console.log("▶️ Auto-refresh resumed");
            }
        }, 200);
    });
} else {
    console.log("ℹ️ Skipped email refresh logic — not on dashboard");
}



document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.reminder-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const emailId = btn.dataset.emailId;
            const inputDiv = document.getElementById(`reminder-input-${emailId}`);

            if (btn.textContent.includes('Set Reminder')) {
                // Show date-time input
                inputDiv.style.display = 'block';
            } else {
                // Remove reminder directly
                fetch(`/toggle-reminder/${emailId}`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        const tag = document.getElementById(`reminder-tag-${emailId}`);
                        if (data.reminder === false) {
                            tag.style.display = 'none';
                            btn.innerHTML = '🔔 Set Reminder';
                        }
                    });
            }
        });
    });
});

// Confirm button: send the selected reminder time
function sendReminderTime(emailId) {
    const datetimeInput = document.getElementById(`reminder-time-${emailId}`);
    const reminderWrapper = document.getElementById(`reminder-input-${emailId}`);
    const reminderTag = document.getElementById(`reminder-tag-${emailId}`);
    const reminderTime = datetimeInput.value;

    if (!reminderTime) {
        showReminderToast("⚠️ Please select a date and time.");
        return;
    }

    const dateObj = new Date(reminderTime);
    const formattedTime = formatTo12Hour(dateObj);

    fetch(`/set-reminder/${emailId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            reminder_time: formattedTime
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                reminderTag.style.display = 'inline';
                reminderTag.setAttribute('data-reminder', formattedTime);
                reminderWrapper.style.display = 'none';
                showReminderToast("✅ Reminder set!");
            } else {
                showReminderToast("❌ Failed to set reminder.");
            }
        });
}

function formatTo12Hour(date) {
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const yyyy = date.getFullYear();

    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12;
    hours = hours ? hours : 12; // hour 0 should be 12

    return `${mm}/${dd}/${yyyy} ${hours}:${minutes} ${ampm}`;
}

// Urgency bar
function updateReminderUrgencyBars() {
    const now = new Date();

    document.querySelectorAll('.reminder-tag').forEach(tag => {
        const reminderStr = tag.getAttribute('data-reminder');
        if (!reminderStr) return;

        const reminderTime = new Date(reminderStr);
        const diffMs = reminderTime - now;
        const diffHrs = diffMs / (1000 * 60 * 60);

        const emailId = tag.id.split('-')[2]; // Extract ID from 'reminder-tag-{{ email.id }}'
        const bar = document.getElementById(`urgency-bar-${emailId}`);
        if (!bar) return;

        bar.classList.remove('urgency-red', 'urgency-yellow', 'urgency-green');

        if (diffHrs < 1) {
            bar.classList.add('urgency-red');
        } else if (diffHrs < 6) {
            bar.classList.add('urgency-yellow');
        } else {
            bar.classList.add('urgency-green');
        }
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', updateReminderUrgencyBars);

// Optional: live update every 60 seconds
setInterval(updateReminderUrgencyBars, 60000);


// Reminder notification count


