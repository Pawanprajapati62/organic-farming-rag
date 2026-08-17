def format_pages(page_list):

    return ", ".join(
        f"Page {page}"
        for page in page_list
    )


def divider():

    print("-" * 80)