class AutoComplete {
    static AUTOCOMPLETE_URL = '/tags/autocomplete/';
    static DELAY = 200;

    #selector;

    constructor(searchBox, selector = '.autocomplete') {
        // Get the search box
        this.searchBox = searchBox;
        this.#selector = selector;
    }

    get autocomplete() {
        return document.querySelector(this.#selector);
    }

    /**
     * Gets the related tags from the server
     * @param {String} searchPhrase The search phrase 
     * @returns {Promise<Array>}
     */
    async getTags(searchPhrase) {
        // Get the last tag
        let lastTag = searchPhrase.trim().split(' ').pop();

        // If it starts with a -, ignore it
        if (lastTag.startsWith('-')) {
            lastTag = lastTag.slice(1);
        }

        // If it's empty, return
        if (lastTag.length === 0) {
            return [];
        }

        // URL encode the tag
        let encodedTag = encodeURIComponent(lastTag);

        // Get the tags
        let response = await fetch(AutoComplete.AUTOCOMPLETE_URL + encodedTag);

        // If the response is not ok, return
        if (!response.ok) {
            return [];
        }

        // Get the json
        let json = await response.json();

        // Return the tags
        return json;
    }

    /**
     * Creates a clickable tag element
     * @param {String} tag The tag
     * @param {Number} count Amount of posts with this tag
     * @param {String} type Type of tag
     * @param {Element} searchBox Trigger element
     * @returns {Element} The tag element
     */
    createTagElement(tag, count, type, searchBox) {
        let li = document.createElement('li');
        li.classList.add('option');
        li.classList.add('tag-type-' + type);

        let spanName = document.createElement('span');
        spanName.classList.add('name');
        spanName.innerText = tag;

        let spanCount = document.createElement('span');
        spanCount.classList.add('count');
        spanCount.innerText = count;

        li.appendChild(spanName);
        li.appendChild(spanCount);

        // Add the click event
        li.addEventListener('click', () => {
            // Add the tag to the search box
            this.addTag(tag, searchBox);
        });

        return li;
    }

    async updateOptions(searchPhrase, searchBox) {
        // Get the tags
        let tags = await this.getTags(searchPhrase);

        // Clear the options
        this.autocomplete.innerHTML = '';

        // Add the options
        for (let tag of tags) {
            let li = this.createTagElement(tag.tag, tag.total, tag.type, searchBox);
            this.autocomplete.appendChild(li);

            // Make the autocomplete visible
            this.autocomplete.style.display = '';
        }

        // Set the position of the autocomplete
        this.autocomplete.style.left = searchBox.offsetLeft + 'px';
    }

    clear() {
        this.autocomplete.innerHTML = '';
        this.autocomplete.style.display = 'none';
    }

    addTag(tag, searchBox) {
        let enteredTags = searchBox.value.trim().split(' ');
        enteredTags.pop();

        // Add the tag
        enteredTags.push(tag);

        // Join the tags
        let joinedTags = enteredTags.join(' ');

        // Set the value
        searchBox.value = joinedTags + ' ';

        // Clear the autocomplete
        this.clear();
    }

    #lastCheck = 0;
    addListeners() {
        for (let box of this.searchBox) {
            // Add a autocomplete element after the search box
            box.insertAdjacentHTML('afterend', '<div class="autocomplete"></div>');
        }

        // Add the keyup listener
        $(this.searchBox).on('keyup', (event) => {
            // Get the search phrase
            let searchPhrase = event.target.value;

            // Check if the box is empty
            if (searchPhrase.length === 0) {
                this.clear();
                return;
            }

            // Get the current time
            let currentTime = new Date().getTime();

            // If the last check was less than 500ms ago, return
            if (currentTime - this.#lastCheck < AutoComplete.DELAY) {
                return;
            }

            // Update the options
            this.updateOptions(searchPhrase, event.target);

            // Set the last check
            this.#lastCheck = currentTime;
        });
    }
}

// When the document is ready
$(document).ready(() => {
    // ui-autocomplete-input
    let input = $('.ui-autocomplete-input');

    // Create the autocomplete
    let autocomplete = new AutoComplete(input);

    // Add the listeners
    autocomplete.addListeners();
});