Chrome Webstore
---------------
https://chrome.google.com/webstore/detail/omniwheel/onhiamlhcgbbjbdnefeclnmnmafgoebk

Hackathon submission
---------------------
http://devpost.com/software/jira-assistant

For development environment
----------------------------
* Install ngrok
* run -> ngrok http 80
* Keep forwarded url handy

Put Wit.api token in state.config.py
Put Webhook listener url in apis.config. Keep the placeholder for webhook id (e.g http://example.com/webhook/{})
Change client connection url in plugin.services.SocketService.js

Generating RSA for OAuth
------------------------
* openssl genrsa -out jira.pem 1024
* openssl rsa -in jira.pem -pubout -out jira.pub

Save jira.pub in home directory

