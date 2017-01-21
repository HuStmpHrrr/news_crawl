def relates_to(article, predicate):
    """
    predicate takes a string and return a boolean

    this function judges if an article is nontrivially related to the predicate

    we only check title and high lights. if such predicate can't pass these two elemens,
    then the topic probably is not very related to the predicate
    """
    return predicate(article.title) \
        or article.highlights is not None \
        and any(predicate(i) for i in article.highlights.items)
