from django import template
register = template.Library()


@register.inclusion_tag('rdf/tags/_deepzoom_js.html')
def deepzoom_js(
        deepzoom_count=0,
        deepzoom_urls=None,
        show_navigator=False,
        navigator_position="TOP_LEFT",
        toolbar_id="zoom_navigation",
        viewer_id="zoom_viewer"):
    """
    get zoom url count and values
    :return: count as integer and urls as array
    """

    return {
        'deepzoom_count': deepzoom_count,
        'deepzoom_urls': deepzoom_urls,
        'show_navigator': show_navigator,
        'navigator_position': navigator_position,
        'toolbar_id': toolbar_id,
        'viewer_id': viewer_id,
    }


@register.inclusion_tag('rdf/tags/_deepzoom_viewer.html')
def deepzoom_viewer(
        viewer_id="zoom_viewer",
        viewer_class="embed-responsive-item"):
    """
    get zoom url count and values
    :return: count as integer and urls as array
    """
    return {
        'viewer_id': viewer_id,
        'viewer_class': viewer_class,
    }