# Miscellaneous Project Information
In this document, I aim to cover some topics that I thought were important to me and the "culture of the project".

## Non-RESTful Endpoints
You may notice there are a few endpoints that are not RESTful, namely `/upload` and `/edit_tag`, the reason why is due to me trying to make the front-end as non-JavaScript dependent as possible - therefore I tend to use these endpoints to not only accept/validate the request but also render a response rather than just making them display a response in JSON.

I do intend on implementing a RESTful API for managing data in the future, this way this will allow developers to easily manage their data and interact with the server, however I still aim to make the front-end as functional as possible without using JavaScript (there will be some JavaScript in the front-end but I try my best to keep it to a minimum).

A lot of people dislike front-end JavaScript due to it often being exploited to fingerprint and track people as they browse the web, this is why many people disable JavaScript within their web browsers. I support this measure, which is why I wrote the front-end in this manor.
