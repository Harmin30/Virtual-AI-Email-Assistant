// // Show reminder modal with subject pre-filled
// function openReminderModal(emailId, subject) {
//     document.getElementById('reminderEmailId').value = emailId;
//     document.getElementById('reminderSubject').value = subject;
//     $('#reminderModal').modal('show');
// }

// document.addEventListener('DOMContentLoaded', () => {
//     const reminderForm = document.getElementById('reminderForm');
//     const messageSpan = document.getElementById('reminderMessage');

//     if (reminderForm) {
//         reminderForm.addEventListener('submit', async (e) => {
//             e.preventDefault();

//             const subject = document.getElementById('reminderSubject').value;
//             const reminderTime = document.getElementById('reminder-time').value;
//             const date = document.getElementById('reminder-date').value;
//             const time = document.getElementById('reminder-clock').value;
//             const emailId = document.getElementById('reminderEmailId').value;

//             if (!subject || !reminderTime || !date || !time || !emailId) {
//                 messageSpan.textContent = '❗ Please fill all fields.';
//                 return;
//             }

//             try {
//                 const response = await fetch('/set-reminder', {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/x-www-form-urlencoded'
//                     },
//                     body: new URLSearchParams({
//                         subject: subject,
//                         reminder_time: reminderTime,
//                         date: date,
//                         time: time,
//                         email_id: emailId
//                     })
//                 });

//                 const result = await response.json();
//                 if (result.success) {
//                     messageSpan.textContent = '✅ Reminder set successfully!';
//                     reminderForm.reset();
//                     setTimeout(() => {
//                         $('#reminderModal').modal('hide');
//                         messageSpan.textContent = '';
//                     }, 1500);
//                 } else {
//                     messageSpan.textContent = '❌ Failed to set reminder.';
//                 }
//             } catch (error) {
//                 console.error(error);
//                 messageSpan.textContent = '⚠️ Error occurred.';
//             }
//         });
//     }
// });
