from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import OwnerSignupSerializer,OwnerLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class OwnerSignupView(APIView):
    def post(self, request, *args, **kwargs):
        # Pass request data to the OwnerSignupSerializer
        print("reach here")
        serializer = OwnerSignupSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            owner = serializer.save()
            
            # Customize the response to exclude sensitive data
            response_data = {
                'id': owner.id,
                'email': owner.email,
                'phone': owner.phone,
                'first_name': owner.first_name,
                'business_name': owner.business_name,
                'is_owner': owner.is_owner,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            # Return errors if the data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class OwnerLoginView(APIView):
    def post(self, request):
        serializer = OwnerLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)
            print("valid user")
            # tokens = serializer.get_tokens(user)

            return Response({
                'message': 'Login successful',
                'token': {'refresh':refresh,"access":access},
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'business_name': user.business_name
                }
            }, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OwnerLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    pass