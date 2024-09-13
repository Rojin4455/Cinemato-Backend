# cookieapp/views.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from twilio.rest import Client
import cinemato.settings as project_settings
import urllib.parse
from rest_framework import permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RequestOTPSerializer,VerifyOTPSerializer, EditProfileSerializer
from .models import User, OTP, UserProfile as UserImage
from django.core.mail import send_mail
from .services import get_user_data
from django.shortcuts import redirect
from django.conf import settings
from .serializers import AuthSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token),
    }
        

class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("request otp: cookie:   ", request.session.session_key)
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.create_otp(serializer.validated_data)

            # Send OTP via email or SMS based on the provided data
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')

            if email:   
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp_code}. It will expire in 20 seconds.',
                    project_settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
            elif phone:
                client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                message = client.messages.create(
                    body=f'Your OTP is: {otp_code}',
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=f'{settings.COUNTRY_CODE}{phone}'
                )
            print("success")
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        print("Received Data:", request.data)
        print("cookie:   ", request.session.session_key)
        
        if serializer.is_valid():
            print("Serializer is valid")
            user = serializer.create_user(serializer.validated_data)
            
            if user is not None:
                if user.is_active:
                    
                    
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    refresh = str(refresh)

                    response = Response()
                    print("access token in verify otp: ",access)
                    
                    user.status = True
                    response.data = {"Success": "Login successfully", "token": {"access":access,"refresh":refresh},'requestData':{"username":user.first_name,"email":user.email,"phone":user.phone}}
                    return response
                else:
                    return Response({"No active": "This account is not active!"}, status=status.HTTP_404_NOT_FOUND)
            else:
                print("User creation failed")
        else:
            print("Serializer errors:", serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ResendOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
            serializer = RequestOTPSerializer(data=request.data)
            if serializer.is_valid():
                otp_code = serializer.create_otp(serializer.validated_data)

                # Send OTP via email or SMS based on the provided data
                email = serializer.validated_data.get('email')
                phone = serializer.validated_data.get('phone')

                if email:
                    send_mail(
                        'Cinemato - Your OTP Code',
                        f'Your OTP code is {otp_code}',
                        project_settings.DEFAULT_FROM_EMAIL,
                        [email],
                    )
                elif phone:
                    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                    message = client.messages.create(
                        body=f'Your OTP is: {otp_code}',
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=f'{settings.COUNTRY_CODE}{phone}'
                    )
                print("success")
                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmGoogleLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_data, *args, **kwargs):
        try:
            user = User.objects.get(email=user_data['email'])
            if user.is_active:
                return Response({"user_id": user.id}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "This account is not active!"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)



# views that handle 'localhost://8000/auth/api/login/google/'
class GoogleLoginApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)

        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)

        if 'email' in user_data:
            mock_request = request._request
            confirm_view = ConfirmGoogleLogin.as_view()

            response = confirm_view(mock_request, user_data=user_data)

            if response.status_code == status.HTTP_200_OK:
                user_id = response.data.get('user_id')
                user = User.objects.get(id=user_id)
                

                custom_data = {
                    'user_id': user.id,
                    'email': user.email
                }


                query_string = urllib.parse.urlencode(custom_data)
                print("_________________________________________________________________")

                print(f'Redirect URL: {settings.BASE_APP_URL}/?{query_string}')
                return redirect(f'{settings.BASE_APP_URL}/?data={query_string}')
            else:
                return response

        return Response({"Error": "Email is not in the user data object"}, status=status.HTTP_404_NOT_FOUND)
        


class SetToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = User.objects.get(id = request.data['user_id'])
        # data = get_tokens_for_user(user)
        response = Response(status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh = str(refresh)
        user.status = True
    
        response.data = {"Success": "Token set to cookie successfully", 'requestData': {"email":user.email},'token':{'refresh':refresh,'access':access}, "status":status.HTTP_200_OK}
        return response



        


# class UserProfile(APIView):
#     # Apply the IsAuthenticated permission to ensure only authenticated users can access


#     def post(self, request):
#         print("FFFFFFFFFFFFFFFFFFFFFFFF")
#         # Instantiate the JWTAuthentication class
#         # jwt_auth = JWTAuthentication()
        
#         # try:
#         #     # Attempt to authenticate the user using the token
#         #     user, token = jwt_auth.authenticate(request)
            
#         #     if user is not None:
#         #         # The user is authenticated
#         #         print("User authenticated successfully")
#         return Response({"message": "User is authenticated"}, status=status.HTTP_200_OK)
#         #     else:
#         #         # User is not authenticated
#         #         return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # except Exception as e:
#         #     # Handle any exceptions that occur during authentication
#         #     return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)



class UserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        user_obj = User.objects.get(id=user_id)
        user_profile = None
        try:
            user_profile = UserImage.objects.get(user=user_obj)
        except UserImage.DoesNotExist:
            pass

        user_details = {
            'email': user_obj.email,
            'profile': user_profile.profile_pic.url if user_profile and user_profile.profile_pic else None
        }
        

        return Response({"message": "test is working", "user_details": user_details}, status=status.HTTP_200_OK)

    

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,reqeuest):
        user = reqeuest.user
        user.status = False
        user.save()
        return Response({"detail": "Logout successful."}, status=200)



class UpdateUserProfile(APIView):

    permission_classes = [IsAuthenticated]

    def put(self,request):
        user = request.user
        profile_pic = request.FILES.get("profile_pic")

        if profile_pic:
            print("profile pic",profile_pic)
            user_image,created = UserImage.objects.get_or_create(user = user)
            user_image.profile_pic = profile_pic
            user_image.save()

            return Response({"message":"Profile Photo Updated Successfully","profilePhoto":str(profile_pic)},status=status.HTTP_200_OK)
        return Response({"error": "No profile picture provided"}, status=status.HTTP_400_BAD_REQUEST)
    



class EditUserProfile(APIView):

    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        serializer = EditProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()


        data = {
            "phone":user.phone,
            "email":user.email,
            "username":user.first_name
        }

        return Response({"message":"User profile details Updated Successfully","updatedData":data},status=status.HTTP_200_OK)

        