from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = UserProfile
      fields =('username', 'email', 'password', 'first_name', 'last_name',
                'age', 'phone_number', 'status', 'date_registered')
      extra_kwargs = {'password': {'write_only': True}}

   def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

   def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверные учетные данные')

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),

        }

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileTwoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class RatingSerializer(serializers.ModelSerializer):
    user = UserProfileTwoSerializer()
    class Meta:
        model = Rating
        fields = ['user', 'stars']


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = ['image']


class ReviewSerializer(serializers.ModelSerializer):
    author = UserProfileTwoSerializer()
    date = serializers.DateTimeField('%d-%m-%Y ' '%H-%M')
    class Meta:
        model = Review
        fields = ['author', 'text', 'date', 'prent_view']


class ProductListSerializer(serializers.ModelSerializer):
    products_photo = ProductPhotoSerializer(read_only=True, many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_name', 'products_photo', 'price', 'average_rating']

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    ratings = RatingSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    date = serializers.DateTimeField('%d-%m-%Y %H-%M')
    products_photo = ProductPhotoSerializer(read_only=True, many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_name', 'category', 'description', 'price', 'date', 'active',
                  'product_video', 'products_photo', 'average_rating', 'ratings', 'reviews']

    def get_average_rating(self, obj):
        return obj.get_average_rating()

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
