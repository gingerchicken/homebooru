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
    request(method, url = location.href) {
        return fetch(url, {
            method,
            headers: this.headers
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
}