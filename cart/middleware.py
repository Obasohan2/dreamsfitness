class PreserveCartMiddleware:
    """
    Store the current session cart before login, so it can be restored after login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Save guest cart before login view executes
        if request.path.startswith('/login') and 'cart' in request.session:
            request.session['pre_login_cart'] = request.session['cart']

        response = self.get_response(request)
        return response
