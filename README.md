# Feed - Personal Email News Feed

Scrape webpages for defined patterns and send an email once a day when changes
are connected. I use this to keep track of blogs and other content.

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

## Adding new Feeds

Currently, all feeds are implemented as part of this application. There is currently no way other than altering this code base, see [feeds.py](./feed/feeds.py).

A Feed bascially consists of a weblink, a title, a parser to identify relevant information which will observed for change, and a factory method to produce an email body which is sent to your target email, whenever new content is available.

## Daily Updates

We recommend to setup a cronjob or launchd service to continously automatically sync your feeds, see [this](feed.template.plist) launchd template for example.
