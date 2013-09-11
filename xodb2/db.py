import string
import xapian
from document import Document


class PrefixDecider(xapian.ExpandDecider):
    """Expand decider to only match terms that begin with a prefix."""

    __slots__ = ['prefix']

    def __init__(self, prefix):
        super(PrefixDecider, self).__init__()
        self.prefix = prefix

    def __call__(self, term):
        return term.startswith(self.prefix)



class LanguageDecider(xapian.ExpandDecider):
    min_length = 5
    nostart = unicode(string.uppercase + string.digits)

    def __call__(self, term):
        term = term.decode("utf-8")
        if (term[0] in self.nostart or len(term) < self.min_length):
            return False
        return True


class Database(object):

    @classmethod
    def from_backends(cls, *backends):
        self = cls()
        if len(backends) == 1:
            self.backend = backends[0]
        else:
            self.backend = xapian.Database()
            for b in backends:
                self.backend.add_database(b)
        return self

    def count(self, search=None, estimate=True):
        self.backend.reopen()
        if search is None:
            return self.backend.get_doccount()
        enq = xapian.Enquire(self.backend)
        enq.set_query(search.query)
        mset = self._build_mset(enq)
        if estimate:
            return mset.get_matches_estimated()
        return mset.size()

    def query(self, search,
              offset=0,
              limit=None,
              order=None,
              reverse=False,
              language=None,
              check=0,
              translit=None,
              match_decider=None,
              match_spy=None,
              document=False):

        self.backend.reopen()
        enq = xapian.Enquire(self.backend)
        enq.set_query(search.query)

        limit = limit or self.backend.get_doccount()

        mset = self._build_mset(enq, offset, limit, order, reverse,
                                check, match_decider, match_spy)
        for match in mset:
            yield Document(match)

    def suggest(self, search,
                offset=0,
                limit=0,
                moffset=0,
                mlimit=0,
                klimit=1.0,
                kmlimit=1.0,
                prefix=None,
                decider=None,
                score=False,
                format_term=True,
                collapse_stems=True,
                include_query_terms=True,
                order=None,
                reverse=False):
        """
        Suggest terms that would possibly yield more relevant results
        for the given query.
        """
        self.backend.reopen()
        if mlimit == 0:
            mlimit = int(self.backend.get_doccount() * kmlimit)

        enq = xapian.Enquire(self.backend)
        enq.set_query(search.query)
        mset = self._build_mset(enq, offset=moffset, limit=mlimit,
                                order=order, reverse=reverse)

        rset = xapian.RSet()
        for m in mset:
            rset.add_document(m.docid)

        if prefix is not None:
            decider = PrefixDecider(prefix)
        if decider is None:
            decider = LanguageDecider()

        if limit == 0:
            limit = int(self.backend.get_doccount() * klimit)

        eset = enq.get_eset(
            limit, rset,
            enq.INCLUDE_QUERY_TERMS if include_query_terms else 0,
            1.0, decider, -3)

        for item in eset.items:
            val = item[0].decode('utf8')
            yield (val, item[1])

    def _build_mset(self,
                    enq,
                    offset=0,
                    limit=None,
                    order=None,
                    reverse=False,
                    check=None,
                    match_decider=None,
                    match_spy=None,
                    ):
        if order is not None:
            enq.set_sort_by_value(order, reverse)

        if limit is None:
            limit = self.backend.get_doccount()

        if check is None:
            check = limit + 1

        return enq.get_mset(offset, limit, check, None, match_decider, match_spy)


class WritableDatabase(Database):

    def __init__(self, path, flags=xapian.DB_CREATE_OR_OPEN):
        self.backend = xapian.WritableDatabase(path, flags)

    def add(self, doc):
        self.backend.add_document(doc.__save__(self))
