class ViewPost {
    constructor(csrfToken) {
        this.csrfToken = csrfToken;
    }

    get headers() {
        return {
            'X-CSRFToken': this.csrfToken
        }
    }

    /**
     * Basic request wrapper
     * @param {String} method request method
     * @param {String} url url
     * @returns {Promise<Response>} response
     */
    request(method, url = location.href, data = {}) {
        // Convert the data to FormData
        let formData = new FormData();

        for (let key in data) {
            formData.append(key, data[key]);
        }

        // Send the request
        return fetch(url, {
            method: method,
            headers: this.headers,
            body: formData
        });
    }

    /**
     * Delete the post
     */
    async delete() {
        let confirm = new OverlayConfirm();

        try {
            await confirm.show('Are you sure you want to delete this post?');
        } catch (e) {
            return;
        }

        // Send a delete request to the server
        let response = await this.request('DELETE');

        // Handle 302
        if (response.redirected) {
            return location.href = response.url;
        }

        // Handle 403
        if (response.status === 403) {
            let error = new OverlayError();

            error.show('You do not have permission to delete this post.');
            return;
        }
    }

    /**
     * Edit the post
     * @param {Object} data post data
     * @returns {Promise<Response>} response
    */
    async edit(data = {}, showError = true) {
        // Send a PUT request to the server
        let resp = await this.request('POST', location.href, data);

        if (showError && !resp.ok) {
            // Show an error if it was not accepted
            let error = new OverlayError();

            let msg = await resp.text();

            // TODO add this to the request function
            if (msg.length === 0) {
                switch (resp.status) {
                    case 400:
                        msg = 'Malformed request.';
                        break;
                    case 403:
                        msg = 'You do not have permission to edit this post.';
                        break;
                    case 404:
                        msg = 'The post was not found.';
                        break;
                    default:
                        msg = 'An unknown error occurred.';
                        break;
                }
            }

            error.show(msg);
        }

        return resp;
    }

    /**
     * Lock the post
     * @returns {Promise<Response>} response
    */
    async lock() {
        // Check if the user wants to lock the post
        let confirm = new OverlayConfirm();

        // Get the confirmation
        try {
            await confirm.show('Are you sure you want to lock this post?');
        } catch (e) {
            return;
        }

        // Send the request to the server
        let resp = await this.edit({
            locked: true
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully locked post.', 'Success');
        }

        return resp;
    }

    /**
     * Unlock the post
     * @returns {Promise<Response>} response
     */
    async unlock() {
        // Check if the user wants to unlock the post
        let confirm = new OverlayConfirm();

        // Get the confirmation
        try {
            await confirm.show('Are you sure you want to unlock this post?');
        } catch (e) {
            return;
        }

        // Send the request to the server
        let resp = await this.edit({
            locked: false
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully unlocked post.', 'Success');
        }

        return resp;
    }

    /**
     * Flag the post for deletion
     * @returns {Promise<Response>} response
    */
    async flag() {
        let validate = (str) => {
            // Strip the string
            str = str.trim();

            // Check if the string is empty
            return (str.length > 0);
        };

        let overlay = new OverlayInput(undefined, validate);

        let reason;
        try {
            reason = await overlay.show(
                'Enter a reason for flagging this post:',
                'Flag Post',
                'Invalid reason, please try again.'
            );
        } catch (e) {
            return;
        }

        // Send the request to the server
        let resp = await this.edit({
            delete_flag: reason
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully flagged post.', 'Success');
        }

        return resp;
    }
}