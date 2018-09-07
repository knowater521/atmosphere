from rest_framework import serializers

from core.models import (Volume, Project)
from api.v2.serializers.fields.base import ModelRelatedField, InstanceSourceHyperlinkedIdentityField
from api.v2.serializers.summaries import (
    IdentitySummarySerializer,
    ProviderSummarySerializer,
    ProjectSummarySerializer,
    UserSummarySerializer
)
from core.models import Identity, Provider


class VolumeSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)

    identity = ModelRelatedField(source="instance_source.created_by_identity",
                                 lookup_field="uuid",
                                 queryset=Identity.objects.all(),
                                 serializer_class=IdentitySummarySerializer,
                                 style={'base_template': 'input.html'})

    provider = ModelRelatedField(source="instance_source.provider",
                                 queryset=Provider.objects.all(),
                                 serializer_class=ProviderSummarySerializer,
                                 style={'base_template': 'input.html'},
                                 required=False)

    user = UserSummarySerializer(source='instance_source.created_by',
                                 read_only=True)

    project = ModelRelatedField(
        queryset=Project.objects.all(),
        serializer_class=ProjectSummarySerializer,
        style={'base_template': 'input.html'})
    uuid = serializers.CharField(source='instance_source.identifier',
                                 read_only=True)
    # NOTE: this is still using ID instead of UUID -- due to abstract classes
    # and use of getattr in L271 of rest_framework/relations.py, this is a
    # 'kink' that has not been worked out yet.
    url = InstanceSourceHyperlinkedIdentityField(
        view_name='api:v2:volume-detail',
    )

    class Meta:
        model = Volume

        read_only_fields = ("user", "uuid", "start_date", "end_date")
        fields = (
            'id',
            'uuid',
            'name',
            'description',
            'identity',
            'user',
            'provider',
            'project',
            'size',
            'url',
            'start_date',
            'end_date')

    def validate(self, data):
        if not data and not self.initial_data:
            return data
        raise Exception(
            "This serializer for GET output ONLY! -- "
            "Use the POST or UPDATE serializers instead!")


class UpdateVolumeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    project = ModelRelatedField(
        queryset=Project.objects.all(),
        serializer_class=ProjectSummarySerializer,
        style={'base_template': 'input.html'})

    class Meta:
        model = Volume
        view_name = 'api:v2:volume-detail'
        fields = ('name', 'description', 'project')
