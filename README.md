[![Build](https://github.com/ChicoState/FriendHub/actions/workflows/actions.yml/badge.svg)](https://github.com/ChicoState/FriendHub/actions/workflows/actions.yml) 
# <img src="https://github.com/ChicoState/FriendHub/assets/101899800/1c407830-d0fa-4a33-b0f0-9b4be572b91e" alt="FriendHub" width="50" height="50" /> FriendHub - Your Location Sharing Service

FriendHub is a Django-based location-sharing application that allows users to connect with friends, share their real-time locations, and visualize how much of their location is visible to their friends. 


<i>Note: This group project is created for the Software Engineer Class at Chico State, please do not create any pull requests as they will not be accepted.</i>

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone git@github.com:ChicoState/FriendHub.git
$ cd FriendHub
```
Get your [Google Maps JS API Key](https://console.cloud.google.com/).
Then create a .env in the current directory & add your API key inside it like this:
```sh
$ API_KEY="<KEY>"
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ pip install virtualenv (if not installed already)
$ virtualenv env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies:
```sh
(env)$ python manage.py migrate
(env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`.

To leave virtual env:
```sh
(env)$ deactive
```
