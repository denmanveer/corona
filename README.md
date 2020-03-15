## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This project is a simple script based on Python. It will send an email with latest stats on CoronaVirus confirmed cases from worldometers.info and canada.ca.

## Technologies
Project is created with:
* Python: 3.6.9
* Selenium: 3.141.0
* Chromedriver: 80.0.3987.87-0

## Setup

First install following packages:
```
$ sudo apt update
$ sudo apt install python3.6
$ sudo pip3 install selenium
$ sudo apt install chromium-chromedriver

```

Things to change:
* Edit the shebang of the script.
* On Line 84 add your email address and password (Which you can obtain from https://security.google.com/settings/security/apppasswords).
* On Line 86 add the sender email address.

To run this project:
```
corona_update.py -c China Canada India USA -e email1@gmail.com email2@gmail.com
```
(You can pass as many countries and email ids as you want)

