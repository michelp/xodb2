import xapian


unset = object()


class Element(object):
    name = None
    store = False
    index = True
    required = False
    prefix = None
    slot = None

    def __init__(self, value, **attrs):
        self.value = value
        self.__dict__.update(attrs)

    def set_name(self, name):
        self.name = name

    def __getstate__(self):
        state = self.__dict__.copy()
        if not self.store:
            del state['value']
        return state

    def __setstate__(self, state):
        if 'value' not in state:
            state['value'] = unset
        self.__dict__.update(state)


class Term(Element):
    boolean = False

    def __call__(self, document, db):
        doc = document.__document__
        backend = db.backend

        if self.required and self.value is unset:
            raise TypeError('%s required' % self.name)

        if self.value is not None:
            prefix = self.name
            if self.prefix is not None:
                prefix = self.prefix
            if prefix:
                term = '%s:%s' % (prefix, self.value.encode("utf-8"))
            else:
                term = self.value

            if len(term) > 245:
                term = term[:244]

            if self.index:
                if self.boolean:
                    doc.add_boolean_term(term)
                else:
                    doc.add_term(term)

            if self.slot is not None:
                doc.add_value(self.slot, self.value)


class Text(Element):
    prefix = None
    language = 'en'

    def __call__(self, document, db):
        if self.index and self.value is not unset:
            doc = document.__document__
            backend = db.backend
            tg = xapian.TermGenerator()
            tg.set_database(backend)
            tg.set_document(doc)
            tg.set_stemmer(xapian.Stem(self.language))

            prefix = self.name
            if self.prefix is not None:
                prefix = self.prefix
            if prefix:
                tg.index_text(self.value, 1, '%s:' % prefix)
            else:
                tg.index_text(self.value, 1)


class List(Element):
    text = False
    language = 'en'

    def __call__(self, document, db):
        doc = document.__document__
        backend = db.backend

        if self.required and not self.value:
            raise TypeError('%s required' % self.name)

        if self.index and self.value is not unset:
            if not self.text:
                prefix = self.name
                if self.prefix is not None:
                    prefix = self.prefix

                for item in self.value:
                    if prefix:
                        term = '%s:%s' % (prefix, item.encode('utf-8'))
                    else:
                        term = self.value

                    if len(term) > 245:
                        term = term[:244]

                    doc.add_term(term)
            else:
                for item in self.value:
                    tg = xapian.TermGenerator()
                    tg.set_database(backend)
                    tg.set_document(doc)
                    tg.set_stemmer(xapian.Stem(self.language))

                    prefix = self.name
                    if self.prefix is not None:
                        prefix = self.prefix
                    if prefix:
                        tg.index_text(item, 1, '%s:' % prefix)
                    else:
                        tg.index_text(item, 1)
                
