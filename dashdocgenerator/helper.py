""" dashdoc generator helper classes and functions """


def is_sequence(arg):
    """ check type is list or other iterable """
    return (
        not hasattr(arg, "strip")
        and hasattr(arg, "__getitem__")
        or hasattr(arg, "__iter__"))


class AwesomeDict(dict):

    """ self referencing dictionary """

    def __getitem__(self, item):
        """ get item """
        return dict.__getitem__(self, item) % self
