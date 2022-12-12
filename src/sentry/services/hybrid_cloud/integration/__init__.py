from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

from sentry.constants import ObjectStatus
from sentry.models.integrations import Integration
from sentry.services.hybrid_cloud import InterfaceWithLifecycle, silo_mode_delegation, stubbed
from sentry.silo import SiloMode


@dataclass(frozen=True)
class APIIntegration(Integration):
    id: int
    provider: str
    external_id: str
    name: str
    metadata: Mapping[str, Any]
    status: ObjectStatus


class IntegrationService(InterfaceWithLifecycle):
    @abstractmethod
    def get_by_provider_id(self, provider: str, external_id: str) -> APIIntegration | None:
        pass


def impl_with_db() -> IntegrationService:
    from sentry.services.hybrid_cloud.integration.impl import DatabaseBackedIntegrationService

    return DatabaseBackedIntegrationService()


integration_service: IntegrationService = silo_mode_delegation(
    {
        SiloMode.MONOLITH: impl_with_db,
        SiloMode.REGION: stubbed(impl_with_db, SiloMode.CONTROL),
        SiloMode.CONTROL: impl_with_db,
    }
)
