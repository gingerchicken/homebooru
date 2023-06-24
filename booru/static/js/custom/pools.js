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

    DeleteMode.bind();
});