from rest_framework import serializers
from .models import User, OTP
from django.utils import timezone
from random import randint

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False,allow_null=True, allow_blank=True)
    phone = serializers.CharField(max_length=12, required=False,allow_null=True, allow_blank=True)

    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone')

        if not email and not phone:
            raise serializers.ValidationError('Either email or phone number must be provided.')
        if email and phone:
            raise serializers.ValidationError('Only one of email or phone number should be provided.')

        return data


    def create_otp(self, validated_data):
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        if email:
        
        # Assuming one user can only have one OTP at a time
            OTP.objects.filter(email=email).delete()

            otp_code = str(randint(100000, 999999))
            print("otpppppppppppppppp1",otp_code,email,phone)
            
            otp = OTP.objects.create(
                otp=otp_code,
                email=email,
            )
            return otp_code
        if phone:
            OTP.objects.filter(phone=phone).delete()

            otp_code = str(randint(100000, 999999))
            
            otp = OTP.objects.create(
                otp=otp_code,
                phone=phone,
            )
            return otp_code
            




class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    def validate(self, data):
        print("Validating OTP and contact details")
        otp = data.get('otp')
        email = data.get('email')
        phone = data.get('phone')
        print("Received email:", email, "Received phone:", phone)
        if email:

            otp_instance = OTP.objects.filter(otp=otp).filter(
                email=email
            ).first()
            print("OTP INSTANCE ",otp_instance)
            if not otp_instance or not otp_instance.is_valid():
                raise serializers.ValidationError('Invalid or expired OTP.')

            return data
        
        elif phone:


            otp_instance = OTP.objects.filter(otp=otp).filter(
                phone=phone
            ).first() 
            print("OTP INSTANCE ",otp_instance)
            if not otp_instance or not otp_instance.is_valid():
                raise serializers.ValidationError('Invalid or expired OTP.')

            return data

        else:
            raise serializers.ValidationError('You must provide either an email or a phone number.')

    def create_user(self, validated_data):
        print("ferrere")
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        # Check if the user already exists before creating
        if email:
            if User.objects.filter(email=email).exists():
                print("User already exists with this email")
                print(User.objects.filter(email=email))
                print("FERRREFFEREFEETETE")
                return User.objects.get(email=email)
        elif phone:  
            if User.objects.filter(phone=phone).exists():
                print("User already exists with this email")
                print(User.objects.filter(email=email))
                print("phone user pirintt")
                return User.objects.get(phone=phone)
        
        user = User.objects.create(
            email=email if email else None,
            phone=phone if phone else None,
            first_name=first_name,
            last_name=last_name
        )
        print("User created:", user)
        return user
    


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)