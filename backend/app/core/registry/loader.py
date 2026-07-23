from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from types import ModuleType

from app.core.registry.models import ExecutiveManifest
from app.core.registry.registry import (
    ExecutiveAlreadyRegisteredError,
    ExecutiveRegistry,
    executive_registry,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ExecutiveLoadError:
    """
    Information about an executive package that failed to load.
    """

    package_name: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "package_name": self.package_name,
            "message": self.message,
        }


@dataclass(slots=True)
class ExecutiveLoadReport:
    """
    Summary returned after executive discovery completes.
    """

    discovered_packages: int = 0
    registered_executives: list[str] = field(
        default_factory=list,
    )
    skipped_packages: list[str] = field(
        default_factory=list,
    )
    errors: list[ExecutiveLoadError] = field(
        default_factory=list,
    )

    @property
    def registered_count(self) -> int:
        return len(self.registered_executives)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_packages)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def successful(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "discovered_packages": (
                self.discovered_packages
            ),
            "registered_count": self.registered_count,
            "registered_executives": list(
                self.registered_executives
            ),
            "skipped_count": self.skipped_count,
            "skipped_packages": list(
                self.skipped_packages
            ),
            "error_count": self.error_count,
            "errors": [
                error.to_dict()
                for error in self.errors
            ],
            "successful": self.successful,
        }


class ExecutiveLoader:
    """
    Discovers and registers executive manifests.

    Each direct package inside app.executives may contain
    a manifest.py module with one or more ExecutiveManifest
    instances.
    """

    def __init__(
        self,
        registry: ExecutiveRegistry | None = None,
        *,
        executives_package: str = "app.executives",
    ) -> None:
        self.registry = registry or executive_registry
        self.executives_package = executives_package

    def load_all(
        self,
        *,
        replace: bool = False,
        raise_on_error: bool = False,
    ) -> ExecutiveLoadReport:
        """
        Discover and register every available executive.

        Args:
            replace:
                Replace an existing registry entry when an
                executive with the same ID is discovered.

            raise_on_error:
                Immediately raise an exception when a package
                cannot be imported or contains an invalid
                manifest.

        Returns:
            ExecutiveLoadReport containing the complete result.
        """

        report = ExecutiveLoadReport()

        try:
            root_package = importlib.import_module(
                self.executives_package
            )
        except Exception as exc:
            message = (
                f"Unable to import executives package "
                f"'{self.executives_package}': {exc}"
            )

            if raise_on_error:
                raise RuntimeError(message) from exc

            report.errors.append(
                ExecutiveLoadError(
                    package_name=self.executives_package,
                    message=message,
                )
            )

            logger.exception(message)
            return report

        package_paths = getattr(
            root_package,
            "__path__",
            None,
        )

        if package_paths is None:
            message = (
                f"'{self.executives_package}' is not "
                "a Python package."
            )

            if raise_on_error:
                raise RuntimeError(message)

            report.errors.append(
                ExecutiveLoadError(
                    package_name=self.executives_package,
                    message=message,
                )
            )

            logger.error(message)
            return report

        discovered = sorted(
            pkgutil.iter_modules(package_paths),
            key=lambda item: item.name,
        )

        for package_info in discovered:
            if not package_info.ispkg:
                continue

            package_name = package_info.name

            if package_name.startswith("_"):
                continue

            report.discovered_packages += 1

            self._load_package(
                package_name=package_name,
                report=report,
                replace=replace,
                raise_on_error=raise_on_error,
            )

        logger.info(
            "Executive discovery completed: "
            "%s registered, %s skipped, %s errors.",
            report.registered_count,
            report.skipped_count,
            report.error_count,
        )

        return report

    def _load_package(
        self,
        *,
        package_name: str,
        report: ExecutiveLoadReport,
        replace: bool,
        raise_on_error: bool,
    ) -> None:
        manifest_module_name = (
            f"{self.executives_package}."
            f"{package_name}.manifest"
        )

        try:
            manifest_module = importlib.import_module(
                manifest_module_name
            )
        except ModuleNotFoundError as exc:
            if exc.name == manifest_module_name:
                report.skipped_packages.append(package_name)

                logger.debug(
                    "Skipping executive package '%s': "
                    "manifest.py was not found.",
                    package_name,
                )
                return

            self._handle_error(
                package_name=package_name,
                message=(
                    f"Dependency import failed while loading "
                    f"'{manifest_module_name}': {exc}"
                ),
                exception=exc,
                report=report,
                raise_on_error=raise_on_error,
            )
            return
        except Exception as exc:
            self._handle_error(
                package_name=package_name,
                message=(
                    f"Unable to import "
                    f"'{manifest_module_name}': {exc}"
                ),
                exception=exc,
                report=report,
                raise_on_error=raise_on_error,
            )
            return

        manifests = self._find_manifests(
            manifest_module
        )

        if not manifests:
            self._handle_error(
                package_name=package_name,
                message=(
                    f"No ExecutiveManifest instance found in "
                    f"'{manifest_module_name}'."
                ),
                exception=None,
                report=report,
                raise_on_error=raise_on_error,
            )
            return

        for manifest in manifests:
            try:
                self.registry.register(
                    manifest,
                    replace=replace,
                )
            except ExecutiveAlreadyRegisteredError:
                if replace:
                    raise

                report.skipped_packages.append(
                    package_name
                )

                logger.warning(
                    "Executive '%s' is already registered; "
                    "package '%s' was skipped.",
                    manifest.executive_id,
                    package_name,
                )
                continue
            except Exception as exc:
                self._handle_error(
                    package_name=package_name,
                    message=(
                        f"Unable to register executive "
                        f"'{manifest.executive_id}': {exc}"
                    ),
                    exception=exc,
                    report=report,
                    raise_on_error=raise_on_error,
                )
                continue

            report.registered_executives.append(
                manifest.executive_id
            )

            logger.info(
                "Registered executive: %s (%s)",
                manifest.name,
                manifest.executive_id,
            )

    @staticmethod
    def _find_manifests(
        module: ModuleType,
    ) -> list[ExecutiveManifest]:
        """
        Find all ExecutiveManifest objects declared in a module.
        """

        manifests: dict[str, ExecutiveManifest] = {}

        for value in vars(module).values():
            if not isinstance(
                value,
                ExecutiveManifest,
            ):
                continue

            manifests[value.executive_id] = value

        return sorted(
            manifests.values(),
            key=lambda item: item.executive_id,
        )

    @staticmethod
    def _handle_error(
        *,
        package_name: str,
        message: str,
        exception: Exception | None,
        report: ExecutiveLoadReport,
        raise_on_error: bool,
    ) -> None:
        if raise_on_error:
            if exception is not None:
                raise RuntimeError(
                    message
                ) from exception

            raise RuntimeError(message)

        report.errors.append(
            ExecutiveLoadError(
                package_name=package_name,
                message=message,
            )
        )

        if exception is not None:
            logger.exception(message)
        else:
            logger.error(message)


executive_loader = ExecutiveLoader()


def load_executives(
    *,
    replace: bool = False,
    raise_on_error: bool = False,
) -> ExecutiveLoadReport:
    """
    Load executives into the shared global registry.
    """

    return executive_loader.load_all(
        replace=replace,
        raise_on_error=raise_on_error,
    )