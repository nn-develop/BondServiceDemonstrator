from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from users.serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    """
    View for user registration.
    """

    serializer_class = RegisterSerializer
    permission_classes: list[type[AllowAny]] = [AllowAny]


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom view for obtaining auth token with public access.
    """

    permission_classes: list[type[AllowAny]] = [AllowAny]


class CustomLogoutView(APIView):
    """
    View for logging out the user by deleting their auth token.
    """

    authentication_classes: list[type[TokenAuthentication]] = [TokenAuthentication]

    def post(self, request, *args, **kwargs) -> Response:
        """
        Log out the user by deleting the auth token.
        """
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=200)
