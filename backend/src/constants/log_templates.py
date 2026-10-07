LOG_TEMPLATES = {
  "Building": [
    "Building.create",
    "Building.update",
    "Building.status",
    "Building.export"
  ],
  "FireDevice": [
    "FireDevice.create",
    "FireDevice.update",
    "FireDevice.status",
    "FireDevice.export"
  ],
  "InspectionTask": [
    "InspectionTask.create",
    "InspectionTask.update",
    "InspectionTask.status",
    "InspectionTask.export",
    "InspectionTask.transfer"
  ],
  "InspectionResult": [
    "InspectionResult.create",
    "InspectionResult.update",
    "InspectionResult.status",
    "InspectionResult.export",
    "InspectionResult.archive"
  ],
  "HazardTicket": [
    "HazardTicket.create",
    "HazardTicket.update",
    "HazardTicket.status",
    "HazardTicket.export",
    "HazardTicket.transfer",
    "HazardTicket.archive_closed"
  ],
  "ReplacementOrder": [
    "ReplacementOrder.submit",
    "ReplacementOrder.resume",
    "ReplacementOrder.conflict",
    "ReplacementOrder.supplement_relation",
    "ReplacementOrder.takeover",
    "ReplacementOrder.pending_review",
    "ReplacementOrder.qr_switch"
  ],
  "QrArchive": [
    "QrArchive.bind",
    "QrArchive.pre_bind",
    "QrArchive.rebind"
  ]
}
