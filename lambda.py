#!/usr/bin/python3

#################################################
# Main file for the lambda calculus interpretor #
#################################################

import sys
import token







def main(instream):
    try:
        while True:
            print("=> ", end='', flush=True)
            data = token.parse(instream)
            if data is not None:
                print(data)
    except KeyboardInterrupt:
        print()
        return

if __name__ == "__main__":
    main(sys.stdin)

