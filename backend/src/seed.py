seed = {
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
      "device_code": "HQ-01-001",
      "device_type": "HYDRANT",
      "floor": "1F",
      "location_desc": "1 号楼大堂消火栓",
      "install_date": "2022-06-11T09:00:00Z",
      "status": "IN_SERVICE",
      "next_maintenance_at": "2026-06-11T09:00:00Z"
    },
    {
      "id": 2,
      "building_id": 2,
      "device_code": "SD-02-003",
      "device_type": "SMOKE_DETECTOR",
      "floor": "2F",
      "location_desc": "2 号楼走廊烟感",
      "install_date": "2022-06-12T09:00:00Z",
      "status": "IN_SERVICE",
      "next_maintenance_at": "2026-06-12T09:00:00Z"
    },
    {
      "id": 3,
      "building_id": 3,
      "device_code": "SP-03-005",
      "device_type": "SPRINKLER",
      "floor": "3F",
      "location_desc": "3 号楼机房喷淋",
      "install_date": "2022-06-13T09:00:00Z",
      "status": "IN_SERVICE",
      "next_maintenance_at": "2026-06-13T09:00:00Z"
    },
    {
      "id": 9,
      "building_id": 1,
      "device_code": "EX-OLD-009",
      "device_type": "EXTINGUISHER",
      "floor": "1F",
      "location_desc": "1 号楼配电房灭火器（已报废）",
      "install_date": "2018-03-01T09:00:00Z",
      "status": "SCRAPPED",
      "next_maintenance_at": "2020-03-01T09:00:00Z"
    }
  ],
  "inspectionTask": [
    {
      "id": 1,
      "building_id": 1,
      "inspector_id": 1,
      "device_id": 1,
      "plan_date": "2026-11-11T09:00:00Z",
      "task_type": "HYDRANT",
      "status": "PLANNED",
      "checklist_version": "checklist v3",
      "finished_at": ""
    },
    {
      "id": 2,
      "building_id": 1,
      "inspector_id": 1,
      "device_id": 1,
      "plan_date": "2026-09-12T09:00:00Z",
      "task_type": "HYDRANT",
      "status": "IN_PROGRESS",
      "checklist_version": "checklist v3",
      "finished_at": ""
    },
    {
      "id": 3,
      "building_id": 2,
      "inspector_id": 2,
      "device_id": 2,
      "plan_date": "2026-11-13T09:00:00Z",
      "task_type": "SMOKE_DETECTOR",
      "status": "PLANNED",
      "checklist_version": "checklist v3",
      "finished_at": ""
    }
  ],
  "inspectionResult": [
    {
      "id": 1,
      "task_id": 2,
      "device_id": 1,
      "item_code": "PRESSURE",
      "result_status": "IN_PROGRESS",
      "measured_value": "0.21MPa",
      "photo_url": "/mock/photo_url-1.png",
      "note": "旧设备历史巡检结果，接管后留档"
    },
    {
      "id": 2,
      "task_id": 3,
      "device_id": 2,
      "item_code": "SMOKE_TEST",
      "result_status": "SUBMITTED",
      "measured_value": "normal",
      "photo_url": "/mock/photo_url-2.png",
      "note": "note 2"
    }
  ],
  "hazardTicket": [
    {
      "id": 1,
      "result_id": 1,
      "device_id": 1,
      "severity": "HIGH",
      "owner_id": 1,
      "deadline": "2026-11-01T09:00:00Z",
      "rectify_status": "OPEN",
      "rectify_note": "未关闭隐患，接管时应转给新设备",
      "closed_at": ""
    },
    {
      "id": 2,
      "result_id": 2,
      "device_id": 2,
      "severity": "LOW",
      "owner_id": 2,
      "deadline": "2026-08-01T09:00:00Z",
      "rectify_status": "CLOSED",
      "rectify_note": "已关闭隐患，接管时留在旧设备档案",
      "closed_at": "2026-08-05T09:00:00Z"
    }
  ],
  "qrArchive": [
    {
      "id": 1,
      "qr_code": "QR-0001",
      "device_id": 1,
      "bound_at": "2022-06-11T09:00:00Z",
      "binding_history": [
        {"device_id": 1, "bound_at": "2022-06-11T09:00:00Z"}
      ]
    },
    {
      "id": 2,
      "qr_code": "QR-0002",
      "device_id": 2,
      "bound_at": "2022-06-12T09:00:00Z",
      "binding_history": [
        {"device_id": 2, "bound_at": "2022-06-12T09:00:00Z"}
      ]
    },
    {
      "id": 3,
      "qr_code": "QR-0003",
      "device_id": 3,
      "bound_at": "2022-06-13T09:00:00Z",
      "binding_history": [
        {"device_id": 3, "bound_at": "2022-06-13T09:00:00Z"}
      ]
    }
  ],
  "replacementOrder": [
    {
      "id": 900,
      "order_no": "RP-2026-0900",
      "old_device_id": 9,
      "new_device_id": None,
      "new_device_code": "",
      "qr_code": "",
      "status": "PENDING_REVIEW",
      "reason": "旧记录缺少更换关系，待核",
      "client_token": "legacy-900",
      "staged_steps": [],
      "conflict_with": None,
      "transferred_task_ids": [],
      "transferred_hazard_ids": [],
      "created_at": "2026-09-01T09:00:00Z",
      "preoccupied_at": "",
      "taken_over_at": ""
    }
  ],
  "operationLog": [
    {
      "id": 1,
      "actor": "system",
      "action": "ReplacementOrder.seed",
      "order_id": 900,
      "target_type": "FireDevice",
      "target_id": "9",
      "detail": "旧报废设备缺少更换关系，登记待核",
      "created_at": "2026-09-01T09:00:00Z"
    }
  ]
}
