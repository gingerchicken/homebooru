function saveSearchPhrase() {
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
        return;
    }

    const saveEndpoint = "/tags/savedsearches"
    let payload = {
        searchPhrase: searchPhrase
    }

    // TODO Send the search phrase to the server
}