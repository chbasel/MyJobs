from django import template

register = template.Library()


@register.filter
def swap_http_with_https(url, arg=""):
    """
    swap http://<arg> with https://<arg>
    :param url: url to check/swap
    :param arg: additional argument string to increase specificity of match
    :return: url with https (if applicable)
    """
    return url.replace("http://" + arg, "https://" + arg)
