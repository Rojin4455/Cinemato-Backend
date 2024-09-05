from django.urls import path
from .views import RequestOTPView,VerifyOTPView,ResendOtpView,GoogleLoginApi,ConfirmGoogleLogin,SetTokenInCookie,UserProfile,Test
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOtpView.as_view(), name='verify-otp'),
    path("auth/api/login/google/", GoogleLoginApi.as_view(), name="login-with-google"),
    path("confirm-google-login/",ConfirmGoogleLogin.as_view(), name="confirm-google-login"),
    path("set-token/",SetTokenInCookie.as_view(), name="set-token"),
    path("user-profile/",UserProfile.as_view(), name="user-profile"),
    path("test/",Test.as_view(), name="test"),
    
]   