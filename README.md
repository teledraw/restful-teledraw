# What's Teledraw?

* Teledraw is the game of telephone combined with the game of pictionary.  
* Played in groups of at least 3, each player first submits a common word ("Inconceivable!"), phrase ("The bee's knees"), or sentence ("They don't think it be like it is, but it do.")
* Play rotates in a circle, with each player "passing" their phrase to the next player, and that player drawing a picture they feel represents that phrase (the 'draw' half of the name).
* The picture is then itself passed along, and interpreted back into a phrase by the next player (the 'tele' half).
* Rotating between drawings and phrases like this, when an idea gets back around the circle to the player whose phrase it originated as, the game is over.
* Most of the fun is in sharing the crazy ways that your ideas went off the rails with each other!

# What's this repo?

This repository contains a REST API and a simple exemplary frontend for playing Teledraw across the Internet.  

The API is a Flask app written in Python 3.8.  The frontend is a React app.  For more details, see api/Pipfile and ui/package.json respectively.

## Useful Backend Commands
### To build the API
In the API directory, use `./gradlew build`
### To build the API
In the API directory, use `./gradlew test`
### To run the API
In the API directory, use `./gradlew bootRun`

## Useful Frontend Commands
To use any of these, you'll need to first `npm install`
### To build the frontend
In the UI directory, use `npm run build`
### To test the frontend
In the API directory, use `npm run test`
### To run the frontend
In the UI directory, use `npm run start`
