from pyramid.view import view_config


@view_config(route_name='home', renderer='tree_wallpaper_server:templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'tree_wallpaper_server'}
