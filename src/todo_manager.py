#!/usr/bin/env python3

import logging
import sys
import gkeepapi
import keyring
import getpass
import re

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
        except gkeepapi.exception.LoginException as error:
            logger.info(error)

    # Abort if authentication failed
    if not logged_in:
        logger.error("Failed to authenticate")
        sys.exit(1)

    return keep

def getTodoNote(keep, query="TODO Managed"):
    notes = list(keep.find(query=query))
    if len(notes) == 1:
        note = notes[0]
    elif len(notes) > 1:
        note = None
        raise Exception("Too many notes match query: '" + str(query) + "'")
    else:
        note = None
        raise Exception("No notes match query: '" + str(query) + "'")
    return note

def sortByParagraph(text):
    lines = text.split("\n")
    sorted_lines = []
    current_line = ""
    for line in lines:
        if len(current_line) > 0:
            current_line += "\n"
        current_line += line
        if re.match('^[ \t]*$', line):
            sorted_lines.append(current_line)
            current_line = ""
            
    if len(current_line) > 0:
        sorted_lines.append(current_line)
        current_line = ""

    sorted_lines = sorted(sorted_lines)
    sorted_text = "\n".join(sorted_lines)
    return sorted_text
