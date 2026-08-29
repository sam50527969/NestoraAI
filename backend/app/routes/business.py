from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.business.models import (
    BusinessProfile,
    BusinessTeam,
    CustomerProfile,
    FinancialProfile,
    OperationalProfile,
    WorkingHours,
)
from app.database.database import get_db
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import (
    BusinessCreateRequest,
    BusinessDeleteResponse,
    BusinessListResponse,
    BusinessResponse,
    BusinessUpdateRequest,
)
from app.repositories.business_workspace_repository import (
    BusinessWorkspaceRepository,
)
from app.services.business_membership_service import (
    user_can_access_business,
    user_has_business_role,
)
from app.services.business_onboarding_service import (
    BusinessOnboardingService,
)
from app.services.business_service import BusinessService


router = APIRouter(
    prefix="/businesses",
    tags=["Businesses"],
)


def get_business_service(
    db: Session = Depends(get_db),
) -> BusinessService:
    """
    Build a BusinessService using the current database session.
    """

    repository = BusinessRepository(db)

    return BusinessService(repository)


def build_business_profile(
    *,
    business_uid: str,
    request: BusinessCreateRequest | BusinessUpdateRequest,
) -> BusinessProfile:
    """
    Convert an API request into a BusinessProfile domain object.
    """

    return BusinessProfile(
        id=business_uid,
        name=request.name,
        industry=request.industry,
        country=request.country,
        city=request.city,
        region=request.region,
        timezone=request.timezone,
        locale=request.locale,
        size=request.size,
        description=request.description,
        team=BusinessTeam(
            employee_count=request.team.employee_count,
            departments=list(request.team.departments),
            roles=dict(request.team.roles),
        ),
        customers=CustomerProfile(
            total_customers=(
                request.customers.total_customers
            ),
            active_customers=(
                request.customers.active_customers
            ),
            inactive_customers=(
                request.customers.inactive_customers
            ),
            average_monthly_customers=(
                request.customers.average_monthly_customers
            ),
            returning_customer_rate=(
                request.customers.returning_customer_rate
            ),
            average_customer_value=(
                request.customers.average_customer_value
            ),
        ),
        finances=FinancialProfile(
            currency=request.finances.currency,
            monthly_revenue=(
                request.finances.monthly_revenue
            ),
            monthly_expenses=(
                request.finances.monthly_expenses
            ),
            average_transaction_value=(
                request.finances.average_transaction_value
            ),
            marketing_budget=(
                request.finances.marketing_budget
            ),
            outstanding_receivables=(
                request.finances.outstanding_receivables
            ),
        ),
        operations=OperationalProfile(
            daily_capacity=(
                request.operations.daily_capacity
            ),
            average_daily_volume=(
                request.operations.average_daily_volume
            ),
            cancellation_rate=(
                request.operations.cancellation_rate
            ),
            utilization_rate=(
                request.operations.utilization_rate
            ),
            locations_count=(
                request.operations.locations_count
            ),
            working_hours=[
                WorkingHours(
                    day=item.day,
                    opens_at=item.opens_at,
                    closes_at=item.closes_at,
                    is_closed=item.is_closed,
                )
                for item in request.operations.working_hours
            ],
        ),
        goals=list(request.goals),
        metadata=dict(request.metadata),
    )


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business(
    request: BusinessCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessResponse:
    """
    Create a new business profile.
    """

    business_uid = (
        f"biz_{uuid.uuid4().hex[:12]}"
    )

    business = build_business_profile(
        business_uid=business_uid,
        request=request,
    )

    try:
        onboarding = BusinessOnboardingService(
            db
        )

        created, _membership = (
            onboarding.create_business_for_owner(
                business=business,
                owner_user_uid=current_user.user_uid,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    return BusinessResponse.from_profile(
        created
    )


@router.get(
    "",
    response_model=BusinessListResponse,
)
def list_businesses(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessListResponse:
    """
    Return paginated business profiles.
    """

    try:
        workspace_repository = (
            BusinessWorkspaceRepository(db)
        )

        businesses = workspace_repository.list_for_user(
            user_uid=current_user.user_uid,
            offset=offset,
            limit=limit,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    return BusinessListResponse(
        businesses=[
            BusinessResponse.from_profile(
                business
            )
            for business in businesses
        ],
        offset=offset,
        limit=limit,
        count=len(businesses),
    )


@router.get(
    "/{business_uid}",
    response_model=BusinessResponse,
)
def get_business(
    business_uid: str,
    service: BusinessService = Depends(
        get_business_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessResponse:
    """
    Retrieve one business by public UID.
    """

    if not user_can_access_business(
        db,
        user_uid=current_user.user_uid,
        business_uid=business_uid,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have access to this business."
            ),
        )

    business = service.get_business(
        business_uid
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Business '{business_uid}' "
                "was not found."
            ),
        )

    return BusinessResponse.from_profile(
        business
    )


@router.put(
    "/{business_uid}",
    response_model=BusinessResponse,
)
def update_business(
    business_uid: str,
    request: BusinessUpdateRequest,
    service: BusinessService = Depends(
        get_business_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessResponse:
    """
    Replace an existing business profile.
    """

    if not user_has_business_role(
        db,
        user_uid=current_user.user_uid,
        business_uid=business_uid,
        allowed_roles={"owner", "admin"},
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this business."
            ),
        )

    business = build_business_profile(
        business_uid=business_uid,
        request=request,
    )

    try:
        updated = service.update_business(
            business
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Business '{business_uid}' "
                "was not found."
            ),
        )

    return BusinessResponse.from_profile(
        updated
    )


@router.delete(
    "/{business_uid}",
    response_model=BusinessDeleteResponse,
)
def delete_business(
    business_uid: str,
    service: BusinessService = Depends(
        get_business_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessDeleteResponse:
    """
    Delete a business profile.
    """

    if not user_has_business_role(
        db,
        user_uid=current_user.user_uid,
        business_uid=business_uid,
        allowed_roles={"owner"},
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only an owner can delete this business."
            ),
        )

    try:
        workspace_repository = (
            BusinessWorkspaceRepository(db)
        )
        deleted = workspace_repository.delete_workspace(
            business_uid=business_uid,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The business workspace could not be deleted."
            ),
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Business '{business_uid}' "
                "was not found."
            ),
        )

    return BusinessDeleteResponse(
        success=True,
        business_uid=business_uid,
        message="Business deleted successfully.",
    )
