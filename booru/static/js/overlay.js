class PageOverlay {
    constructor(elementId = 'overlay') {
        this.elementId = elementId;
    }

    /**
     * The overlay element.
     */
    get element() {
        return document.getElementById(this.elementId);
    }

    /**
     * Makes the overlay visible.
    */
    show() {
        $(this.element).show();
    }

    /**
     * Makes the overlay invisible.
    */
    hide() {
        $(this.element).hide();

        // Clear the overlay's contents.
        this.element.innerHTML = '';
    }
}

class OverlayButton {
    constructor(text, callback = () => {}) {
        this.text = text;
        this.callback = callback;
    }

    get html() {
        return this.text;
    }

    createElement() {
        let button = document.createElement('button');

        // Add the styling classes
        button.className = `button button-${this.text.toLowerCase()}`;
        
        // Add the html
        button.innerHTML = this.html;

        // Add the listener.
        button.addEventListener('click', this.callback);

        return button;
    }
}

class OverlayMessage extends PageOverlay {
    constructor(elementId) {
        super(elementId);
    }

    get icon() {
        return 'ui-icon-info'
    }

    show(message, title = 'Message', ...buttons) {
        // Clear the message.
        this.element.innerHTML = '';

        // Create the message box
        let messageBox = document.createElement('div');
        messageBox.className = 'message-box';

        // Create the title.
        let titleElement = document.createElement('div');
        titleElement.className = 'message-title';

        // Add icon
        let icon = document.createElement('span');
        icon.className = `ui-icon ${this.icon}`;
        titleElement.appendChild(icon);

        let titleText = document.createElement('span');
        titleText.innerHTML = title;
        titleElement.appendChild(titleText);

        // Create the message.
        let messageElement = document.createElement('div');
        messageElement.className = 'message';

        let messageText = document.createTextNode(message);
        messageElement.appendChild(messageText);

        // Append the elements
        messageBox.appendChild(titleElement);
        messageBox.appendChild(messageElement);

        // Create the buttons.
        let buttonsElement = document.createElement('div');
        buttonsElement.className = 'buttons';

        // By default add an OK button.
        if (buttons.length === 0) {
            buttons.push(new OverlayButton('Okay', () => {
                this.hide();
            }));
        }

        // Create the buttons.
        for (let b of buttons) {
            buttonsElement.appendChild(b.createElement());
        }
        
        // Append the buttons to the message box.
        messageBox.appendChild(buttonsElement);

        // Append the message box to the overlay.
        this.element.appendChild(messageBox);

        // Show the overlay.
        super.show();
    }
}

class OverlayError extends OverlayMessage {
    constructor(elementId) {
        super(elementId);
    }

    get icon() {
        return 'ui-icon-alert'
    }

    show(message, title = 'Error', ...args) {
        super.show(message, title, ...args);

        // Add the error class to the message box.
        $(this.element).find('.message').addClass('error');
    }
}

class OverlayConfirm extends OverlayMessage {
    constructor(elementId) {
        super(elementId);
    }

    get icon() {
        return 'ui-icon-help'
    }

    async show(question, title = 'Confirmation', ...args) {
        return new Promise((resolve, reject) => {
            // Create Yes and No buttons.
            let yesButton = new OverlayButton('Yes', () => {
                this.hide();

                resolve();
            });

            let noButton = new OverlayButton('No', () => {
                this.hide();

                reject();
            });

            // Show the message.
            super.show(question, title, yesButton, noButton, ...args);
        });
    }
}

class OverlaySuccess extends OverlayMessage {
    constructor(elementId) {
        super(elementId);
    }

    get icon() {
        return 'ui-icon-check'
    }

    show(message, title = 'Success', ...args) {
        let successButton = new OverlayButton('Okay', () => {
            // Refresh the page.
            window.location.reload();
        });

        super.show(message, title, successButton, ...args);

        // Add the success class to the message box.
        $(this.element).find('.message').addClass('success');
    }
}