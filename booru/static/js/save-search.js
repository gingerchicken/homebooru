async function saveSearchPhrase(csfrToken) {
    // Get the search phrase
    const searchInputIds = ["tags-search", "search-input"] // For some unholy reason, the search input has multiple ids

    let searchInput;
    for (let i in searchInputIds) {
        searchInput = $(`#${searchInputIds[i]}`);
        if (searchInput.length) {
            break;
        }
    }

    let searchPhrase = searchInput.val();

    // Clean the search phrase
    searchPhrase = searchPhrase.trim();

    // Remove any double spaces
    searchPhrase = searchPhrase.replace(/\s+/g, ' ');

    // Check if the search phrase is empty
    if (searchPhrase.length === 0) {
        let errorMessage = new OverlayError();
        errorMessage.show('Search phrase cannot be empty.', 'Error');
        return;
    }

    const saveEndpoint = "/tags/savedsearches"
    let formData = new FormData();
    formData.append("searchPhrase", searchPhrase);

    // Save the search phrase
    let resp = await fetch(saveEndpoint, {
        method: "POST",
        headers: {
            "X-CSRFToken": csfrToken,
        },
        body: formData,
    });

    if (resp.ok) {
        // Show success message
        let message = new OverlaySuccess();
        message.show('Successfully saved search phrase.', 'Success');
        return;
    }

    let errorMessage = new OverlayError();
    errorMessage.show(await resp.text(), 'Error');
}

async function deleteSearchPhrase(csfrToken, phraseId) {
    const deleteEndpoint = `/tags/savedsearches/${phraseId}`;

    // Confirm deletion
    let confirm = new OverlayConfirm();
    try {
        await confirm.show('Are you sure you want to delete this search phrase?');
    } catch (e) {
        return;
    }

    let resp = await fetch(deleteEndpoint, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csfrToken,
        },
    });

    if (resp.ok) {
        // Show success message
        let message = new OverlaySuccess();
        message.show('Successfully deleted search phrase.', 'Success');
        return;
    }

    let errorMessage = new OverlayError();
    errorMessage.show(await resp.text(), 'Error');
}