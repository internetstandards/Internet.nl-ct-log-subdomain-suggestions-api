# Internet.nl Certificate Transparency Log Subdomain Suggestions

## What does this do / Intended use case
The goal is to replace subdomain suggestions from crt.sh with higher uptime and faster response times. This way it can
be used in other applications, such as the internet.nl dashboard, to suggest possible subdomains to end users.

## How does it work
This tool ingests subdomains from public certificate transparency logs using a connection from a certstream server. A
web interface allows for querying the stored data, which results in a list of known subdomains.

There are several key-optimizations performed that reduce the amount of subdomains stored in the database. The most
important one is the list of allowed tlds that are being stored. By default only domains relevant to the Kingdom of
the Netherlands are being stored.

## What are the limits of this tool
The limits have not yet been discovered and no optimizations have been performed yet, aside from a few proactive
database indexes. It is expected to being able to store about a years worth of data from the .nl zone. This means
about 5 million domains with an estimated 50 million subdomains, each which will have a new certificate every 90 days.
In total about 200 million records per year. This is the same in most EU countries. There is no expectation that this
tool will work quickly on the combined com/net/org zones. Although some partitioning and smarter inserting might just
do the trick. For the Netherlands the total number of certificate renewals seems to be much lower for subdomains,
between 0.5 to 2 per second.

The goal is to being able to run this on medium sized virtual machines with just a few cores and a few gigabytes of
ram. That should be enough for the Netherlands and most EU countries. We've not tried to see if this solution is 'web
scale'.

## How to ingest data from cerstream
Configure `CTLSSA_CERTSTREAM_SERVER_URL` to point to a certstream-server instance. The default points to a certstream
server hosted by the creator of certstream, calidog. This is great for testing and development, but don't use it for
production purposes.

Read more about setting up a certstream server here: https://github.com/CaliDog/certstream-server

After configuration run the following command:
```python manage.py migrate```
```python manage.py ingest```

This command should run forever. In case your certstream server is down it will patiently wait until the server is up.

## How to query the results
The webserver can be started with the command:
```python manage.py runserver```

When you visit the web interface at http://localhost:8000/ you will see a blank JSON response. Use the following
parameters to retrieve data: `http://localhost:8000/?domain=example&suffix=nl&period=365`


## Further configuration options
Configuration is done via environment variables, but can also be hardcoded in the settings.py file if need be.

Everything is configured with environment variables and fallbacks. Environment variables of the app are prefixed with
CTLSSA_, so they stand out in your `env`.

CTLSSA_ACCEPTED_TLDS: Comma separted string with the zones you want subdomains from.
The default is set to "nl,aw,cw,sr,sx,bq,frl,amsterdam,politie". Mileage will vary with .com, .net, .org zones and
we expect ingestion not to be fast enough.

DEQUE_LENGTH: Configure this to be around the amount of domains you ingest in a few hours to a day, but in a way that
it doesn't hit the database limit. This value is used to deduplicate certificate renewal requests. It's very common to
see certificate renewals containing the same domain for every subdomain. It's also very common to see the same request
happening over and over again because the administrator made some configuration mistake and needs to repeat the process.
The default is 100.000 domains.

There are various database settings so any django-supported database can be used. We recommend postgres as it has more
options regarding optimization than mysql. Either should be fine. Sqlite might also work, as there is only one process
that writes to the database.

Database settings:

- CTLSSA_DB_ENGINE
- CTLSSA_DB_NAME
- CTLSSA_DB_USER
- CTLSSA_DB_PASSWORD
- CTLSSA_DB_HOST
- CTLSSA_DJANGO_DATABASE


## Expectations in database size and performance

This package assumes that insertions in the database are faster than the amount of newly found domains. This will not
hold true for every zone, especially when combining .com, .net and .org.

Once this assumption doesn't hold optimizations are needed. There are several options that might help: bulk insert,
parallel inserts from multiple processes, database partitioning, index ordering, reducing the amount of indexes by
merging domain+suffix and so on. Other solutions might work as well. None of these have been tried yet, but you might
need them. If you do, please get in touch with the repository owner so this project can be optimized for everyone.


## Development
This project does not have a managed virtual environment yet. This might be added in the future if need be.

### Linting
Run these commands before checking in. These should all pass without error.
```
isort .
black .
pytest
```

### Dependency management
Run these commands to create a dependency hierarchy
```
pip-compile requirements.in --output-file=requirements.txt
pip-compile requirements-dev.in --output-file=requirements-dev.txt
```
