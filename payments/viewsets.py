from rest_framework.viewsets import ReadOnlyModelViewSet

from core.permissions import EvibesPermission, IsOwner
from payments.serializers import TransactionSerializer


class TransactionViewSet(ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (EvibesPermission, IsOwner)
