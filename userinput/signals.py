from django.dispatch import Signal

pre_page_move = Signal(providing_args=['instance', 'parent_page_before', 'parent_page_after', 'url_path_before', 'url_path_after'])
post_page_move = Signal(providing_args=['instance', 'parent_page_before', 'parent_page_after', 'url_path_before', 'url_path_after'])
