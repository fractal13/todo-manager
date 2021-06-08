#!/usr/bin/env python3

import sys
import gkeepapi
import todo_manager
import re

gkeepapi.node.DEBUG = True

def main(argv):
    keep = todo_manager.login(argv[1])
    keep.sync()
    note = todo_manager.getTodoNote(keep)
    print(note.title)

    text = todo_manager.sortByParagraph(note.text)
    print(text)
    #note.text = text
    #keep.sync()
    return

if __name__ == "__main__":
    main(sys.argv)
