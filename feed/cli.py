import logging
import os
from argparse import ArgumentParser, Namespace
from getpass import getpass
from pathlib import Path

from .get_version import get_version

from .email import create_server, get_email_server, set_email_server
from .feed import get_cache_dir, set_cache_dir
from .registry import Registry


def enable_debugger(parser: ArgumentParser) -> bool:
    """Activates the VSCode debugger and waits for a remote connection."""
    try:
        import ptvsd
    except ImportError:
        parser.error(
            "Cannot import ptvsd package. Install the package in order to"
            " debug this application."
        )

    # 5678 is the default attach port in the VS Code debug configurations
    print("Waiting for debugger attach")
    ptvsd.enable_attach(address=("localhost", 5678), redirect_output=True)
    ptvsd.wait_for_attach()


#
# Subcommands
#


def sync_feeds(parser: ArgumentParser, args: Namespace, registry: Registry) -> None:
    if args.mail_server:
        set_email_server(args.mail_server)

    mail_user = args.mail_user if args.mail_user else os.environ.get("FEED_MAIL_USER")
    if not mail_user:
        parser.error(
            "An email user is not provided. Use --mail-user or define FEED_MAIL_USER."
        )
    mail_password = os.environ.get("FEED_MAIL_PASSWORD")

    # when --mail-user is provided, the password must always be entered from CLI
    if args.mail_user:
        mail_password = getpass(prompt=f"Password for {mail_user}: ")

    if not mail_password:
        parser.error(
            "An email password is not provided. Use --mail-user and enter a"
            " password in the terminal or define FEED_MAIL_PASSWORD."
        )

    feeds = (
        registry.get_feeds_from_ids(args.feeds) if args.feeds else registry.get_feeds()
    )
    server = create_server(get_email_server(), mail_user, mail_password)
    recepient = args.send_to if args.send_to else mail_user

    if args.dry_run:
        print("Dry-Run: Not updating cache and sending emails.")

    for index, feed in enumerate(feeds):
        print(f"Syncing {feed.title} ({index+1}/{len(feeds)})")
        mailer = feed.sync(differ_on_create=args.initial_send, dry_run=args.dry_run)
        mailer(
            smtp_server=server,
            recepient_email=recepient,
            force_send=args.force_send,
            dry_run=args.dry_run,
        )


def list_feeds(parser: ArgumentParser, args: Namespace, registry: Registry) -> None:
    print("Available Feeds:\n")
    for feed in registry.get_feeds():
        print("  ", end="")
        if not feed.path.is_file():
            print("! ", end="")
        else:
            print("  ", end="")
        print(f"{feed.title} (Id: {feed.id})", end="")
        if not feed.path.is_file():
            print(" -- not visited yet")
        else:
            print()


def clean_feeds(parser: ArgumentParser, args: Namespace) -> None:
    if args.dry_run:
        print("Dry-Run: Not deleting files.")

    cache_files = sorted(get_cache_dir().iterdir())
    for cache_file in cache_files:
        if args.dry_run:
            logging.debug(f"Would delete {cache_file}")
        else:
            cache_file.unlink()
    print(f"Deleted {len(cache_files)} cached files.")


#
# Main Command
#


def program(registry: Registry) -> None:
    parser = ArgumentParser(
        description="Send emails for updates on personalized news feeds.",
        epilog="""You may customize the following environment variables:

FEED_CACHE_DIR: The path were diff files for each newsfeed should be stored.
        """,
    )

    subparsers = parser.add_subparsers(title="Subcommands", dest="command")

    parser.add_argument(
        "--debugger", action="store_true", help="Enable debugging via VSCode"
    )
    parser.add_argument(
        "--cache-dir",
        help=(
            "The path to store cache files in. Must exist. Can also be"
            " provided via the FEED_CACHE_DIR environment variable."
        ),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Log debug output to console."
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version number."
    )

    sync_p = subparsers.add_parser(
        "sync",
        description="Fetch feed webpages and send update emails.",
        epilog="""You may customize the following environment variables:

FEED_MAIL_SERVER: The email server to use for sending updates, i.e smtp.gmail.com.
FEED_MAIL_USER: The email address/ username for the mail account.
FEED_MAIL_PASSWORD: The password for the mail account.""",
    )
    sync_p.set_defaults(func=sync_feeds)
    sync_p.add_argument(
        "--mail-server",
        help=(
            "The email server to use for sending updates, i.e. smtp.gmail.com."
            " Can also be set via the FEED_MAIL_SERVER environment variable."
        ),
    )
    sync_p.add_argument(
        "--mail-user",
        help=(
            "The email address/ username to use for login. If provided, the"
            " password must be entered via command line. Otherwise the username"
            " and password can be set via the FEED_MAIL_USER and"
            " FEED_MAIL_PASSWORD environment variables."
        ),
    )
    sync_p.add_argument(
        "-t",
        "--send-to",
        help=(
            "Send the updates to this email address. Defaults to sending to"
            " the sender itself, see --mail-user"
        ),
    )
    sync_p.add_argument(
        "--no-initial-send",
        dest="initial_send",
        action="store_false",
        help="Don't send emails when the webpage is crawled for the first time.",
    )
    sync_p.add_argument(
        "-f",
        "--force-send",
        action="store_true",
        help=(
            "Always send an email, even if the feed did not update. Useful for"
            " debugging purposes."
        ),
    )
    sync_p.add_argument(
        "--dry-run", action="store_true", help="Don't actually do anything."
    )
    sync_p.add_argument(
        "--feeds",
        nargs="+",
        choices=[feed.id for feed in registry.get_feeds()],
        help="Choose the feeds to update. Will update all feeds if none given.",
    )

    list_p = subparsers.add_parser("list", description="List available news feeds")
    list_p.set_defaults(func=list_feeds)

    clean_p = subparsers.add_parser("clean", description="Clear the cache directory")
    clean_p.set_defaults(func=clean_feeds)
    clean_p.add_argument(
        "--dry-run", action="store_true", help="Don't actually do anything."
    )

    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if args.debugger:
        enable_debugger(parser)

    if args.version:
        print(get_version())
        return

    if args.cache_dir:
        try:
            set_cache_dir(Path(args.cache_dir))
        except FileNotFoundError as error:
            parser.error(error)

    cache_dir = get_cache_dir()
    cache_dir.mkdir(exist_ok=True)

    if not hasattr(args, "func"):
        parser.error("Please choose a subcommand.")

    # run the chosen command
    args.func(parser, args, registry)
