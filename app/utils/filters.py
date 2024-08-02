from main import app

@app.template_filter()
def prev_page(current, pages):
    prev_page = None
    for page in pages:
        if page.category == current.category and page.weight < current.weight:
            prev_page = page
    return prev_page


@app.template_filter()
def next_page(current, pages):
    next_page = None
    for page in pages:
        if page.category == current.category and page.weight > current.weight:
            next_page = page
            break
    return next_page


JINJA_FILTERS = {'prev_page': prev_page, 'next_page':next_page}