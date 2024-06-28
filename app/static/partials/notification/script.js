// app/static/partials/notification.js
function showNotification(message, time) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';

    const progressBarInner = document.createElement('div');
    progressBarInner.className = 'progress-bar-inner';
    progressBarInner.style.animationDuration = `${time / 1000}s`;

    progressBar.appendChild(progressBarInner);
    notification.appendChild(progressBar);

    document.querySelector('.notification-container').appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        notification.addEventListener('transitionend', function() {
            notification.remove();
        });
    }, time);
}

window.showNotification = showNotification;