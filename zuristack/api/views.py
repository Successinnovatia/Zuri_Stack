import email
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from . permissions import IsCreatorOrAdminReadOnly
from . import serializers
# Create your views here.

UserModel = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    default_serializer_class = serializers.UserOutputSerializer

    serializers_classes = {
        "create": serializers.UserInputSerializer
    }

    def create(self, request, *args, **kwargs):
        """"
        User SignUp
            -Allow anyone to signup (without authentication)
        """
        self.check_permissions(request)
        serializer = serializers.UserInputSerializer(data = request.POST)
        serializer.is_valid(raise_exception=True)

        user = UserModel.objects.create_user(
            email = serializer.validated_data["email"],
            first_name = serializer.validated_data["first_name"],
            last_name = serializer.validated_data["last_name"],
            password = serializer.validated_data["password"]
        )
        response  = serializers.UserOutputSerializer(user).data
        return Response(response, status=status.HTTP_201_CREATED)


    def retrieve(self, request, pk=None):
        #check if pk is a valid slug
        user = UserModel.objects.filter(slug=pk).first()

        if not user and pk.isdigit():
            #find user by primary key/ID
            user = UserModel.objects.filter(pk=pk).first()

        self.check_object_permissions(request, user)
        response = serializers.UserOutputSerializer(user).data
        return Response(response, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'create': #Create, List, Retrieve, Update, or Destroy
            permissions_classes  = [permissions.AllowAny]
        elif self.action == 'retrieve':
            permissions_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions_classes = [IsCreatorOrAdminReadOnly, permissions.IsAuthenticated]
        elif self.action == 'list' :
            permissions_classes = [permissions.IsAdminUser]
        else:
            permissions_classes = [permissions.IsAdminUser]
        
        return (permission() for permission in permissions_classes)


    def get_serializer_class(self):
        return self.serializers_classes.get(self.action, self.default_serializer_class)