from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AdminLoginSerializer,TheaterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from accounts.models import User
from django.db.models import F, Value
from django.db.models.functions import Coalesce,Concat
from ownerauth.serializers import TheaterOwnerSerializer
from theater_managemant.models import Theater
from django.shortcuts import get_object_or_404


class AdminLogin(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            print("before authenticate")
            user = authenticate(request,email=email, password=password)
            print("after authenticate",user)
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


class GetTheaterOwnersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owners = User.objects.filter(is_owner=True, is_approved=True)
        serializer = TheaterOwnerSerializer(owners, many=True)  # Serialize the data
        return Response({"message": "All owners retrieved", "allOwners": serializer.data}, status=status.HTTP_200_OK)


class GetRequestedOwnersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owners = User.objects.filter(is_owner=True, is_approved=False)
        serializer = TheaterOwnerSerializer(owners, many=True)  # Serialize the data
        return Response({"message": "All owners retrieved", "allOwners": serializer.data}, status=status.HTTP_200_OK)
    

class GetOwnerDetails(APIView):
    def get(self, request, ownerId):
        try:
            owner = User.objects.get(id=ownerId)
            serializer = TheaterOwnerSerializer(owner)
            print("owner got", owner)
            
            print("serializer obj", serializer)
            return Response({"message": "Owner found successfully", "owner_data": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            print("Owner not found with that ID")
            return Response({"message": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)


    

class ApproveTheaterOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request, owner_id):
        try:
            owner = User.objects.get(id = owner_id)
            owner.is_approved = True
            owner.save()
            return Response({"message": "Theater owner approved successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Theater owner not found"}, status=status.HTTP_404_NOT_FOUND)



# class DisapproveTheaterOwnerView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self,request, owner_id):
#         try:
#             owner = User.objects.get(id = owner_id)
#             owner.is_approved = False
#             owner.save()
#             return Response({"message": "Theater owner Disapproved successfully"}, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({"error": "Theater owner not found"}, status=status.HTTP_404_NOT_FOUND)



class OwnerAllDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        try:
            # Fetch the owner by id
            owner = get_object_or_404(User, id=id)
            
            # Fetch all theaters owned by this owner
            theaters = Theater.objects.filter(owner=owner)

            # Serialize owner and theater data
            owner_data = {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'email': owner.email,
                'phone': owner.phone,
                'theaters': TheaterSerializer(theaters, many=True).data  # serialize theaters
            }
            
            return Response({
                "message": "Owner details found successfully",
                "owner_data": owner_data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)