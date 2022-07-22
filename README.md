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

#### Enabling Django Debugging
In production, this should **NOT** be enabled - therefore I made sure that the `DEBUG` environment variable is set to `False` in the `.env` file by default. If you do want more information, you can enable it by setting the `DEBUG` environment variable to `True`.

#### Accessing the Debugging Server
As I prepared the `docker-compose.yml` file for the server, I did not make the Django server accessible from the "direct" outside world, but instead through a reverse proxy.

Therefore, to get direct access to the server, you will need to add the following to the `docker-compose.yml` file in the `web` section:

```yml
web:
  ports:
    - "8000:8000"
```

*Feel free to disable the nginx image while debugging, but I recommend keeping it enabled for production.*

#### Live Reloading
By default, I prepared homebooru to be as ready as possible for production. This means that you will need to tweak the `docker-compose.yml` file to make sure that the server is reloaded when you make changes to the code. You can do this by passing through the workspace folder to `/code/` in the docker container.

You can do this by adding the following configuration to the `docker-compose.yml` file in the `web` section:

```yml
web:
    ...
    volumes:
      ...
      - .:/code
      ...
```

> Please bare in mind, if you have the default `.env` file, i.e. you haven't changed the "**ACTUAL_*something*_PATH**" variables, then this will pass through the database folder etc., which is not brilliant and should **NEVER** be used in production.

#### Unit testing
If you want to test the server, you simply need to define an environment variable `UNIT_TEST` to `True` in the `.env` file and restart the docker compose, instead of starting the application, it should instead run the unit tests.