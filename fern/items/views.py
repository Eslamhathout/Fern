import logging
from datetime import timedelta

from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from rest_framework import filters, generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Item
from .serializers import ItemSerializer

logger = logging.getLogger(__name__)


class ItemList(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    List, delete, or filter items.
    """
    queryset = Item.objects.filter(Q(expiry_time__gt=timezone.now()) | Q(expiry_time__isnull=True))
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['$name']

    def get_object(self):
        return Item.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ItemDetail(APIView):
    """
    Retrieve, update or delete a code item.
    """
    def get_object(self, pk):
        try:
            return Item.objects.get(Q(pk=pk) & Q(Q(expiry_time__gt=timezone.now()) | Q(expiry_time__isnull=True)))
        except Item.DoesNotExist:
            logger.warning('[{}] Item not found'.format(pk))
            raise Http404

    def get(self, request, pk, format=None):
        item = self.get_object(pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        item = self.get_object(pk)
        expiry_in_minutes = request.query_params.get('expire_in', None)
        if expiry_in_minutes is not None:
            logger.info('[{}] Item is eligiable for expiry.'.format(pk))
            item.expiry_date = timezone.now() + timedelta(minutes=int(expiry_in_minutes))
            item.save()
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def head(self, request, pk, format=None):
        if self.get_object(pk):
            from rest_framework.metadata import SimpleMetadata
            meta = SimpleMetadata()
            data = meta.determine_metadata(request, self)
            logger.info('[{}] Item exists with following info: {}'.format(pk, data))
            return Response(data, status=status.HTTP_200_OK)
