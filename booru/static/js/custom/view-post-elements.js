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

/**
 * Shows the new comment form
 */
function toggleCommentBox() {
    // Get the new comment form
    const form = $('#comment-section > .comments');

    // Toggle the form's visibility
    form.toggle();

    return false;
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
});