# RedditClone
 
Python version: 3.7.3
Pycharm IDE
Flask, SQLAlchemy, SQLlite

Run cli.commands: "Flask *command*"

Used Postman to do curl commands


Running postman: insert URL right behind locahost:5000/
register() & make_post(): requires keys that are specified in the request.form code
Make sure to change method when testing (GET, POST, etc)

list_post_sub:requires you to enter both the subreddit and the nth number
ex) http://localhost:5000/v1/api/posts/list_post_sub/CSUF/?amount=1
you are looking up the CSUF subreddit, and filtering it by the amount of 1
