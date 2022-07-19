class ViewPost {
    /**
     * Constructor for post viewer front-end
     * @param {String} csrfToken csrf token 
     * @param {Number} userId user id
     */
    constructor(csrfToken, userId = null) {
        this.csrfToken = csrfToken;
        this.userId = userId;
    }

    get #isAuthorised() {
        return this.userId !== null;
    }

    get headers() {
        return {
            'X-CSRFToken': this.csrfToken
        }
    }

    get profileUrl() {
        // TODO I think this should link back to the backend but whatever for now.
        return `/accounts/profile/${this.userId}`;
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

    // TODO add this to some units
    async #getStringError(resp) {
        // Get the msg
        let msg = await resp.text();

        if (msg.length !== 0) return false;

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
            error.show(this.#getStringError(resp) || msg);
        }

        return resp;
    }

    get postId() {
        // Get the last directory in the url
        let path = location.pathname.split('/');

        return Number(path[path.length - 1]);
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

    /**
     * Favourite the post
     * @returns {Promise<Response>} response
    */
    async favourite() {
        // Ask the user if they're sure they want to favourite the post
        let confirm = new OverlayConfirm();

        // Get the confirmation
        try {
            await confirm.show('Are you sure you want to favourite this post?');
        } catch (e) {
            return;
        }

        // Send the request to the server
        let resp = await this.request('POST', this.profileUrl + '/favourites', {
            post_id: this.postId
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully added this post to your favourites.', 'Success');
            return resp;
        }

        // Show an error if it was not accepted
        let error = new OverlayError();
        let msg = (await resp.text()).trim() || this.#getStringError(resp);
        
        error.show(msg);

        return resp;
    }
}