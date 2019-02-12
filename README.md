#SNCF invoices scrapper from http://oui.sncf 

Project that retrieve incoices from sncf each time a script is ran. it allows to not think to manually read emails and download files

It stores downloaded invoices to a target folder. already downloaded invoices are downloaded once only. Only the 1st page of invoice is scrapped, so run the script quite often.

Edit a .env file that looks like : 
```bash
EMAIL=my@email.com
PASS=oui.sncf-web-password
```

Create the docker container

```bash
docker build . -t sncf:1.0.0
```

Run the process in cron for exemple

```
0 0 * * 0 docker run -v /path/to/store:/app/data sncf:1.0.0 pipenv run python main.py
```
