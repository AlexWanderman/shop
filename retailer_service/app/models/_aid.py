from random import choices
from string import ascii_letters, digits


class Aid:
    ''' Sort of *generate-me-aid* mixin. Has only static method
        generate_key(length).
    '''
    @staticmethod
    def generate_key(length: int) -> str:
        '''Return str of ascii_letters + digits, len = length.'''
        alphabet = ascii_letters + digits
        return ''.join(choices(alphabet, k=length))
