from django import template

register = template.Library()


@register.filter
def extract_dict(dicio, key):
    """Método de uso no template, em que a tag retorna o valor do dicionário
        correspondente à chave passada como parâmetro.

    Args:
        dicio (Dict): Dict
        key (Str): Dict key

    Returns:
        Any: Qualquer tipo que seja value em um dicionário.
    """
    return key

# @register.filter(name='err_msg_classes')
# def err_msg_classes(value, arg):
#     return value.split(' ')[arg]
