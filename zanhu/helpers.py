from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.views.generic.base import View


def ajax_required(f):
    """check if it is ajax request"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("不是Ajax请求")
        return f(request, *args, **kwargs)

    return wrap


class AuthorRequiredMixin(View):
    """
    check if a user is the original author, used for news deletion and article edit
    """
    def dispatch(self, request, *args, **kwargs):
        # news and article instances have user attribute
        if self.get_object().user.username != request.user.username:
            raise PermissionDenied

        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
