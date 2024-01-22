document.addEventListener("DOMContentLoaded", function () {
    const welcomeMessage = document.getElementById("welcome-message");

    if (welcomeMessage) {
        const username = sessionStorage.getItem('username');

        if (username) {
            WelcomeNotification(username);
        }
    }
});

function WelcomeNotification(username) {
    const notificationSpan = document.createElement('span');
    notificationSpan.classList.add('welcome-notification', 'success');
    notificationSpan.textContent = `Вы вошли, ${username}!`;

    document.body.appendChild(notificationSpan);

    setTimeout(() => {
        hideNotification();
    }, 3000);

    function hideNotification() {
        if (notificationSpan) {
            notificationSpan.parentNode.removeChild(notificationSpan);
        }
    }
}