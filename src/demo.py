#!/usr/bin/env python3

import sys
import logging
import gkeepapi
import keyring
import getpass

gkeepapi.node.DEBUG = True

def login(username):

    # Set up logging
    logger = logging.getLogger("gkeepapi")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Initialize the client
    keep = gkeepapi.Keep()

    token = keyring.get_password("google-keep-token", username)
    logged_in = False

    # Use an existing master token if one exists
    if token:
        logger.info("Authenticating with token")
        try:
            keep.resume(username, token, sync=False)
            logged_in = True
            logger.info("Success")
        except gkeepapi.exception.LoginException:
            logger.info("Invalid token")

    # Otherwise, prompt for credentials and login
    if not logged_in:
        password = getpass.getpass()
        try:
            keep.login(username, password, sync=False)
            logged_in = True
            del password
            token = keep.getMasterToken()
            keyring.set_password("google-keep-token", username, token)
            logger.info("Success")
        except gkeepapi.exception.LoginException as e:
            logger.info(e)

    # Abort if authentication failed
    if not logged_in:
        logger.error("Failed to authenticate")
        sys.exit(1)

    return keep


def main(argv):
    keep = login(argv[1])
    keep.sync()
    notes = keep.find(query='TODO Managed')
    for note in notes:
        print(note.title)
        print(note.text)
        print(note.color)
    return

if __name__ == "__main__":
    main(sys.argv)
    
