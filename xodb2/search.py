from operator import attrgetter
from itertools import imap
import xapian
from xapian import Query, Stem


def phrase(terms, prefix=None, language=None, window=3):
    if isinstance(terms, basestring):
        terms = terms.split()
    if prefix:
        terms = ['%s:%s' % (prefix, t) for t in terms]
    if language:
        stem = xapian.Stem(language)
        terms = ['Z%s' % stem(t) for t in terms]
    print terms
    return Query(Query.OP_PHRASE, terms, window)

def near(terms, prefix=None, window=10):
    if isinstance(terms, basestring):
        terms = terms.split()
    if prefix:
        terms = ['%s:%s' % (prefix, t) for t in terms]
    return Query(Query.OP_NEAR, terms, window)

def elite(terms, prefix=None, window=10):
    if isinstance(terms, basestring):
        terms = terms.split()
    if prefix:
        terms = ['%s:%s' % (prefix, t) for t in terms]
    return Query(Query.OP_ELITE_SET, terms, window)


class Search(object):

    def __init__(self, db, query='',
                 language=None, limit=0, offset=0,
                 order=None, reverse=False):

        self.query = self.to_query(query)

        self._db = db
        self._language = language
        self._limit = limit
        self._offset = offset
        self._order = order
        self._reverse = reverse

    def to_query(self, query, default_op=Query.OP_AND):
        if isinstance(query, list):
            return Query(default_op, [self.to_query(q) for q in query])
        elif isinstance(query, basestring):
            return Query(query)
        elif isinstance(query, Query):
            return query

    def copy(self, **kwargs):
        args = dict(query=self.query,
                    language=self._language,
                    limit=self._limit,
                    offset=self._offset,
                    order=self._order,
                    reverse=self._reverse)
        if kwargs:
            args.update(kwargs)
        return type(self)(self._db, **args)

    def operator(self, query, op):
        """Wrap self with an operator and another query.
        """
        query = querify(query)
        return self.copy(query=Query(op, self.query, query))

    def filter(self, query):
        return self.operator(query, Query.OP_FILTER)

    def and_(self, query):
        return self.operator(query, Query.OP_AND)

    def or_(self, query):
        return self.operator(query, Query.OP_OR)

    def and_not(self, query):
        return self.operator(query, Query.OP_AND_NOT)

    def xor(self, query):
        return self.operator(query, Query.OP_XOR)

    def and_maybe(self, query):
        return self.operator(query, Query.OP_AND_MAYBE)

    def and_elite(self, queries):
        return self.and_(Query(Query.OP_ELITE_SET, queries))

    def or_elite(self, *queries):
        return self.or_(Query(Query.OP_ELITE_SET, queries))

    def scale(self, factor):
        return self.copy(query=Query(Query.OP_SCALE_WEIGHT, self.query, factor))

    def expand(self, prefix=None, limit=10, mlimit=100):
        candidates = self.suggest(prefix, limit, mlimit)
        return self.or_(candidates)

    def limit(self, limit):
        return self.copy(limit=limit)
        
    def offset(self, offset):
        return self.copy(offset=offset)

    def language(self, language):
        return self.copy(language=language)

    def order(self, order):
        return self.copy(order=order)

    def reverse(self, reverse):
        return self.copy(reverse=reverse)

    def count(self):
        return self._db.count(self)

    def estimate(self):
        return self._db.count(self, estimate=True)

    def suggest(self, mlimit=64, moffset=0, prefix=None):
        for r in self._db.suggest(
            self, limit=self._limit, mlimit=mlimit, moffset=moffset,
            prefix=prefix,
            order=self._order, reverse=self._reverse, offset=self._offset):
            yield r

    def __iter__(self):
        """Generator over xapian results.
        """
        for r in self._db.query(
            self, limit=self._limit, language=self._language,
            order=self._order, reverse=self._reverse, offset=self._offset):
            yield r

    def __repr__(self):
        return str(self.query)
