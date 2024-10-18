from rest_framework import serializers
from .models import Theater, Screen, Tier, ScreenImage, Seat
import cloudinary.uploader



class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'



class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class TierSerializer(serializers.ModelSerializer):

    seats = SeatSerializer(many=True, required=False)

    class Meta:
        model = Tier
        fields = ['name', 'price', 'total_seats', 'seats', 'id']

class ScreenImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenImage
        fields = ['image_url']


# class AllScreenSerializer(serializers.ModelSerializer):
#     screen_images = ScreenImageSerializer(many=True,read_only=True)
#     class Meta:
#         model = Screen
#         fields = ['name', 'type', 'tiers', 'screen_images', 'theater']



class ScreenSerializer(serializers.ModelSerializer):
    tiers = TierSerializer(many=True)
    screen_images = ScreenImageSerializer(many=True, required=False)
    

    class Meta:
        model = Screen
        fields = ['name', 'type', 'tiers', 'screen_images', 'theater', 'capacity','id']

    def create(self, validated_data):
        tiers_data = validated_data.pop('tiers')
        screen_images_data = validated_data.pop('screen_images', [])

        screen = Screen.objects.create(**validated_data)

        request = self.context.get('request')
        screen_images_data = request.FILES.getlist('screen_images[]')


        for image_file in screen_images_data:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="screen_photos"
            )
            
            image_url = upload_result.get('secure_url')

            ScreenImage.objects.create(screen=screen, image_url=image_url)


        print("Screen images data: ", screen_images_data)
        

        for tier_data in tiers_data:
            Tier.objects.create(screen=screen, **tier_data)


        return screen

    def update(self, instance, validated_data):
        tiers_data = validated_data.pop('tiers', [])
        screen_images_data = validated_data.pop('screen_images', [])
        
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.save()

        for tier_data in tiers_data:
            tier_id = tier_data.get('id', None)
            if tier_id:
                Tier.objects.filter(id=tier_id, screen=instance).update(**tier_data)
            else:
                Tier.objects.create(screen=instance, **tier_data)

        if screen_images_data:
            ScreenImage.objects.filter(screen=instance).delete()
            for image_data in screen_images_data:
                ScreenImage.objects.create(screen=instance, **image_data)

        return instance

    def validate(self, attrs):
        if 'tiers' not in attrs or not attrs['tiers']:
            raise serializers.ValidationError("At least one tier must be provided.")
        return attrs
