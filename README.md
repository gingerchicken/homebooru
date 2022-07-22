# Homebooru
<div align="center">
    <img src="assets/cirno_smiling_touhou.png" width=500px \>
    <p><i><small>Artwork by <a href="https://twitter.com/nvi2762/status/1495867899881619456">Navi</a></small></i></p>
    <img src="https://img.shields.io/badge/-Python 3-3776AB?style=flat&logo=Python&logoColor=white" \>
    <img src="https://img.shields.io/badge/PostgreSQL-3776AB.svg?logo=postgreSQL&amp;logoColor=white" \>
    <img src="https://img.shields.io/badge/Docker-3776AB.svg?logo=docker&amp;logoColor=white" \><br>
    <img src="https://github.com/gingerchicken/homebooru/actions/workflows/test.yml/badge.svg" \>
    <p>A self-hosted <a href="https://www.yourdictionary.com/booru">Booru</a> written in <a href="https://www.djangoproject.com/">Python (Django)</a> for storing and sorting large media collections.</p>
</div>

## Installation
Included with the repository is a Docker compose configuration file, this should set everything up for you automatically. You can run the following command to start the server:

```bash
$ docker-compose up --build
```

## Configuration
By default, since the PostgreSQL database should be locked off from the rest of the network, the server will have a default username and password of `homebooru` and `H0meboOru!420`. You can change these by editing the `.env` file in the root directory.

## Contributions
If you have any suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/gingerchicken/homebooru). If you have a bit of knowledge with Python and Django, feel free to fork the repository and submit a pull request for new features. Before contributing to the project, I would recommend reading some of the [Miscellaneous Project Information](/docs/MISC.md) to understand why certain things are implemented in certain ways and maybe what ethics you should work with when contributing (such as the low JavaScript dependence).

### Debug Environment
To make it easier to debug, I have created a `docker-compose.yml` file alongside a `.env` file, in the [`.debug`](.debug) directory.

This file is similar to the main `docker-compose.yml` file, but with the following differences:

- Persistent volumes are not used (i.e. no `volumes` section)
- The `nginx` container is not used.
- By default, **the container will only run unit tests** - (this is mainly to encourage contributors to write tests for their own code).
- Direct pass-through to the Django debug server is enabled. (by default, the port is set to `8000`)

That all sounds great, but how do I use this environment? This is very straight forward - just run the following command:

```bash
# Move to the .debug directory
$ cd .debug

# Run the debug environment
$ docker-compose up --build
```

And to stop the environment, run the following command (while in the .debug directory, of course):

```bash
$ docker-compose down
```

#### Enabling the Debug Web Server
As you may have read earlier, the debug environment is setup to run unit tests and close the server after the tests are complete, however sometimes you might want a more live/real-time server. To enable this, simply set `UNIT_TEST` to `False` in the [**debug** `.env`](.debug/.env) file like so:

```env
UNIT_TEST=False
```