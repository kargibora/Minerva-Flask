document.addEventListener('DOMContentLoaded', function() {
    var closeButtons = document.querySelectorAll('[data-dismiss-target]');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var targetId = e.currentTarget.getAttribute('data-dismiss-target');
            var targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.classList.add('fade-out');
                setTimeout(function(){
                    targetElement.remove();
                }, 500); // Corresponds to the duration of the transition in the CSS (0.5s = 500ms)
            }
        });
    });
});

function raiseAlert(message, alertId) {
    var alertContainer = document.createElement('div');
    alertContainer.id = 'alert-id-' + alertId;
    alertContainer.className = getAlertClass(alertId);
    alertContainer.role = 'alert';

    var iconSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    iconSvg.setAttribute('class', 'flex-shrink-0 w-5 h-5');
    iconSvg.setAttribute('fill', 'currentColor');
    iconSvg.setAttribute('viewBox', '0 0 20 20');
    iconSvg.innerHTML = '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>';

    var messageContainer = document.createElement('div');
    messageContainer.className = 'ml-3 text-sm font-medium';
    messageContainer.innerText = message;

    var closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'ml-auto -mx-1.5 -my-1.5 bg-gray-50 text-gray-500 rounded-lg focus:ring-2 focus:ring-gray-400 p-1.5 hover:bg-gray-200 inline-flex h-8 w-8 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white';
    closeButton.setAttribute('data-dismiss-target', '#alert-id-' + alertId);
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.innerHTML = '<span class="sr-only">Dismiss</span><svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';

    alertContainer.appendChild(iconSvg);
    alertContainer.appendChild(messageContainer);
    alertContainer.appendChild(closeButton);

    var alertContainerContainer = document.getElementById('alert-container');
    if (alertContainerContainer) {
        alertContainerContainer.appendChild(alertContainer);
    } else {
        document.body.appendChild(alertContainer);
    }

    closeButton.addEventListener('click', function() {
        alertContainer.classList.add('fade-out');
        setTimeout(function() {
            alertContainer.remove();
        }, 500); // Corresponds to the duration of the transition in the CSS (0.5s = 500ms)
    });
    
}

function getAlertClass(alertId) {
    var alertClasses = {
        '1': 'flex p-4 mb-4 text-blue-800 border-t-4 border-blue-300 bg-blue-50 dark:text-blue-400 dark:bg-gray-800 dark:border-blue-800',
        '2': 'flex p-4 mb-4 text-red-800 border-t-4 border-red-300 bg-red-50 dark:text-red-400 dark:bg-gray-800 dark:border-red-800',
        '3': 'flex p-4 mb-4 text-green-800 border-t-4 border-green-300 bg-green-50 dark:text-green-400 dark:bg-gray-800 dark:border-green-800',
        '4': 'flex p-4 mb-4 text-yellow-800 border-t-4 border-yellow-300 bg-yellow-50 dark:text-yellow-300 dark:bg-gray-800 dark:border-yellow-800',
        '5': 'flex p-4 border-t-4 border-gray-300 bg-gray-50 dark:bg-gray-800 dark:border-gray-600'
    };
    return alertClasses[alertId] || alertClasses['5']; // Default to class '5' if alertId is not found
}