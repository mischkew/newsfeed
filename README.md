# Feed - Personal Email News Feed

Scrape webpages for defined patterns and send an email once a day when changes
are connected.

## Installation

`pip install -e .`

If you need the VScode remote debugger for `feed --debugger` than use `pip install -e ".[dev]"`

## Usage

```
usage: feed [-h] [--debugger] [--cache-dir CACHE_DIR] [-v] [--version]
            {sync,list,clean} ...

Send emails for updates on personalized news feeds.

optional arguments:
  -h, --help            show this help message and exit
  --debugger            Enable debugging via VSCode
  --cache-dir CACHE_DIR
                        The path to store cache files in. Must exist. Can also
                        be provided via the FEED_CACHE_DIR environment
                        variable.
  -v, --verbose         Log debug output to console.
  --version             Print the version number.

Subcommands:
  {sync,list,clean}

You may customize the following environment variables: FEED_CACHE_DIR: The
path were diff files for each newsfeed should be stored.
```

We recommend to setup a cronjob or launchd service to continously automatically sync your feeds.
