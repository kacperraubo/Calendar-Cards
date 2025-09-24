from django.conf import settings


def generate_meta_tags(
    title,
    description,
    website_url,
    facebook_image_path=None,
    twitter_image_path=None,
    icon_href=None,
    image_alt=None,
):
    if image_alt is None:
        image_alt = "A logo of Services on a white background"

        icon_href = f"{settings.STATIC_URL}"

    if facebook_image_path is None:
        facebook_image_path = "/meta/meta_facebook.png"  # from static

    if twitter_image_path is None:
        twitter_image_path = "/meta/meta_twitter_summary.png"  # from static

    meta = f"""<title>{title}</title>
        <meta name="title" content="{title}">
        <meta name="description" content="{description}">

        <meta property="og:type" content="website">
        <meta property="og:url" content="{website_url}">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:image" content="{facebook_image_path}">

        <meta property="twitter:card" content="summary">
        <meta property="twitter:url" content="{website_url}">
        <meta property="twitter:title" content="{title}">
        <meta property="twitter:description" content="{description}">
        <meta property="twitter:image" content="{twitter_image_path}">
        <meta property="twitter:image:alt" content="{image_alt}">"""
    return meta
