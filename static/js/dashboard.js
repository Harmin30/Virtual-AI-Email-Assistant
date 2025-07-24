

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

// Archive Email
// window.archiveEmail = (id) => {
//     fetch('/archive', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ id })
//     })
//     .then(res => res.json())
//     .then(data => {
//         if (data.success) {
//             // Remove the email card
//             const emailCard = document.querySelector(`.email[data-id="${id}"]`);
//             if (emailCard) {
//                 emailCard.remove();
//             }

//             // Remove the detailed body section
//             const detailsSection = document.querySelector(`.email-details[data-id="${id}"]`);
//             if (detailsSection) {
//                 detailsSection.remove();
//             }

//             // Show a toast or inline confirmation
//             showToast("Email archived ✅");
//         }
//     });
// };

// window.unarchiveEmail = (id) => {
//     fetch('/unarchive', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ id })
//     })
//     .then(res => res.json())
//     .then(data => {
//         if (data.success) {
//             const emailCard = document.querySelector(`.email[data-id="${id}"]`);
//             if (emailCard) emailCard.remove();

//             const detailsSection = document.querySelector(`.email-details[data-id="${id}"]`);
//             if (detailsSection) detailsSection.remove();

//             showToast("Email unarchived ✅");
//         }
//     });
// };


// Toast function (add once globally)
// function showToast(message) {
//     let toast = document.createElement('div');
//     toast.textContent = message;
//     toast.style.cssText = `
//         position: fixed;
//         bottom: 20px;
//         right: 20px;
//         background: #333;
//         color: white;
//         padding: 10px 20px;
//         border-radius: 8px;
//         box-shadow: 0 0 10px rgba(0,0,0,0.3);
//         z-index: 9999;
//         opacity: 0;
//         transition: opacity 0.5s ease-in-out;
//     `;
//     document.body.appendChild(toast);
//     requestAnimationFrame(() => {
//         toast.style.opacity = 1;
//     });
//     setTimeout(() => {
//         toast.style.opacity = 0;
//         setTimeout(() => toast.remove(), 5000);
//     }, 5000); // visible for 2 sec
// }

// DELETE button for the email cards on email dashboard


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


// Voice Command (EVA)
// window.startVoiceCommand = () => {
//     if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
//         alert("Sorry, your browser does not support speech recognition.");
//         return;
//     }

//     const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
//     recognition.lang = 'en-US';
//     recognition.interimResults = false;
//     recognition.maxAlternatives = 1;

//     recognition.start();

//     recognition.onstart = () => alert("🎙 EVA is listening...");
//     recognition.onresult = (event) => {
//         const command = event.results[0][0].transcript.toLowerCase();
//         if (command.includes("logout")) location.href = "/logout";
//         else if (command.includes("inbox")) location.href = "/dashboard";
//         else if (command.includes("compose")) location.href = "/compose";
//         else if (command.includes("sent")) location.href = "/sent";
//         else if (command.includes("archive")) location.href = "/archive";
//         else alert(`EVA heard: ${command} but didn’t recognize it.`);
//     };

//     recognition.onerror = (event) => alert("Voice recognition error: " + event.error);
//     recognition.onend = () => console.log("EVA finished listening.");
// };



// Toast message function


// let isListening = false;
// let recognition = null;
// let evaToast = null;
// let selectedVoice = null;

// // EVA Speak Function
// function evaSpeak(text) {
//     if (!window.speechSynthesis) {
//         showEVAToast("🔇 Your browser does not support speech synthesis.");
//         return;
//     }

//     const utterance = new SpeechSynthesisUtterance(text);
//     utterance.voice = selectedVoice;
//     utterance.lang = 'en-US';
//     utterance.rate = 1;
//     utterance.pitch = 1;

//     window.speechSynthesis.cancel(); // Cancel ongoing speech if any
//     window.speechSynthesis.speak(utterance);
// }

// // Load and select preferred female voice
// function loadEVAVoice() {
//     const voices = window.speechSynthesis.getVoices();
//     selectedVoice =
//         voices.find(v => v.name.includes("Google UK English Female")) ||
//         voices.find(v => v.name.toLowerCase().includes("female")) ||
//         voices.find(v => v.lang === "en-IN") ||
//         voices.find(v => v.lang === "en-US") ||
//         voices[0];
// }
// window.speechSynthesis.onvoiceschanged = loadEVAVoice;
// loadEVAVoice();

// // Toast messages
// function showEVAToast(message, sticky = false) {
//     if (evaToast) evaToast.remove();
//     evaToast = document.createElement('div');
//     evaToast.className = 'eva-toast';
//     evaToast.innerText = message;
//     document.body.appendChild(evaToast);
//     setTimeout(() => evaToast.classList.add('visible'), 100);

//     if (!sticky) {
//         setTimeout(() => {
//             evaToast.classList.remove('visible');
//             setTimeout(() => evaToast.remove(), 500);
//         }, 3000);
//     }
// }

// // Start voice recognition
// function startVoiceRecognition() {
//     recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
//     recognition.lang = 'en-US';
//     recognition.interimResults = true;
//     recognition.maxAlternatives = 1;

//     const transcriptBox = document.getElementById('evaLiveTranscript');
//     transcriptBox.style.display = 'block';
//     transcriptBox.innerText = '';

//     recognition.onresult = (event) => {
//         const interimTranscript = Array.from(event.results)
//             .map(r => r[0].transcript)
//             .join('');
//         transcriptBox.innerText = `🎧 EVA: ${interimTranscript}`;

//         if (event.results[0].isFinal) {
//             const command = event.results[0][0].transcript.toLowerCase().trim();
//             transcriptBox.innerText = '';

//             // Recognized commands
//             if (command.includes("logout")) {
//                 evaSpeak("Logging you out.");
//                 location.href = "/logout";
//             } else if (command.includes("inbox")) {
//                 evaSpeak("Opening your inbox.");
//                 location.href = "/dashboard";
//             } else if (command.includes("compose")) {
//                 evaSpeak("Let's compose a new email.");
//                 location.href = "/compose";
//             } else if (command.includes("sent")) {
//                 evaSpeak("Here are your sent emails.");
//                 location.href = "/sent";
//             } else if (command.includes("archive")) {
//                 evaSpeak("Opening archive.");
//                 location.href = "/archive";
//             } else {
//                 evaSpeak(`I heard: "${command}", but I didn’t recognize that command.`);
//                 showEVAToast(`🤖 EVA heard: "${command}" but didn’t recognize it.`);
//             }
//         }
//     };

//     recognition.onerror = (event) => {
//         showEVAToast(`⚠️ Voice error: ${event.error}`);
//         evaSpeak("There was a problem with voice recognition.");
//     };

//     recognition.onend = () => {
//         if (isListening) recognition.start(); // Auto-restart
//     };

//     recognition.start();
//     showEVAToast("🎙 EVA is listening...", true);
//     const btn = document.getElementById("evaBtn");
//     btn.classList.add("listening");
//     btn.innerHTML = `Stop EVA <i class="fa-solid fa-microphone-slash"></i>`;
// }

// // Stop voice recognition
// function stopVoiceRecognition() {
//     if (recognition) {
//         recognition.stop();
//         recognition = null;
//     }
//     isListening = false;
//     showEVAToast("🛑 EVA stopped listening");

//     const btn = document.getElementById("evaBtn");
//     btn.classList.remove("listening");
//     btn.innerHTML = `Talk to EVA <i class="fa-solid fa-robot"></i>`;
//     document.getElementById('evaLiveTranscript').style.display = 'none';
// }

// // Toggle voice command
// window.startVoiceCommand = () => {
//     if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
//         showEVAToast("❌ Browser doesn't support voice recognition.");
//         return;
//     }

//     isListening ? stopVoiceRecognition() : (isListening = true, startVoiceRecognition());
// };


// ==================================================================

let isListening = false;
let recognition = null;
let evaToast = null;
let selectedVoice = null;
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
function loadVoicesAndSetEVA() {
    return new Promise(resolve => {
        let voices = speechSynthesis.getVoices();

        if (voices.length) {
            resolve(voices);
        } else {
            speechSynthesis.onvoiceschanged = () => {
                voices = speechSynthesis.getVoices();
                resolve(voices);
            };
        }
    }).then(voices => {
        evaVoice =
            voices.find(v => v.name.toLowerCase().includes("google uk english female")) ||
            voices.find(v => v.name.toLowerCase().includes("zira")) ||
            voices.find(v => v.name.toLowerCase().includes("samantha")) ||
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

// Call this once at the top


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
        };

        utterance.onerror = () => {
            restoreOriginalHTML(bodyElement);
            button.innerHTML = `<i class="fas fa-volume-up"></i> Read Aloud`;
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
// function setReminderManually(subjectValue, reminderTimeValue) {
//     fetch('/set-reminder', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             subject: subjectValue,
//             reminder_time: reminderTimeValue
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         alert("Reminder set!");
//     })
//     .catch(err => {
//         console.error("Failed to set reminder", err);
//         alert("Something went wrong");
//     });
// }
// setReminderManually("Follow up email", "2025-07-21 18:00");


//     // Reminder checker
//     function checkReminders() {
//         fetch('/api/due-reminders')
//             .then(res => res.json())
//             .then(data => {
//                 if (data.length > 0) {
//                     data.forEach(reminder => {
//                         alert(`🔔 Reminder: "${reminder.subject}" from ${reminder.sender}`);
//                     });
//                     location.reload();
//                 }
//             })
//             .catch(err => console.error("Reminder check failed", err));
//     }

//     setInterval(checkReminders, 60000); // every 60 seconds
//     checkReminders(); // initial load

//     // Modal helper
//     window.openReminderModal = (emailId) => {
//         document.getElementById('reminderEmailId').value = emailId;
//         $('#reminderModal').modal('show');
//     };
// });


