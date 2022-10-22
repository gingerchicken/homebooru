class AdvancedAutoComplete extends AutoComplete {
    // TODO - Add the advanced autocomplete

    static QUOTES = ['"', '\'']; 
    static OPERATORS = {
        'AND': 'And',
        'OR': 'Or',
        '-': 'Not',
        'XOR': 'Xor',
        '(': 'Open Parenthesis',
        ')': 'Close Parenthesis',
        'IFF': 'If and only if',
        'IMP': 'Implies',
    }

    /**
     * 
     * @param {String} searchPhrase the search phrase
     * @returns {String} the last quote type, or null if there are no quotes
     */
    static getLastQuote(searchPhrase) {
        // Iterate backwards through the search phrase
        for (let i = searchPhrase.length - 1; i >= 0; i--) {
            // Get the character
            let char = searchPhrase[i];

            // If it's a quote, set the last quote
            if (AdvancedAutoComplete.QUOTES.includes(char)) {
                return char;
            }
        }
    }

    async getTag(searchPhrase) {
        // Get the last quote type
        let lastQuote = AdvancedAutoComplete.getLastQuote(searchPhrase);

        if (!lastQuote) {
            // This should never happen
            return [];
        }

        // Get the last tag
        let lastTag = searchPhrase.trim().split(lastQuote).pop();

        // Call the super method
        return await super.getTags(lastTag);
    }

    async getOperator(searchPhrase) {
        // Get the last tag
        let lastTag = searchPhrase.trim().split(' ').pop();

        // Get the related operators
        let operators = Object.keys(AdvancedAutoComplete.OPERATORS);

        // Get the operators that match the last tag
        let matchingOperators = lastTag.length == 0 ? operators : operators.filter(operator => operator.toLowerCase().startsWith(lastTag.toLowerCase()));

        // Sort the operators
        matchingOperators.sort();

        // Return the operators with their descriptions
        return matchingOperators.map(operator => {
            return {
                tag: operator,
                total: AdvancedAutoComplete.OPERATORS[operator], // This is will override the total part of the screen 
            };
        });
    }

    /**
     * Gets the total number of quotes in the search phrase
     * @param {String} searchPhrase the search phrase 
     * @returns {Number} the total number of quotes in the search phrase
     */
    getTotalQuotes(searchPhrase) {
        let totalQuotes = 0;
        let lastQuoteType = null;
        let escape = false;

        for (let char of searchPhrase) {
            // Check if the character is an escape character
            if (char === '\\') {
                escape = true;
                continue;
            }
            
            // Check if we are escaping
            if (escape) {
                escape = false;
                continue;
            }

            // We need to check if the quote is opened and is not escaped
            if (AdvancedAutoComplete.QUOTES.includes(char) && lastQuoteType !== char) {
                totalQuotes++;
                lastQuoteType = char;
            }

            // Check if the quote is closed
            if (lastQuoteType === char) {
                lastQuoteType = null;
            }
        }

        return totalQuotes;
    }

    /**
     * Gets if the last tag is an operator or a tag
     * @param {String} searchPhrase The search phrase
     * @returns {Boolean} True if the last tag is an operator, false if it's a tag
     */
    isLastOperator(searchPhrase) {
        let totalQuotes = this.getTotalQuotes(searchPhrase);

        // Check if there is an odd or even number of quotes
        return totalQuotes % 2 === 0;
    }

    async getTags(searchPhrase) {
        let totalQuotes = 0;
        for (let quote of AdvancedAutoComplete.QUOTES) {
            totalQuotes += searchPhrase.split(quote).length - 1;
        }

        // Check if there is an odd or even number of quotes
        if (totalQuotes % 2 === 0) {
            // Even number of quotes, get the operator
            return await this.getOperator(searchPhrase);
        } else {
            // Odd number of quotes, get the tag
            return await this.getTag(searchPhrase);
        }
    }

    addTag(tag, searchBox) {
        let searchPhrase = searchBox.value;

        // Check if we are dealing with an operator
        if (this.isLastOperator(searchPhrase)) {
            // Remove the last word from the search phrase
            searchPhrase = searchPhrase.trim().split(' ').slice(0, -1).join(' ');

            // Add the tag
            searchPhrase += ` ${tag} `;

            // Set the search phrase
            searchBox.value = searchPhrase;
        } else {
            // Get the last quote type
            let lastQuote = AdvancedAutoComplete.getLastQuote(searchPhrase);

            // Get the last tag
            let lastTag = searchPhrase.trim().split(lastQuote).pop();

            // Remove the last tag
            searchBox.value = searchPhrase.slice(0, searchPhrase.length - lastTag.length);

            // Add the tag
            searchBox.value += tag + lastQuote;
        }

        // Clear
        this.clear();
    }
}

// When the document is ready
$(document).ready(() => {
    // ui-autocomplete-input
    let input = $('.advanced');

    // Create the autocomplete
    let autocomplete = new AdvancedAutoComplete(input);

    // Add the listeners
    autocomplete.addListeners();
});