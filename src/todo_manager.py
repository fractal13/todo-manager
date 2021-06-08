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

def parseIntoParagraphs(text):
    lines = text.split("\n")
    paragraphs = []
    current_paragraph = ""
    for line in lines:
        if len(current_paragraph) > 0:
            current_paragraph += "\n"
        current_paragraph += line
        if re.match('^[ \t]*$', line):
            paragraphs.append(current_paragraph)
            current_paragraph = ""
            
    if len(current_paragraph) > 0:
        paragraphs.append(current_paragraph)
        current_paragraph = ""

    return paragraphs

def sort_key(text):
    default_key = 100.0
    first_line = text.split("\n")[0]
    match = re.match("^.*(@([^#]*))?(#([^ ]*))?.*$", first_line)
    match = re.match("^.*(@([^#]*))(#([.]+))?(.*)$", first_line)
    if match:
        priority = match.group(4)
        if priority is not None:
            try:
                key = float(priority)
            except ValueError:
                key = default_key
                print("----> using default_key:", first_line)
        else:
            key = default_key
            print("---> using default_key:", first_line)
            print(match.group(1))
            print(match.group(2))
            print(match.group(3))
            print(match.group(4))
            print(match.group(5))
                
    else:
        print("--> using default_key:", first_line)
        key = default_key
    return key

def sortByParagraph(text):
    paragraphs = parseIntoParagraphs(text)
    sorted_paragraphs = sorted(paragraphs, key=sort_key)
    sorted_text = "\n".join(sorted_paragraphs)
    return sorted_text

