/**
 * Shows the image overlay when the user clicks on the image
 */
function displayImageOverlay() {
    // Get the image overlay
    const overlay = $('#image-overlay');

    // Get the image overlay's image
    const image = overlay.find('img');

    // Get the value of the media-src attribute
    let src = image.attr('media-src');

    // Add an src attribute to the image and make it equal to media-src
    image.attr('src', src);

    // Disable scrolling
    $('body').css('overflow', 'hidden');

    // Show the overlay
    overlay.show();
}

/**
 * Hides the image overlay
 */
function hideImageOverlay() {
    // Get the image overlay
    const overlay = $('#image-overlay');

    // Enable scrolling
    $('body').css('overflow', 'auto');

    // Hide the overlay
    overlay.hide();

    return false;
}

/**
 * Opens the original image in a new tab
 * @param {String} src The source of the image
 */
function openOriginal(src) {
    // Open the image in a new tab
    window.open(src, '_blank');

    return false;
}

/**
 * Downloads the image
 * @param {String} src The source of the image
 */
function downloadOriginal(src) {
    // Create a link to the image
    const link = document.createElement('a');

    // Set the href attribute to the image's src
    link.href = src;

    // Set the download attribute to the image's src
    link.download = src;

    // Click the link
    link.click();
}

function updateFormTitle(form, title = null) {
    const NORTH_CARET = 'ui-icon-caret-2-n';
    const SOUTH_CARET = 'ui-icon-caret-2-s';

    // Get the title
    title = title ? title : form.find('.title');

    // Get the icon
    let icon = title.find('.ui-icon');

    // If the form is visible then make it a north arrow
    if (form.is(':visible')) {
        icon.removeClass(SOUTH_CARET).addClass(NORTH_CARET);
    } else {
        // Otherwise make it a south arrow
        icon.removeClass(NORTH_CARET).addClass(SOUTH_CARET);
    }
    
    return false;
}

/**
 * Shows the new comment form
 */
function toggleCommentBox() {
    // Get the new comment form
    let form = $('#comment-section > .comments');

    // Toggle the form's visibility
    form.toggle();

    // Update the form's title
    updateFormTitle($('#comment-section > .comments'), $('#comment-section > .title'));

    return false;
}

/**
 * Shows the edit form
 */
function toggleEditForm() {
    // Get the edit form
    let form = $('#edit-box > form');

    // Toggle the form's visibility
    form.toggle();

    // Update the form's title
    updateFormTitle(form, $('#edit-box > .title'));

    return false;
}

/**
 * Sends the comment from the comment section
 * @returns {Promise} response from the server
 */
function sendComment() {
    // Get the comment text area
    const textarea = $('#comment');

    // Get the comment text
    let comment = textarea.val();

    // Try and get .anonymous > input:nth-child(1)
    let anonymousElement = $('.anonymous > input:nth-child(1)');
    let anonymous = anonymousElement.length !== 0 ? anonymousElement.prop('checked') : false;

    // Check if view is defined
    if (typeof view === 'undefined') {
        return comment;
    }

    // Send the comment
    return view.comment(comment, anonymous);
}

async function sendEdit() {
    // Get the edit form
    const form = $('#edit-box > form');

    // Parse it into a FormData object
    const formData = new FormData(form[0]);

    // Get the title
    let title = formData.get('title');

    // Get the tags
    let tags = formData.get('tags');
    // Get them as an array
    tags = tags.split(' ');
    // Strip any whitespace from the tags
    tags = tags.map(tag => tag.trim());
    // Remove any empty strings
    tags = tags.filter(tag => tag !== '');
    // Join the tags back together
    tags = tags.join(' ');

    // Check if the tags are empty
    if (tags.length === 0) {
        // Show an error message
        let error = new OverlayError();
        error.show('Each post must have at least one tag, please check your tags and try again.');
        return;
    }

    // Get the rating
    let rating = formData.get('rating');

    // Get the source
    let source = formData.get('source');

    // Generate the payload
    const payload = {
        rating, tags, title, source
    }

    // Send the edit
    let resp = await view.edit(payload);

    // If the response is okay then reload the page
    if (!resp.ok) return;

    // Reload the page
    location.reload();
}

// On document ready
$(document).ready(() => {
    // Add a click listener to #image
    $('#image').click(() => {
        // Display the image overlay
        displayImageOverlay();
    });

    // Add a click listener to #image-overlay
    $('#image-overlay').click((e) => {
        // Make sure the click was image-overlay background
        if (e.target.id !== 'image-overlay') return;

        // Hide the image overlay
        hideImageOverlay();
    });

    // Add the cursor point to the image
    // (I am doing this dynamically as non-javascript users will not see this)
    $('#image').css('cursor', 'pointer');

    // Add the comment section toggle
    $('#comment-section > .title').click((e) => {
        // Toggle the comment box
        toggleCommentBox();
    });

    // Add the comment submit button
    $('.new-comment > * > .submit').click((e) => {
        // Send the comment
        sendComment();
    });

    // Add anonymous check button
    $('.new-comment > * > .anonymous').click((e) => {
        // Get the element
        const element = $(e.target);

        // Get the input
        const input = element.find('input');

        // Toggle the input
        input.prop('checked', !input.prop('checked'));
    });

    // Add toggle edit form button
    $('#edit-box > .title').click((e) => {
        // Toggle the edit form
        toggleEditForm();
    });

    // Add the edit submit button
    $('#edit-box > form > .submit').click((e) => {
        sendEdit();

        return false;
    });
});