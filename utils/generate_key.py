''' Simple script that generates a secret key of specified length or 32
    symbols using python built-in module 'secrets'. Uses ascii_letters,
    digits, punctuation, except " and '.
'''

from secrets import choice
from string import ascii_letters, digits, punctuation
from sys import argv


def main():
    alphabet = ascii_letters + digits + punctuation
    n = int(argv[1]) if len(argv) > 1 else 32

    key = ''.join(choice(alphabet) for _ in range(n))
    key = key.replace('"', choice(ascii_letters + digits))
    key = key.replace("'", choice(ascii_letters + digits))

    print(key)


if __name__ == '__main__':
    main()
