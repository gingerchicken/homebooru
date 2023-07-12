function validateCreateForm(form) {
    let data = new FormData(form);

    let name = data.get('name');
    if (name.length < 3) {
        throw 'Pool name must be at least 3 characters long.';
    }

    if (name.length > 255) {
        throw 'Pool name must be at most 255 characters long.';
    }

    let description = data.get('description');
    if (description.length > 1024) {
        throw 'Pool description must be at most 1024 characters long.';
    }

    return true;
}

async function createPool(payload) {
    let response = await fetch('/pools', {
        method: 'POST',
        body: payload
    });

    if (response.status === 200) {
        // Get the body's data
        let data = await response.json();

        // Redirect to the pool's page
        window.location.href = `/pools/${data.id}`;
    } else {
        // Get the body's data as a string
        let data = await response.text();

        // Throw the error
        throw data;
    }
}

function getPoolId() {
    // Get the URL path
    let path = window.location.pathname;

    // It should be something like /pools/1
    // Split the path by /
    let split = path.split('/');
    if (split.length !== 3) {
        throw 'Invalid pool path.';
    }

    // Get the pool id
    let poolId = split[2];

    // Convert the pool id to an integer
    poolId = parseInt(poolId);

    // Check if the pool id is a number
    if (isNaN(poolId)) {
        throw 'Invalid pool id.';
    }

    return poolId;
}

// Encapsulates the delete mode.
class DeleteMode {
    static poolDeleteMode = false;
    static selectedThumbnails = {};

    /**
     * Updates the save changes button.
     */
    static #handleSaveButtonChanges() {
        let selected = Object.keys(DeleteMode.selectedThumbnails);
        if (selected.length === 0 || !DeleteMode.poolDeleteMode) {
            $('.pool-save-changes').hide();
            return;
        }

        // Show the save changes button
        $('.pool-save-changes').show();
    }

    /**
     * Updates the delete mode toggle button.
     */
    static #handleDeleteButtonChanges() {
        const e = $('.pool-delete');

        // Update the button text
        e.text(DeleteMode.poolDeleteMode ? 'Cancel Deletion' : 'Delete');

        // Add/Remove the mode-active class
        if (DeleteMode.poolDeleteMode) {
            // Add .mode-active
            e.addClass('mode-active');
        } else {
            // Remove .mode-active
            e.removeClass('mode-active');
        }
    }

    /**
     * Shows the message popup giving instructions on how to use the delete mode.
     */
    static #handleMessagePopup() {
        if (!DeleteMode.poolDeleteMode) return;

        let overlay = new OverlaySuccess();
        overlay.reloadOnOkay = false;
        overlay.show('Click on a post that you want to remove, once you have selected all that you need to remove, click on the save button.', 'Pool Delete Mode');
    }

    /**
     * Updates the stored thumbnails as well as their classes.
     */
    static #handleStoredThumbnails() {
        if (DeleteMode.poolDeleteMode) return;

        // Remove all deletion-selected classes
        $('.thumbnail-preview').removeClass('deletion-selected');

        // Clear the selected thumbnails
        DeleteMode.selectedThumbnails = {};
    }

    static handleDisplayPagination() {
        const e = $('.pagination');
        
        if (DeleteMode.poolDeleteMode) e.hide();
        else e.show();
    }

    /**
     * Updates all the changes that need to be made when the delete mode is toggled.
     */
    static async handleDeleteChange() {
        // Update the display pagination
        DeleteMode.handleDisplayPagination();

        // Update the delete button
        DeleteMode.#handleDeleteButtonChanges();

        // Update the message popup
        DeleteMode.#handleMessagePopup();

        // Update the stored thumbnails
        DeleteMode.#handleStoredThumbnails();

        // Update the save changes button
        DeleteMode.#handleSaveButtonChanges();
    }

    static async handleThumbnailDeleteSelection(element) {
        element = $(element);
        
        // Get the thumb class element
        let thumb = $(element).find('.thumb');
    
        // Get the element id
        let id = thumb.attr('id');
    
        // Remove the first s character
        id = id.substring(1);
    
        // Convert the id to an integer
        id = parseInt(id);

        // Check if the id is in the selected thumbnails
        if (id in DeleteMode.selectedThumbnails) {
            // Remove the thumbnail from the selected thumbnails
            delete DeleteMode.selectedThumbnails[id];
    
            // Remove the selected class
            element.removeClass('deletion-selected');
        } else {
            // Add the thumbnail to the selected thumbnails
            DeleteMode.selectedThumbnails[id] = true;
    
            // Add the selected class
            element.addClass('deletion-selected');
        }

        // Update the save changes button
        DeleteMode.#handleSaveButtonChanges();
    }

    static toggle() {
        DeleteMode.poolDeleteMode = !DeleteMode.poolDeleteMode;
        DeleteMode.handleDeleteChange();
    }

    static clickThumbnail(element) {
        if (!DeleteMode.poolDeleteMode) return false;
        DeleteMode.handleThumbnailDeleteSelection(element);
        return true;

    }

    static async saveChanges() {
        // Get the pool id
        let poolId = getPoolId();

        // Get the selected thumbnails as a list of post ids
        let selected = Object.keys(DeleteMode.selectedThumbnails).map(e => parseInt(e));

        // Send the request
        let response = await fetch(`/pools/${poolId}`, {
            method: 'DELETE',
            body: JSON.stringify({
                posts: selected
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        // Check if the response was successful
        if (response.status !== 200) {
            // Get the body's data as a string
            let data = await response.text();

            // Show the error as an overlay
            let err = new OverlayError();
            err.show(data);
            return;
        }

        // Successfully deleted the posts
        let overlay = new OverlaySuccess();
        overlay.show('Successfully deleted the posts from the pool.');

        // Disable delete mode
        if (DeleteMode.poolDeleteMode) DeleteMode.toggle();
    }

    static bind() {
        $('.pool-delete').click(function (e) {
            DeleteMode.toggle();
            return false;
        });

        $('.thumbnail-preview').click(function (e) {
            try {
                return !DeleteMode.clickThumbnail(this);
            } catch (e) {
                let err = new OverlayError();
                err.show(e);
            }

            return false;
        });

        $('.pool-save-changes').click(function (e) {
            DeleteMode.saveChanges();
            return true;
        });
    }
}

class ContentCreationTab {
    #tabName;
    #highlight;
    #parent;

    constructor(parent, tabName) {
        this.#parent = parent;
        this.#tabName = tabName;
    }

    get tabName() {
        return this.#tabName;
    }

    get tabId() {
        return this.#tabName.toLowerCase() + '-tab';
    }

    /**
     * Sets the highlight state of the tab.
     */
    set highlight(value) {
        if (value) {
            // Add the highlight class
            $(`.${this.tabId}`).addClass('selected');
        } else {
            // Remove the highlight class
            $(`.${this.tabId}`).removeClass('selected');
        }

        this.#highlight = value;
    }

    /**
     * Gets the highlight state of the tab.
     * @returns {Boolean} True if the tab is highlighted, false otherwise.
    */
    get highlight() {
        return this.#highlight;
    }

    createContainer() {
        let div = document.createElement('div');
        div.classList.add('tab-content');
        div.classList.add(this.tabId);

        return div;
    }

    createTab() {
        let id = this.tabId;

        let div = document.createElement('div');
        div.classList.add('tab');
        div.classList.add(id);

        // Create the tab's content
        let content = document.createElement('div');
        content.classList.add('tab-content');
        // Add the tab name to the content
        content.innerText = this.tabName;

        // Add the content to the tab
        div.appendChild(content);

        // Add the click event
        div.addEventListener('click', () => {
            this.#parent.selectTab(this.tabName);
        });

        return div;
    }

    async performAdd() {
        throw 'Not implemented.';
    }

    async addPosts(post) {
        let poolId = getPoolId();

        let formData = new FormData();
        formData.append('post', post);

        let resp = await fetch(`/pools/${poolId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        return resp;
    }
}

class SingularContentCreationTab extends ContentCreationTab {
    constructor(parent) {
        super(parent, 'Singular');
    }

    createContainer() {
        let div = super.createContainer();

        // Create the input
        let input = document.createElement('input');
        input.classList.add('singular-input');
        input.type = 'text';
        input.placeholder = 'Post ID';

        // Create a label
        let label = document.createElement('label');
        label.innerText = 'Post ID';

        // Add the label to the container
        div.appendChild(label);

        // Add the input to the contain
        div.appendChild(input);

        return div;
    }

    async performAdd() {
        // Get the input
        let input = $('.singular-input');

        console.log(input.val());

        // Get the number
        let postId = parseInt(input.val());

        // Check if the number is valid
        if (isNaN(postId)) {
            throw 'Invalid post id, it must be a number greater than or equal to 0.';
        }

        // Ensure that it is greater than or equal to 0
        if (postId < 0) {
            throw 'The post id must be greater than or equal to 0.';
        }

        // Send the request
        let resp = await this.addPosts([postId]);

        // Check if the response was successful
        if (resp.ok === false) {
            // Get the body's data as a string
            let data = await resp.text();
            throw data;
        }

        // Successfully added the post
        return true;
    }
}

class MultipleContentCreationTab extends ContentCreationTab {
    constructor(parent) {
        super(parent, 'Range');
    }

    createContainer() {
        let div = super.createContainer();

        // Create an input container in the form of a table
        // Such that it looks like this:

        // | From | To |
        // |  1   | 2  |

        let table = document.createElement('table');
        table.classList.add('range-input-table');

        // Create the from input
        let fromInput = document.createElement('input');
        fromInput.classList.add('from-input');
        fromInput.type = 'text';
        fromInput.placeholder = 'First ID to include';

        // Create the to input
        let toInput = document.createElement('input');
        toInput.classList.add('to-input');
        toInput.type = 'text';
        toInput.placeholder = 'Final ID to include';

        // Create the title row
        let titleRow = document.createElement('tr');

        // Create the from title
        let fromTitle = document.createElement('th');
        fromTitle.innerText = 'End';

        // Create the to title
        let toTitle = document.createElement('th');
        toTitle.innerText = 'Start';

        // Add the titles to the title row
        titleRow.appendChild(fromTitle);
        titleRow.appendChild(toTitle);

        // Create the input row
        let inputRow = document.createElement('tr');

        // Create the td for the from input
        let fromInputTd = document.createElement('td');

        // Create the td for the to input
        let toInputTd = document.createElement('td');

        // Add the inputs to the input row
        fromInputTd.appendChild(fromInput);
        toInputTd.appendChild(toInput);

        // Add the input row to the table
        inputRow.appendChild(fromInputTd);
        inputRow.appendChild(toInputTd);

        // Add the title row to the table
        table.appendChild(titleRow);

        // Add the input row to the table
        table.appendChild(inputRow);

        // Add the table to the container
        div.appendChild(table);

        return div;
    }
}

class PoolPostOverlay extends OverlayMessage {    
    #tabs;

    constructor(elementId) {
        super(elementId);
        
        this.#tabs = [
            new SingularContentCreationTab(this),
            new MultipleContentCreationTab(this)
        ];
    }

    get icon() {
        return 'ui-icon-help';
    }

    #createTabs() {
        // Create the tabs
        let tabContainer = document.createElement('div');
        tabContainer.classList.add('tabs');

        for (let tab of this.#tabs) {
            // Create the tab
            let tabElement = tab.createTab(tab.tabName);

            // Add the tab to the container
            tabContainer.appendChild(tabElement);
        }

        // Add the tabs to the overlay
        return tabContainer;
    }

    selectTab(tabName) {
        for (let tab of this.#tabs) {
            tab.highlight = tab.tabName === tabName;
        }

        // Destroy the current content
        $(this.element).find('.message > .tab-content').remove();

        // Create the new content
        let content = this.#tabs.find(e => e.tabName === tabName).createContainer();

        // Add the content to the overlay
        $(this.element).find('.message').append(content);
    }

    show() {
        let cancelButton = new OverlayButton('Cancel', () => {
            this.hide();
        });

        let okButton = new OverlayButton('Okay', async () => {
            let tab = this.#tabs.find(e => e.highlight);

            if (tab === undefined) {
                let err = new OverlayError();
                err.show('Please select a tab.');
                return;
            }

            // Perform the add
            try {
                await tab.performAdd();
            }
            catch (e) {
                let err = new OverlayError();
                err.show(e);
                
                // TODO recover from error and re-populate the overlay
                throw e;
                return;
            }

            let overlay = new OverlaySuccess();
            overlay.show('Successfully added the post(s) to the pool.');
        });

        super.show('', 'Add Content', okButton, cancelButton);

        // Add the tabs
        $(this.element).find('.message').append(this.#createTabs());

        this.selectTab(this.#tabs[0].tabName);
    }
}

$(document).ready(function () {
    $('.pool-create-form').submit(function (e) {
        e.preventDefault();

        try {
            validateCreateForm(this);
        } catch (e) {
            let err = new OverlayError();
            err.show(e);
            return;
        }

        // Create pool
        createPool(new FormData(this)).catch(e => {
            let err = new OverlayError();
            err.show(e);
        });
    });

    $('.pool-add-post').click(function (e) {
        let overlay = new PoolPostOverlay();
        overlay.show();
    });

    DeleteMode.bind();
});