# tools.py

def tool_search(query):
    from skatlaz_llms_prompt import search_bing
    return search_bing(query)


def tool_code(prompt):
    from skatlaz_llms_prompt import generate_code
    return generate_code(prompt)


def tool_image(prompt):
    from skatlaz_llms_prompt import generate_image
    return generate_image(prompt)


TOOLS = {
    "search": tool_search,
    "code": tool_code,
    "image": tool_image
}
