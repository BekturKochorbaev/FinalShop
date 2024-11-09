from django.shortcuts import render
from requests import Response
from rest_framework import viewsets, permissions, generics, status
from .serializers import *
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from rest_framework import filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .permissions import ChekOwner


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'detail': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProductListViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name']
    ordering_fields = ['price', 'date']
    filterset_class = ProductListFilter
    permission_classes = [permissions.IsAuthenticated, ChekOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductDetailViewSet(viewsets.ModelViewSet):
     queryset = Product.objects.all()
     serializer_class = ProductDetailSerializer
     permission_classes = [permissions.IsAuthenticatedOrReadOnly, ChekOwner]


     def perform_create(self, serializer):
      serializer.save(owner=self.request.user)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileTwoViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileTwoSerializer


class ProductPhotoViewSet(viewsets.ModelViewSet):
    queryset = ProductPhoto.objects.all()
    serializer_class = ProductPhotoSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer


    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer


    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


