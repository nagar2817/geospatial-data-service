# from typing import List, Optional
# from uuid import UUID
# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from database import AsyncRepositoryFactory
# from database.repositories.alert_repository import AlertCreate as DBAlertCreate, AlertUpdate as DBAlertUpdate
# from api.dependencies import get_repository_factory, validate_alert_exists, CommonParams
# from api.alert_schema import (
#     AlertCreate, AlertUpdate, AlertResponse, AlertListResponse,
#     AlertResolveRequest, BulkAlertResolveRequest, AlertDeliveryUpdate,
#     AlertStatistics, AlertDeliveryStats, AlertType, AlertSeverity, DeliveryStatus
# )

# router = APIRouter(prefix="/alerts", tags=["alerts"])

# @router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
# async def create_alert(
#     alert_data: AlertCreate,
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Create a new alert."""
#     db_alert_data = DBAlertCreate(**alert_data.model_dump())
#     alert = await repo_factory.alert.create(db_alert_data)
#     return AlertResponse.model_validate(alert)

# @router.get("/", response_model=AlertListResponse)
# async def list_alerts(
#     commons: CommonParams,
#     alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
#     severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
#     delivery_status: Optional[DeliveryStatus] = Query(None, description="Filter by delivery status"),
#     resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
#     job_run_id: Optional[UUID] = Query(None, description="Filter by job run ID"),
#     anomaly_id: Optional[UUID] = Query(None, description="Filter by anomaly ID"),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """List all alerts with optional filtering."""
#     filters = {}
#     if alert_type:
#         filters["alert_type"] = alert_type.value
#     if severity:
#         filters["severity"] = severity.value
#     if delivery_status:
#         filters["delivery_status"] = delivery_status.value
#     if resolved is not None:
#         filters["resolved"] = resolved
#     if job_run_id:
#         filters["job_run_id"] = job_run_id
#     if anomaly_id:
#         filters["anomaly_id"] = anomaly_id

#     alerts = await repo_factory.alert.get_multi(
#         skip=commons.skip,
#         limit=commons.limit,
#         filters=filters
#     )
#     total = await repo_factory.alert.count(filters)
    
#     return AlertListResponse(
#         alerts=[AlertResponse.model_validate(alert) for alert in alerts],
#         total=total,
#         skip=commons.skip,
#         limit=commons.limit
#     )

# @router.get("/{alert_id}", response_model=AlertResponse)
# async def get_alert(
#     alert_id: UUID,
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Get a specific alert by ID."""
#     alert = await repo_factory.alert.get(alert_id)
#     if not alert:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Alert with ID {alert_id} not found"
#         )
#     return AlertResponse.model_validate(alert)

# @router.put("/{alert_id}", response_model=AlertResponse)
# async def update_alert(
#     alert_id: UUID,
#     alert_data: AlertUpdate,
#     alert = Depends(validate_alert_exists),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Update an existing alert."""
#     db_alert_data = DBAlertUpdate(**alert_data.model_dump(exclude_unset=True))
#     updated_alert = await repo_factory.alert.update(alert, db_alert_data)
#     return AlertResponse.model_validate(updated_alert)

# @router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_alert(
#     alert_id: UUID,
#     alert = Depends(validate_alert_exists),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Delete an alert."""
#     await repo_factory.alert.delete(alert_id)

# @router.post("/{alert_id}/resolve", response_model=AlertResponse)
# async def resolve_alert(
#     alert_id: UUID,
#     resolve_data: AlertResolveRequest,
#     alert = Depends(validate_alert_exists),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Mark an alert as resolved."""
#     from datetime import datetime
    
#     update_data = DBAlertUpdate(
#         resolved=True,
#         resolved_by=resolve_data.resolved_by,
#         resolved_at=datetime.utcnow(),
#         metadata={
#             **(alert.metadata or {}),
#             "resolution_notes": resolve_data.resolution_notes
#         } if resolve_data.resolution_notes else alert.metadata
#     )
    
#     updated_alert = await repo_factory.alert.update(alert, update_data)
#     return AlertResponse.model_validate(updated_alert)

# @router.post("/resolve-bulk", response_model=dict)
# async def resolve_alerts_bulk(
#     resolve_data: BulkAlertResolveRequest,
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Resolve multiple alerts at once."""
#     # Note: This would need to be implemented in the async repository
#     # For now, we'll resolve them one by one
#     resolved_count = 0
#     for alert_id in resolve_data.alert_ids:
#         alert = await repo_factory.alert.get(alert_id)
#         if alert and not alert.resolved:
#             from datetime import datetime
            
#             update_data = DBAlertUpdate(
#                 resolved=True,
#                 resolved_by=resolve_data.resolved_by,
#                 resolved_at=datetime.utcnow(),
#                 metadata={
#                     **(alert.metadata or {}),
#                     "resolution_notes": resolve_data.resolution_notes
#                 } if resolve_data.resolution_notes else alert.metadata
#             )
            
#             await repo_factory.alert.update(alert, update_data)
#             resolved_count += 1
    
#     return {
#         "message": f"Successfully resolved {resolved_count} alerts",
#         "resolved_count": resolved_count,
#         "total_requested": len(resolve_data.alert_ids)
#     }

# @router.get("/unresolved/count", response_model=dict)
# async def get_unresolved_alert_count(
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Get count of unresolved alerts."""
#     unresolved_alerts = await repo_factory.alert.get_unresolved()
#     return {
#         "unresolved_count": len(unresolved_alerts),
#         "critical_count": sum(1 for alert in unresolved_alerts if alert.severity == "critical"),
#         "error_count": sum(1 for alert in unresolved_alerts if alert.severity == "error"),
#         "warning_count": sum(1 for alert in unresolved_alerts if alert.severity == "warning")
#     }

# @router.get("/unresolved/list", response_model=AlertListResponse)
# async def list_unresolved_alerts(
#     commons: CommonParams,
#     severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Get all unresolved alerts."""
#     unresolved_alerts = await repo_factory.alert.get_unresolved()
    
#     # Apply severity filter if provided
#     if severity:
#         unresolved_alerts = [alert for alert in unresolved_alerts if alert.severity == severity.value]
    
#     # Apply pagination
#     total = len(unresolved_alerts)
#     paginated_alerts = unresolved_alerts[commons.skip:commons.skip + commons.limit]
    
#     return AlertListResponse(
#         alerts=[AlertResponse.model_validate(alert) for alert in paginated_alerts],
#         total=total,
#         skip=commons.skip,
#         limit=commons.limit
#     )

# @router.get("/critical/recent", response_model=AlertListResponse)
# async def get_recent_critical_alerts(
#     hours: int = Query(24, description="Number of hours to look back"),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Get recent critical alerts."""
#     # Note: This would need to be implemented in the async repository
#     # For now, we'll get recent alerts and filter
#     from datetime import datetime, timedelta
    
#     cutoff_time = datetime.utcnow() - timedelta(hours=hours)
#     all_alerts = await repo_factory.alert.get_multi(limit=1000)
    
#     critical_alerts = [
#         alert for alert in all_alerts 
#         if alert.severity == "critical" and alert.created_at >= cutoff_time
#     ]
    
#     return AlertListResponse(
#         alerts=[AlertResponse.model_validate(alert) for alert in critical_alerts],
#         total=len(critical_alerts),
#         skip=0,
#         limit=len(critical_alerts)
#     )

# @router.post("/{alert_id}/delivery-update", response_model=AlertResponse)
# async def update_alert_delivery(
#     alert_id: UUID,
#     delivery_data: AlertDeliveryUpdate,
#     alert = Depends(validate_alert_exists),
#     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# ):
#     """Update alert delivery status and attempts."""
#     update_data = DBAlertUpdate(
#         delivery_status=delivery_data.delivery_status.value,
#         delivery_attempts=delivery_data.delivery_details
#     )
    
#     updated_alert = await repo_factory.alert.update(alert, update_data)
#     return AlertResponse.model_validate(updated_alert)

# # @router.get("/statistics/overview", response_model=AlertStatistics)
# # async def get_alert_statistics(
# #     days: int = Query(30, description="Number of days for statistics"),
# #     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# # ):
# #     """Get alert statistics for the specified period."""
# #     from datetime import datetime, timedelta
    
# #     cutoff_time = datetime.utcnow() - timedelta(days=days)
# #     all_alerts = await repo_factory.alert.get_multi(limit=10000)
    
# #     # Filter alerts within the time period
# #     period_alerts = [alert for alert in all_alerts if alert.created_at >= cutoff_time]
    
# #     total_alerts = len(period_alerts)
# #     resolved_alerts = sum(1 for alert in period_alerts if alert.resolved)
# #     unresolved_alerts = total_alerts - resolved_alerts
    
# #     # Count by delivery status
# #     by_delivery_status = {}
# #     for alert in period_alerts:
# #         status = alert.delivery_status
# #         by_delivery_status[status] = by_delivery_status.get(status, 0) + 1
    
# #     # Count by severity
# #     by_severity = {}
# #     for alert in period_alerts:
# #         severity = alert.severity
# #         by_severity[severity] = by_severity.get(severity, 0) + 1
    
# #     # Count by type
# #     by_type = {}
# #     for alert in period_alerts:
# #         alert_type = alert.alert_type
# #         by_type[alert_type] = by_type.get(alert_type, 0) + 1
    
# #     return AlertStatistics(
# #         period_days=days,
# #         total_alerts=total_alerts,
# #         resolved_alerts=resolved_alerts,
# #         unresolved_alerts=unresolved_alerts,
# #         by_delivery_status=by_delivery_status,
# #         by_severity=by_severity,
# #         by_type=by_type
# #     )

# # @router.get("/delivery/performance", response_model=AlertDeliveryStats)
# # async def get_delivery_performance(
# #     days: int = Query(30, description="Number of days for statistics"),
# #     repo_factory: AsyncRepositoryFactory = Depends(get_repository_factory)
# # ):
#     # """Get alert delivery performance statistics."""
#     # from datetime import datetime, timedelta
    
#     # cutoff_time = datetime.utcnow() - timedelta(days=days)
#     # all_alerts = await repo_factory.alert.get_multi(limit=10000)
    
#     # # Filter alerts within the time period
#     # period_alerts = [alert for alert in all_alerts if alert.created_at >= cutoff_time]
    
#     # # Calculate performance by channel
#     # channel_stats = {}
    
#     # for alert in period_alerts:
#     #     for channel in alert.delivery_channels:
#     #         if channel not in channel_stats:
#     #             channel_stats[channel] = {
#     #                 "total_alerts": 0,
#     #                 "successful_deliveries": 0,
#     #                 "failed_deliveries": 0,
#     #                 "success_rate": 0
#     #             }
            
#     #         channel_stats[channel]["total_alerts"] += 1
            
#     #         if alert.delivery_status == "sent":
#     #             channel_stats[channel]["successful_deliveries"] += 1
#     #         elif alert.delivery_status == "failed":
#     #             channel_stats[channel]["failed_deliveries"] += 1
    
#     # # Calculate success rates
#     # for channel, stats in channel_stats.items():
#     #     if stats["total_alerts"] > 0:
#     #         stats["success_rate"] = (stats["successful_deliveries"] / stats["total_alerts"]) * 100
    
#     # return AlertDeliveryStats(
#     #     period_days=days,
#     #     channels=channel_stats
#     # )