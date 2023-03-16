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
});