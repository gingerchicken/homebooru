# Miscellaneous Project Information
In this document, I aim to cover some topics that I thought were important to me and the "culture of the project".

## Non-RESTful Endpoints
You may notice there are a few endpoints that are not RESTful, namely `/upload` and `/edit_tag`, the reason why is due to me trying to make the front-end as non-JavaScript dependent as possible - therefore I tend to use these endpoints to not only accept/validate the request but also render a response rather than just making them display a response in JSON.

I do intend on implementing a RESTful API for managing data in the future, this way this will allow developers to easily manage their data and interact with the server, however I still aim to make the front-end as functional as possible without using JavaScript (there will be some JavaScript in the front-end but I try my best to keep it to a minimum).

A lot of people dislike front-end JavaScript due to it often being exploited to fingerprint and track people as they browse the web, this is why many people disable JavaScript within their web browsers. I support this measure, which is why I wrote the front-end in this manor.

## Re-rolling Secret Key
I have added a feature that allows you to automatically generate a new secret key for your project, this is useful if you have accidentally lost your secret key or it was stolen.

This can be done by running the following command:
```bash
$ python manage.py createsecretkey
```

If you'd like docker to do this for you, then modify the `.env` file and set `ROLL_SECRET` to `True` - this will force the secret key to be re-rolled on startup.

```
ROLL_SECRET=True
```

Typically, this is automatically done on startup if a key isn't found in the `secret.txt` file. It is important to keep this file secure, as it is the key that is used to salt some session data.

There are some side effects of changing the secret key, as discussed in this [Stack Overflow answer](https://stackoverflow.com/a/52509362/8736749).