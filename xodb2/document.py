from cPickle import loads, dumps
import json
import xapian

from elements import Element


class Document(object):

    _slot_cache = dict()

    def __init__(self, match=None):
        if match is None:
            document = xapian.Document()
        else:
            document = match.document
        self.__document__ = document
        self.__match__ = match
        self.__schema__ = None

    def __load__(self):
        if self.__schema__ is None:
            data = self.__document__.get_data()
            if not data:
                self.__schema__ = {}
            else:
                self.__schema__ = loads(data)

    def __save__(self, db):
        for e in self.__schema__.values():
            e(self, db)
        self.__document__.set_data(dumps(self.__schema__))
        return self.__document__

    def __setattr__(self, name, element):
        if name.startswith('__'):
            return super(Document, self).__setattr__(name, element)
        if not isinstance(element, Element):
            raise TypeError('can only set elements')
        element.set_name(name)
        self.__load__()
        self.__schema__[name] = element

    def __getattribute__(self, name):
        if name.startswith('__'):
            return super(Document, self).__getattribute__(name)
        sc = type(self).__slot_cache__
        if name in sc:
            return self.__document__.get_value(sc[name])
        self.__load__()
        if name not in self.__schema__:
            raise AttributeError(name)
        element = self.__schema__[name]
        if element.store:
            return element.value
        elif element.slot is not None:
            slot_val = self.__document__.get_value(element.slot)
            sc[name] = slot_val
            return slot_val

    def __getitem__(self, index):
        return self.__document__.get_value(index)

    def __repr__(self):
        self.__load__()
        return '<Document %s>' % `self.__schema__`

