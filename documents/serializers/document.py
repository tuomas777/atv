from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from atv.exceptions import (
    DocumentLockedException,
    InvalidFieldException,
    MaximumFileCountExceededException,
)
from users.models import User

from ..models import Document
from .attachment import (
    AttachmentSerializer,
    CreateAttachmentSerializer,
    GDPRAttachmentSerializer,
)
from .status_history import StatusHistorySerializer


def status_to_representation(representation):
    status_timestamp = representation.pop("status_timestamp")
    status_display_values = representation.pop("status_display_values")
    representation["status"] = {
        "value": representation["status"],
        "status_display_values": status_display_values,
        "timestamp": status_timestamp,
    }
    return representation


class GDPRDocumentSerializer(serializers.ModelSerializer):
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )
    attachments = GDPRAttachmentSerializer(many=True)
    attachment_count = serializers.IntegerField()
    user_id = serializers.UUIDField(source="user.uuid", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "user_id",
            "service",
            "type",
            "human_readable_type",
            "deletable",
            "attachment_count",
            "attachments",
        )


class GDPRSerializer(serializers.Serializer):  # noqa
    data = serializers.SerializerMethodField()

    def get_data(self, documents_qs):
        documents_qs = documents_qs.annotate(attachment_count=Count("attachments"))
        total_deletable = 0
        total_undeletable = 0
        total = documents_qs.count()
        deletable = documents_qs.filter(deletable=True).count()
        total_deletable += deletable
        total_undeletable += total - deletable

        stats = {
            "total_deletable": total_deletable,
            "total_undeletable": total_undeletable,
            "documents": GDPRDocumentSerializer(documents_qs, many=True).data,
        }
        return stats


class DocumentMetadataSerializer(serializers.HyperlinkedModelSerializer):
    status_histories = StatusHistorySerializer(many=True, read_only=True)
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )

    class Meta:
        model = Document
        fields = (
            "id",
            "type",
            "human_readable_type",
            "created_at",
            "updated_at",
            "service",
            "status",
            "status_display_values",
            "status_timestamp",
            "status_histories",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return status_to_representation(rep)


class DocumentSerializer(serializers.ModelSerializer):
    """Basic "read" serializer for the Document model"""

    user_id = serializers.UUIDField(
        source="user.uuid", required=False, default=None, read_only=True
    )
    attachments = AttachmentSerializer(many=True, required=False, read_only=True)
    content = serializers.JSONField(
        required=True, decoder=None, encoder=DjangoJSONEncoder
    )
    service = serializers.CharField(
        source="service.name", required=False, read_only=True
    )
    status_histories = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created_at",
            "updated_at",
            "status",
            "status_display_values",
            "status_timestamp",
            "status_histories",
            "type",
            "human_readable_type",
            "service",
            "user_id",
            "transaction_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "content",
            "draft",
            "locked_after",
            "deletable",
            "attachments",
        )

    def update(self, document, validated_data):
        # If the document has been locked, no further updates are allowed
        if document.locked_after and document.locked_after <= now():
            raise DocumentLockedException()

        user_id = self.initial_data.get("user_id", None)
        if user_id:
            if document.user_id:
                raise PermissionDenied(
                    detail="Document owner can not be changed.",
                    code="invalid field: user_id",
                )

            user, created = User.objects.get_or_create(
                uuid=user_id, defaults={"username": f"User-{user_id}"}
            )
            document.user = user
            document.save()

        return super().update(document, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return status_to_representation(representation)


class CreateAnonymousDocumentSerializer(serializers.ModelSerializer):
    """Create a Document with Attachment for an anonymous user submitting the document
    through a Service authorized with an API key.

    Also handles the creation of the associated Attachments through `CreateAttachmentSerializer`.
    """

    user_id = serializers.UUIDField(source="user.uuid", required=False, default=None)
    attachments = serializers.ListField(child=serializers.FileField(), required=False)
    content = serializers.JSONField(
        required=True, decoder=None, encoder=DjangoJSONEncoder
    )

    class Meta:
        model = Document
        fields = (
            "status",
            "status_display_values",
            "type",
            "human_readable_type",
            "user_id",
            "transaction_id",
            "business_id",
            "tos_function_id",
            "tos_record_id",
            "metadata",
            "content",
            "draft",
            "locked_after",
            "attachments",
            "deletable",
        )

    def validate(self, attrs):
        # Validate that no additional fields are being passed (to sanitize the input)
        if hasattr(self, "initial_data"):
            invalid_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if invalid_keys:
                raise InvalidFieldException(
                    detail=_("Got invalid input fields: {list_of_fields}").format(
                        list_of_fields=", ".join(invalid_keys)
                    )
                )

        # Validate that no more than settings.MAX_FILE_UPLOAD_ALLOWED files
        # are uploaded on the same call
        if len(attrs.get("attachments", [])) > settings.MAX_FILE_UPLOAD_ALLOWED:
            raise MaximumFileCountExceededException()

        return attrs

    def create(self, validated_data):
        attachments = validated_data.pop("attachments", [])

        document = Document.objects.create(**validated_data)
        for attached_file in attachments:
            data = {
                "document": document.id,
                "file": attached_file,
                "media_type": attached_file.content_type,
            }
            attachment_serializer = CreateAttachmentSerializer(data=data)
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()
        return document
