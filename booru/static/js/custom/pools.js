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

    static async handleChanges() {
        let selected = Object.keys(DeleteMode.selectedThumbnails);
        if (selected.length === 0 || !DeleteMode.poolDeleteMode) {
            $('.pool-save-changes').hide();
            return;
        }

        // Show the save changes button
        $('.pool-save-changes').show();
    }

    static async handleDeleteChange() {
        // Update the button text
        $('.pool-delete').text(DeleteMode.poolDeleteMode ? 'Cancel Deletion' : 'Delete');

        if (DeleteMode.poolDeleteMode) {
            // Add .mode-active
            $('.pool-delete').addClass('mode-active');
        } else {
            // Remove .mode-active
            $('.pool-delete').removeClass('mode-active');
        }
        

        if (DeleteMode.poolDeleteMode) {
            let overlay = new OverlaySuccess();
            overlay.reloadOnOkay = false;
            overlay.show('Click on a post that you want to remove, once you have selected all that you need to remove, click on the save button.', 'Pool Delete Mode');
        } else {
            // Remove all deletion-selected classes
            $('.thumbnail-preview').removeClass('deletion-selected');

            // Clear the selected thumbnails
            DeleteMode.selectedThumbnails = {};
        }

        // Update the save changes button
        DeleteMode.handleChanges();
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
        DeleteMode.handleChanges();
    }

    static toggle() {
        DeleteMode.poolDeleteMode = !DeleteMode.poolDeleteMode;
        DeleteMode.handleDeleteChange();
    }

    static clickThumbnail(element) {
        if (!DeleteMode.poolDeleteMode) return;
        DeleteMode.handleThumbnailDeleteSelection(element);

    }

    static bind() {
        $('.pool-delete').click(function (e) {
            DeleteMode.toggle();
            return false;
        });

        $('.thumbnail-preview').click(function (e) {
            try {
                DeleteMode.clickThumbnail(this);
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