from django.template.defaulttags import register

# Jinja trolling
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def tag_view(tag_name):
    # Replace _ with spaces
    return tag_name.replace('_', ' ')

@register.filter
def remove(string, to_remove):
    return string.replace(to_remove, '')

@register.filter
def concat(a, b):
    return str(a) + str(b)