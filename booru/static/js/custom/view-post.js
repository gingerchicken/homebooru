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
        // Send a delete request to the server
        let response = await this.request('DELETE');

        // Follow the redirect
        if (response.redirected) {
            return location.href = response.url;
        }
    }
}