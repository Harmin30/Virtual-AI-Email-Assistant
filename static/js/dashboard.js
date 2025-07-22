// document.addEventListener("DOMContentLoaded", () => {
//     const form = document.getElementById("reminder-form");
//     if (form) {
//         form.addEventListener("submit", async (e) => {
//             e.preventDefault();
//             const reminderTime = document.getElementById("reminder-time").value;

//             if (!reminderTime) {
//                 alert("Please select a valid date and time.");
//                 return;
//             }

//             try {
//                 const response = await fetch("/set_reminder", {
//                     method: "POST",
//                     headers: { "Content-Type": "application/json" },
//                     body: JSON.stringify({ reminder_time: reminderTime })
//                 });

//                 const result = await response.json();
//                 if (response.ok) {
//                     alert("Reminder set successfully!");
//                 } else {
//                     alert("Failed to set reminder: " + result.error);
//                 }
//             } catch (error) {
//                 alert("An error occurred: " + error.message);
//             }
//         });
//     }

//     const reminderForm = document.getElementById("reminderForm");
//     if (reminderForm) {
//         reminderForm.addEventListener("submit", async (e) => {
//             e.preventDefault();

//             const reminderTime = document.getElementById("reminder-time").value;
//             const date = document.getElementById("reminder-date").value;
//             const time = document.getElementById("reminder-clock").value;
//             const subject = document.getElementById("subject")?.value || '';
//             const description = document.getElementById("description")?.value || '';
//             const messageSpan = document.querySelector(".reminder-message");

//             try {
//                 const response = await fetch("/set-reminder", {
//                     method: "POST",
//                     headers: { "Content-Type": "application/x-www-form-urlencoded" },
//                     body: new URLSearchParams({
//                         reminder_time: reminderTime,
//                         date: date,
//                         time: time,
//                         subject: subject,
//                         description: description
//                     })
//                 });

//                 const result = await response.json();

//                 if (result.success) {
//                     messageSpan.textContent = "✅ Reminder set!";
//                     reminderForm.reset();
//                     setTimeout(() => messageSpan.textContent = '', 3000);
//                 } else {
//                     messageSpan.textContent = "❌ Failed to set reminder.";
//                 }
//             } catch (error) {
//                 console.error("Error setting reminder:", error);
//                 messageSpan.textContent = "⚠️ Server error occurred.";
//             }
//         });
//     }

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

    // Delete Email
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
    window.archiveEmail = (subject) => {
        fetch('/archive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subject })
        }).then(res => {
            if (res.ok) {
                const emailCard = document.querySelector(`.email:has(button[onclick*="${subject}"])`);
                const archivedBadge = document.createElement('span');
                archivedBadge.className = 'badge archived';
                archivedBadge.textContent = '📁 Archived';
                emailCard.insertBefore(archivedBadge, emailCard.children[0]);
            }
        });
    };

    // Voice Command (EVA)
    window.startVoiceCommand = () => {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            alert("Sorry, your browser does not support speech recognition.");
            return;
        }

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.start();

        recognition.onstart = () => alert("🎙 EVA is listening...");
        recognition.onresult = (event) => {
            const command = event.results[0][0].transcript.toLowerCase();
            if (command.includes("logout")) location.href = "/logout";
            else if (command.includes("inbox")) location.href = "/dashboard";
            else if (command.includes("compose")) location.href = "/compose";
            else if (command.includes("sent")) location.href = "/sent";
            else if (command.includes("archive")) location.href = "/archive";
            else alert(`EVA heard: ${command} but didn’t recognize it.`);
        };

        recognition.onerror = (event) => alert("Voice recognition error: " + event.error);
        recognition.onend = () => console.log("EVA finished listening.");
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
