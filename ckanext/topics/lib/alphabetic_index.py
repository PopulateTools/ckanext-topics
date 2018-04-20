import string


class IndexOutOfBoundsError(Exception):

    def __init__(self, message):
        self.message = message


class AlphabeticIndex(object):

    ALPHABET = string.lowercase

    @classmethod
    def first_letter(cls):
        return cls.ALPHABET[0]

    @classmethod
    def next_letter(cls, index_letter):
        if (index_letter == 'z'):
            raise IndexOutOfBoundsError("Attempted to get next letter for 'z' value")

        current_alphabet_position = cls.ALPHABET.index(index_letter)

        return cls.ALPHABET[current_alphabet_position + 1]

    @classmethod
    def previous_letter(cls, index_letter):
        if (index_letter == 'a'):
            raise IndexOutOfBoundsError("Attempted to get previous letter for 'a' value")

        current_alphabet_position = cls.ALPHABET.index(index_letter)

        return cls.ALPHABET[current_alphabet_position - 1]

    @classmethod
    def max_items(cls):
        return len(cls.ALPHABET)
