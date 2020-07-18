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

## Cronjob Configuration

We use cronjobs to sync the feeds on every reboot and once per day at 4pm. You can install the cronjobs via `crontab ./feed.crontab`.

Make sure that these environment variables are defined:

- `FEED_VIRTUALENV_PYTHON`: The path to the python binary of the virtualenv. If you don't use virtualenv, then this should simply be `python`.
- `FEED_MAIL_USER`: The email address to login to.
- `FEED_MAIL_PASSWORD`: The password for you mail account.

In our `.bashrc` this looks as follows:

```bash
export FEED_VIRTUALENV_PYTHON="$HOME/.pyenv/versions/feed/bin/python"
export FEED_MAIL_USER="<send-from-email>"
export FEED_MAIL_PASSWORD="$(cat $HOME/.feed.password)"
```

We recommend to never store the password in plain text in your `.bashrc` or cronjob files. You may acquire the password by reading a special config file. Also, don't avoid using your daily email account ;)
