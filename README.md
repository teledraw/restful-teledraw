# What's Teledraw?

* Teledraw is the game of telephone combined with the game of pictionary.  
* Played in groups of at least 3, each player first submits a common word ("Inconceivable!"), phrase ("The bee's knees"), or sentence ("They don't think it be like it is, but it do.")
* Play rotates in a circle, with each player "passing" their phrase to the next player, and that player drawing a picture they feel represents that phrase (the 'draw' half of the name).
* The picture is then itself passed along, and interpreted back into a phrase by the next player (the 'tele' half).
* Rotating between drawings and phrases like this, when an idea gets back around the circle to the player whose phrase it originated as, the game is over.
* Most of the fun is in sharing the crazy ways that your ideas went off the rails with each other!

    ## OK, any tips for playing?
    * As with other popular remote party games, you'll need to join the same "room" as each other to play together.  You can't use the same room twice!
    * If you close or otherwise lose your browser tab during the game, join the room again with your same name in a new tab and all should be well.
    * Players can't join once the game starts!  Submit that first phrase only once you see everyone you expect to play in the room.
    
    ##Example
    Dan, Tracy, and Nate play Teledraw.  Dan submits 'money in the bank' as his first phrase.  When Tracy sees this in Round 2, she draws a stack of dollar bills inside a bank vault as her submission.  In Round 3, Nate sees the image, but mistakes the bank vault for a jail cell, and writes "Savings accounts are money jail" for his phrase.  Then, everyone looks at the results.  Hopefully, Dan is entertained by how his phrase was perverted, Tracy got to find out the fate of her image, and Nate got to discover the original meaning of the drawing he had to interpret.  Once they've looked at all the result threads together, the game is over!


# What's this repo?

This repository contains a REST API and a simple exemplary frontend for playing Teledraw across the Internet.  

The API is a Flask app written in Python 3.8.  The frontend is a React app.  For more details, see api/Pipfile and ui/package.json respectively.

## Useful Backend Commands
To use any of these, you'll need to first `pipenv install`
### To test the API
In the API directory, use `flask test`
### To run the API
In the API directory, use `flask run`

## Useful Frontend Commands
To use any of these, you'll need to first `npm install`
### To build the frontend
In the UI directory, use `npm run build`
### To test the frontend
In the API directory, use `npm run test`
### To run the frontend
In the UI directory, use `npm run start`
