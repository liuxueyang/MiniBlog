#!/usr/bin/fish

#proxychains4 heroku config:set MAIL_USERNAME=$MAIL_USERNAME
#proxychains4 heroku config:set MINIBLOG_ADMIN=$MAIL_USERNAME
#proxychains4 heroku config:set MAIL_PASSWORD=$MAIL_PASSWORD

proxychains4 git push heroku master
#proxychains4 heroku run python manage.py reset_db

proxychains4 heroku restart