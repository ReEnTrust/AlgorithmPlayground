from django import template

register = template.Library()

#This is used to access dictionary in the template
def key(d, key_name):
    return d[key_name]
key = register.filter('key', key)

def subtract(value, arg):
    return value - arg
subtract = register.filter('subtract', subtract)

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)