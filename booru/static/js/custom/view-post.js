class PoolOverlay extends OverlayMessage {
    #selectedPoolId = null;
    
    constructor(elementId) {
        super(elementId);
    }

    get icon() {
        return 'ui-icon-help';
    }

    setSelectedPool(poolId) {
        this.#selectedPoolId = poolId;
    }

    get selectedPool() {
        return this.#selectedPoolId;
    }

    createPoolList(pools = []) {
        // Create a table
        let table = document.createElement('table');
        table.classList.add('pool-table');

        // Create the headers
        let headers = document.createElement('tr');
        // Name, Description, Creator
        headers = ['Name', 'Description', 'Creator', 'Posts'].map(text => {
            let th = document.createElement('th');
            th.innerText = text;

            return th;
        });

        // Add the headers to the table
        for (let header of headers) {
            table.appendChild(header);
        }

        // Add the pools to the table
        for (let pool of pools) {
            let row = document.createElement('tr');

            // Add the name
            let name = document.createElement('td');
            // Create a link
            let link = document.createElement('a');
            link.href = `/pools/${pool.id}`;
            // Make it open in a new tab
            link.target = '_blank';
            link.innerText = pool.name;
            name.appendChild(link);
            row.appendChild(name);

            // Add the description
            let description = document.createElement('td');
            description.innerText = pool.description || 'No description';
            row.appendChild(description);

            // Add the creator
            let creator = document.createElement('td');
            creator.innerText = pool.creator;
            row.appendChild(creator);

            // Add the description
            let totalPosts = document.createElement('td');
            totalPosts.innerText = pool.total_posts;
            row.appendChild(totalPosts);

            // Add on click event
            row.addEventListener('click', () => {
                // Remove the selected class from all rows
                for (let row of table.querySelectorAll('tr')) {
                    row.classList.remove('selected');
                }

                if (pool.id === this.selectedPool) {
                    this.setSelectedPool(null);
                    return;
                }

                // Set the selected pool
                this.setSelectedPool(pool.id);
                row.classList.add('selected');
            });

            // Add the row to the table
            table.appendChild(row);
        }

        return table;
    }

    async createTableFromSearch(phrase = '') {
        let pools = [];

        // Get the pools from the server
        let response = await fetch(`/pools?search=${phrase}&json=true`);

        // Get the response as json
        let data = await response.json();

        // Add the pools to the list
        for (let pool of data) {
            pools.push({
                name: pool.name,
                description: pool.description,
                total_posts: pool.total_posts,
                creator: pool.creator,
                id: pool.id
            });
        }

        // Remove the no pools message
        let noPools = this.element.querySelector('.no-pools');
        if (noPools) {
            noPools.remove();
        }

        // Check if there are any pools
        if (pools.length === 0) {
            // Create a message
            let message = document.createElement('p');
            message.innerText = 'No pools found.';
            message.classList.add('no-pools');

            return message;
        }

        // Create the table
        let table = this.createPoolList(pools);

        return table;
    }

    async show() {
        return new Promise(async (resolve, reject) => {
            let addButton = new OverlayButton('Add', () => {
                this.hide();

                resolve(this.selectedPool);
            });

            let cancelButton = new OverlayButton('Cancel', () => {
                this.hide();

                reject('cancelled');
            });

            // Create the base message
            super.show('Add the image to a given pool', 'Pooling', addButton, cancelButton);
            const messageBox = this.element.querySelector('.message');

            // Create the form
            let form = document.createElement('form');
            form.classList.add('pool-add-form');

            // Create the search bar
            let search = document.createElement('input');
            search.type = 'text';
            search.placeholder = 'Search for a pool ...';
            search.classList.add('pool-search');
            search.addEventListener('input', async () => {
                // Remove the table
                let table = messageBox.querySelector('.pool-table');
                if (table) {
                    table.remove();
                    // Reset the selected pool
                    this.setSelectedPool(null);
                }

                // Create the table
                table = await this.createTableFromSearch(search.value);

                // Add the table to the message box
                form.appendChild(table);
            });

            // Add the search bar to the form
            form.appendChild(search);

            // Create the table
            // TODO get this from the server
            let table = await this.createTableFromSearch();

            // Add the table to the message box
            form.appendChild(table);

            // Add the form to the message box
            messageBox.appendChild(form);
        });
    }
}

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

        return msg;
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

            let msg = await this.#getStringError(resp);
            error.show(msg);
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

        // POST the data to the server
        let resp = await this.request('POST', `${location.pathname}/flag`, {
            reason
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully flagged post.', 'Success');

            return resp;
        }

        // Show an error message
        let error = new OverlayError();
        let msg = (await resp.text()) || this.#getStringError(resp);

        error.show(msg);

        return resp;
    }

    /**
     * Unflag the post
     * @returns {Promise<Response>} response
     */
    async unflag() {
        // Check if the user wants to unflag the post
        let confirm = new OverlayConfirm();

        // Get the confirmation
        try {
            await confirm.show('Are you sure you want to unflag this post?');
        } catch (e) {
            return;
        }

        // Send the request to the server
        let resp = await this.request('DELETE', `${location.pathname}/flag`);

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully unflagged post.', 'Success');

            return resp;
        }

        // Show an error message
        let error = new OverlayError();
        let msg = (await resp.text()) || this.#getStringError(resp);

        error.show(msg);

        return resp;
    }

    /**
     * Favourite the post
     * @returns {Promise<Response>} response
    */
    async favourite() {
        // Make sure that we are logged in
        if (!this.#isAuthorised) {
            // Show an error message
            let error = new OverlayError();
            error.show('You must be logged in to favourite a post.');

            // This must be done as it will try and request something along the lines of /null/favourites
            // which will cause an error ...

            return;
        }

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

    /**
     * Post a comment
     * @param {String} comment comment text
     * @param {Boolean} anonymous if the comment was posted anonymously
     * @param {Boolean} showSuccessMessage if a message should be shown on success
     * @returns {Promise<Response>} response
    */
    async comment(comment, anonymous = false, showSuccessMessage = false) {
        let resp = await this.request('POST', this.postId + '/comments', {
            comment: comment,
            as_anonymous: anonymous
        });

        if (!resp.ok) {
            // Show an error if it was not accepted
            let error = new OverlayError();

            let msg = (await resp.text()).trim() || this.#getStringError(resp);
            error.show(msg);
            
            return resp;
        }

        if (showSuccessMessage) {
            // Show a success message
            let message = new OverlaySuccess();

            let msg = anonymous ? 'Successfully posted comment anonymously.' : 'Successfully posted comment.';
            message.show(msg, 'Success');

            // Finish
            return resp;
        }

        // Else ...

        // Reload the page
        location.reload();
        
        return resp;
    }

    /**
     * Add post to pool
     * @returns {Promise<Response>} response
     */
    async pool() {
        // Make sure that we are logged in
        if (!this.#isAuthorised) {
            // Show an error message
            let error = new OverlayError();
            error.show('You must be logged in to add a post to a pool.');

            // This must be done as it will try and request something along the lines of /null/favourites
            // which will cause an error ...

            return;
        }

        // Show the pool overlay
        let overlay = new PoolOverlay();
        let selectedId;

        try {
            selectedId = await overlay.show();
        } catch (e) {
            // Handle cancelled
            if (e === 'cancelled') return;

            // Else throw the error
            throw e;
        }

        // Handle no pool selected
        if (!selectedId) {
            // Show an error message
            let error = new OverlayError();
            error.show('You must select a pool to add the post to.');
            
            return;
        }

        let resp = await this.request('POST', `/pools/${selectedId}`, {
            post: this.postId
        });

        if (resp.ok) {
            // Show a success message
            let message = new OverlaySuccess();
            message.show('Successfully added this post to the pool.', 'Success');
            return resp;
        }

        // Show an error if it was not accepted
        let error = new OverlayError();
        let msg = (await resp.text()).trim() || this.#getStringError(resp);

        error.show(msg);

        return resp;
    }
}