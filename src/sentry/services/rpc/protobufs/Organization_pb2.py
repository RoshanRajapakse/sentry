# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sentry/services/rpc/protobufs/Organization.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from sentry.services.rpc.protobufs import (
    User_pb2 as sentry_dot_services_dot_rpc_dot_protobufs_dot_User__pb2,
)

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n0sentry/services/rpc/protobufs/Organization.proto\x1a(sentry/services/rpc/protobufs/User.proto"(\n\x0cOrganization\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t2H\n\x13OrganizationService\x12\x31\n\nChangeName\x12\x12.ChangeNameRequest\x1a\r.Organization"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "sentry.services.rpc.protobufs.Organization_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _ORGANIZATION._serialized_start = 94
    _ORGANIZATION._serialized_end = 134
    _ORGANIZATIONSERVICE._serialized_start = 136
    _ORGANIZATIONSERVICE._serialized_end = 208
# @@protoc_insertion_point(module_scope)
