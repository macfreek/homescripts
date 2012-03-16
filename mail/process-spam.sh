#!/bin/bash

HOME=/home/freek
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/home/freek/bin
LC_ALL=C

extract-spam.php >> $HOME/log/spam.log
sa-learn --spam $HOME/Maildir/.Spam.negatives/cur/        >> $HOME/log/spam.log
sa-learn --spam $HOME/Maildir/.Spam.falsenegatives/cur/   >> $HOME/log/spam.log
sa-learn --ham $HOME/Maildir/.Spam.falsepositives/cur/    >> $HOME/log/spam.log
sa-learn --ham $HOME/Maildir/.Hobbies.victory/cur/        >> $HOME/log/spam.log

# sa-learn --ham  $HOME/Maildir/cur                       >> $HOME/log/spam.log
# rm -f $HOME/Maildir/.Spam.negatives/cur/*
