# from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
# from django.conf import settings
# from django.utils.deprecation import MiddlewareMixin

# class RefreshTokenMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
#         refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])

#         if access_token and refresh_token:
#             try:
#                 # Check if the access token is valid
#                 AccessToken(access_token)
#             except Exception as e:
#                 try:
#                     # If the access token is expired, generate a new one using the refresh token
#                     refresh = RefreshToken(refresh_token)
#                     new_access_token = refresh.access_token
                    
#                     # Update the access token in the cookie
#                     request.COOKIES[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(new_access_token)
#                     request._new_access_token = new_access_token
#                 except Exception as refresh_error:
#                     # Handle cases where the refresh token is invalid/expired
#                     pass

#     def process_response(self, request, response):
#         # Check if a new access token was generated
#         if hasattr(request, '_new_access_token'):
#             response.set_cookie(
#                 key=settings.SIMPLE_JWT['AUTH_COOKIE'],
#                 value=request._new_access_token,
#                 expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
#                 secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#                 httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
#                 samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
#             )
#         return response
