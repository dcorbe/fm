import postmarkup

class postmarkup_wrapper():
    """ A wrapper around postmarkup 
    this ensures that the right options are always passed """

    def __init__(self):
        self.bbcode = postmarkup.create(annotate_links=False)

    def render(self, args):
        return self.bbcode(args)
