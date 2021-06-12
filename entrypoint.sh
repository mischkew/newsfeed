#! /bin/sh

if [ -z "${FEED_MAIL_SEND_TO}" ]; then
  echo "Environment variable FEED_MAIL_SEND_TO not set!"
  exit 1
elif [ -z "${FEED_MAIL_USER}" ]; then
  echo "Environment variable FEED_MAIL_USER not set!"
  exit 1
elif [ -z "${FEED_MAIL_PASSWORD}" ]; then
  echo "Environment variable FEED_MAIL_PASSWORD not set!"
  exit 1
else
  python /app/my-feeds.py \
    --verbose \
    --cache-dir /data \
    sync \
    --report-errors \
    --send-to ${FEED_MAIL_SEND_TO}
fi
