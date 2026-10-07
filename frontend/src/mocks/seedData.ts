export const mockData = {
  "building": [
    {
      "id": 1,
      "name": "name 1",
      "campus": "campus 1",
      "floor_count": "floor count 1",
      "fire_grade": "fire grade 1",
      "manager_id": 1,
      "address_code": "address code 1"
    },
    {
      "id": 2,
      "name": "name 2",
      "campus": "campus 2",
      "floor_count": "floor count 2",
      "fire_grade": "fire grade 2",
      "manager_id": 2,
      "address_code": "address code 2"
    },
    {
      "id": 3,
      "name": "name 3",
      "campus": "campus 3",
      "floor_count": "floor count 3",
      "fire_grade": "fire grade 3",
      "manager_id": 3,
      "address_code": "address code 3"
    }
  ],
  "fireDevice": [
    {
      "id": 1,
      "building_id": 1,
      "device_code": "FE-1F-001",
      "device_type": "EXTINGUISHER",
      "floor": "1F",
      "location_desc": "一层东侧走廊",
      "install_date": "2024-01-15T09:00:00Z",
      "status": "ACTIVE",
      "next_maintenance_at": "2026-11-01T09:00:00Z",
      "qr_code": "QR-FE-001"
    },
    {
      "id": 2,
      "building_id": 2,
      "device_code": "HY-2F-002",
      "device_type": "HYDRANT",
      "floor": "2F",
      "location_desc": "二层楼梯间",
      "install_date": "2024-03-10T09:00:00Z",
      "status": "ACTIVE",
      "next_maintenance_at": "2026-10-20T09:00:00Z",
      "qr_code": "QR-HY-002"
    },
    {
      "id": 3,
      "building_id": 3,
      "device_code": "SD-3F-003",
      "device_type": "SMOKE_DETECTOR",
      "floor": "3F",
      "location_desc": "三层机房门口",
      "install_date": "2024-05-08T09:00:00Z",
      "status": "ACTIVE",
      "next_maintenance_at": "2026-12-05T09:00:00Z",
      "qr_code": "QR-SD-003"
    },
    {
      "id": 4,
      "building_id": 1,
      "device_code": "FE-1F-001-R1",
      "device_type": "EXTINGUISHER",
      "floor": "1F",
      "location_desc": "一层东侧走廊",
      "install_date": "2026-10-06T09:00:00Z",
      "status": "PREOCCUPIED",
      "next_maintenance_at": "2027-10-01T09:00:00Z",
      "qr_code": null
    }
  ],
  "inspectionTask": [
    {
      "id": 1,
      "building_id": 1,
      "inspector_id": 1,
      "plan_date": "2026-10-15T09:00:00Z",
      "task_type": "EXTINGUISHER",
      "status": "PLANNED",
      "checklist_version": "v2026.09",
      "finished_at": "",
      "device_id": 1,
      "replacement_id": null
    },
    {
      "id": 2,
      "building_id": 1,
      "inspector_id": 1,
      "plan_date": "2026-10-22T09:00:00Z",
      "task_type": "EXTINGUISHER",
      "status": "PLANNED",
      "checklist_version": "v2026.09",
      "finished_at": "",
      "device_id": 1,
      "replacement_id": 1
    },
    {
      "id": 3,
      "building_id": 1,
      "inspector_id": 2,
      "plan_date": "2026-09-11T09:00:00Z",
      "task_type": "EXTINGUISHER",
      "status": "REVIEWED",
      "checklist_version": "v2026.08",
      "finished_at": "2026-09-11T10:30:00Z",
      "device_id": 1,
      "replacement_id": null
    },
    {
      "id": 4,
      "building_id": 2,
      "inspector_id": 2,
      "plan_date": "2026-10-12T09:00:00Z",
      "task_type": "HYDRANT",
      "status": "IN_PROGRESS",
      "checklist_version": "v2026.09",
      "finished_at": "",
      "device_id": 2,
      "replacement_id": null
    },
    {
      "id": 5,
      "building_id": 3,
      "inspector_id": 3,
      "plan_date": "2026-10-18T09:00:00Z",
      "task_type": "SMOKE_DETECTOR",
      "status": "PLANNED",
      "checklist_version": "v2026.09",
      "finished_at": "",
      "device_id": 3,
      "replacement_id": null
    }
  ],
  "inspectionResult": [
    {
      "id": 1,
      "task_id": 3,
      "device_id": 1,
      "item_code": "PRESSURE",
      "result_status": "NORMAL",
      "measured_value": "1.2MPa",
      "photo_url": "/mock/photo_url-1.png",
      "note": "压力正常"
    },
    {
      "id": 2,
      "task_id": 3,
      "device_id": 1,
      "item_code": "EXPIRY_DATE",
      "result_status": "ABNORMAL",
      "measured_value": "已过期",
      "photo_url": "/mock/photo_url-2.png",
      "note": "药剂到期，建议报废更换"
    },
    {
      "id": 3,
      "task_id": 4,
      "device_id": 2,
      "item_code": "WATER_PRESSURE",
      "result_status": "NORMAL",
      "measured_value": "0.4MPa",
      "photo_url": "/mock/photo_url-3.png",
      "note": "水压正常"
    }
  ],
  "hazardTicket": [
    {
      "id": 1,
      "result_id": 2,
      "severity": "HIGH",
      "owner_id": 1,
      "deadline": "2026-10-30T09:00:00Z",
      "rectify_status": "OPEN",
      "rectify_note": "等待新灭火器到位",
      "closed_at": "",
      "device_id": 1,
      "replacement_id": 1
    },
    {
      "id": 2,
      "result_id": 2,
      "severity": "MEDIUM",
      "owner_id": 2,
      "deadline": "2026-09-30T09:00:00Z",
      "rectify_status": "CLOSED",
      "rectify_note": "已补充检查记录",
      "closed_at": "2026-09-20T09:00:00Z",
      "device_id": 1,
      "replacement_id": null
    },
    {
      "id": 3,
      "result_id": 3,
      "severity": "LOW",
      "owner_id": 3,
      "deadline": "2026-11-15T09:00:00Z",
      "rectify_status": "OPEN",
      "rectify_note": "观察中",
      "closed_at": "",
      "device_id": 2,
      "replacement_id": null
    }
  ],
  "deviceReplacement": [
    {
      "id": 1,
      "request_id": "REQ-20261006-A01",
      "old_device_id": 1,
      "new_device_id": 4,
      "status": "PREOCCUPIED",
      "reason": "灭火器药剂到期报废更换",
      "operator_id": 1,
      "qr_code": "QR-FE-001",
      "created_at": "2026-10-06T09:00:00Z",
      "confirmed_at": null,
      "conflict_with": null,
      "steps_done": ["REGISTER_NEW_DEVICE", "LINK_OPEN_RECORDS"],
      "pending_record_ids": []
    }
  ],
  "auditLog": [] as { id: number; actor: string; action: string; target_type: string; target_id: string; detail: string; created_at: string }[]
} as const;
