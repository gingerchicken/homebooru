# Homebooru
<div align="center">
    <img src="assets/cirno_smiling_touhou.png" width=500px \> <br>
    <img src="https://img.shields.io/badge/-Python 3-3776AB?style=flat&logo=Python&logoColor=white" \>
    <img src="https://img.shields.io/badge/PostgreSQL-3776AB.svg?logo=postgreSQL&amp;logoColor=white" \>
    <img src="https://img.shields.io/badge/Docker-3776AB.svg?logo=docker&amp;logoColor=white" \>
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
If you have any suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/gingerchicken/homebooru-rewritten). If you have a bit of knowledge with Python and Django, feel free to fork the repository and submit a pull request for new features.

### Debug Environment

### Enabling Django Debugging
In production, this should **NOT** be enabled - therefore I made sure that the `DEBUG` environment variable is set to `False` in the `.env` file by default. If you do want more information, you can enable it by setting the `DEBUG` environment variable to `True`.

### Unit testing
If you want to test the server, you simply need to define an environment variable `UNIT_TEST` to `True` in the `.env` file and restart the docker compose, instead of starting the application, it should instead run the unit tests.