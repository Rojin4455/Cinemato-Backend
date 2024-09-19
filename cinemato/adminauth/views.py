from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AdminLoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from accounts.models import User
from django.db.models import F, Value
from django.db.models.functions import Coalesce,Concat

class AdminLogin(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            print("before authenticate")
            user = authenticate(request,email=email, password=password)
            print("after authenticate")
            if user is not None:
                if user.is_staff:
                    refresh = RefreshToken.for_user(user)

                    return Response({
                        'email':user.email,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'is_admin':user.is_superuser
                    },status=status.HTTP_200_OK)


                else:
                    return Response({"error": "User is not an admin."}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # If the serializer is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     




class AllUsers(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data
        page_no = data.get('currentPage')
        users_per_page = data.get('usersPerPage')
      
        users = User.objects.filter(is_staff=False).select_related('user_profile').annotate(
            profile_pic=Coalesce(F('user_profile__profile_pic'), Value(None))
        ).values('id','email', 'date_joined', 'phone', 'is_active', 'profile_pic').order_by("email")[users_per_page*(page_no-1):users_per_page+users_per_page*(page_no-1)]
        totalcount = User.objects.count()
        return Response({"message":"users frtched successfully","allUsers":users,'totalCount':totalcount},status=status.HTTP_200_OK)
        # BASE_URL = "http://127.0.0.1:8000/"
        # users = User.objects.filter(is_staff=False).select_related('user_profile').annotate(
        #     profile_pic=Coalesce(
        #         Concat(Value(BASE_URL), F('user_profile__profile_pic')),
        #         Value(f'{BASE_URL}default-profile-pic.jpg')  # Fallback to a default image if profile_pic is None
        #     )
        # ).values('email', 'date_joined', 'phone', 'is_active', 'profile_pic')

        # return Response({"message":"users frtched successfully","allUsers":users},status=status.HTTP_200_OK)

        pass

class ChangeStatus(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request,user_id):

        print("user id:", user_id)
        
        # Fetch the user object by user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        # Toggle the user's is_active status
        user.is_active = not user.is_active
        user.save()  # Save the updated user status
        
        print("User status updated")
        
        return Response({"message": "User status updated successfully"})


