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

class OverlayInput extends OverlayMessage {
    constructor(elementId, verify = () => true) {
        super(elementId);

        this.verify = verify;
    }

    get icon() {
        return 'ui-icon-help';
    }

    /**
     * Shows the input overlay.
     * @param {String} question message question
     * @param {String} title message title
     * @param  {...any} args
     * @returns {Promise<String>} The inputted text
     */
    async show(question, title = 'Reason', failMessage = 'Invalid input, check that what you entered and try again.', ...args) {
        return new Promise((resolve, reject) => {
            let cancelButton = new OverlayButton('Cancel', () => {
                this.hide();

                reject();
            });
    
            let okButton = new OverlayButton('Okay', () => {
                // Get the text.
                let text = this.toString();

                // Verify the text.
                if (!this.verify(text)) {
                    // Show the error.

                    // Create an Okay button that re-shows this overlay.
                    let okayButton = new OverlayButton('Okay', () => {
                        this.show(question, title, ...args);
                    });

                    let error = new OverlayError();
                    error.show(failMessage, 'Error', okayButton);

                    return;
                }

                // Hide the overlay.
                this.hide();

                // Resolve the promise.
                resolve(text);
            });

            // Display the original message
            super.show(question, title, okButton, cancelButton, ...args);

            // Add the input box.
            let inputBox = document.createElement('div');
            inputBox.className = 'input-box';

            // Create a div for the input.
            let inputDiv = document.createElement('div');
            inputDiv.className = 'text-input';

            // Add the input.
            let input = document.createElement('input');
            input.type = 'text';

            // Add the input to the div.
            inputDiv.appendChild(input);

            // Add the div to the input box.
            inputBox.appendChild(inputDiv);

            // Append the input box above the buttons
            $(this.element).find('.buttons').before(inputBox);
        });
    }

    toString() {
        return $(this.element).find('.text-input input').val();
    }
}