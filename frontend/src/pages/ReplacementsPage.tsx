import { useEffect, useState } from "react";
import { useReplacementHandover } from "../hooks/useReplacementHandover";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { StatusBadge } from "../components/common/StatusBadge";
import { StatCard } from "../components/common/StatCard";
import { EmptyState } from "../components/common/EmptyState";
import { ReplacementStatusText } from "../constants/ReplacementStatus";
import type { ReplacementStatus } from "../types/ReplacementStatus";
import { formatDate, formatHandoverStep, formatQrBinding } from "../utils/formatters";

export function ReplacementsPage() {
  const { rows, loading, error, notice, submitForm, confirmOrder, backfillOrder } = useReplacementHandover();
  const { rows: devices, load: loadDevices } = useFireDeviceStore();
  const [oldDeviceId, setOldDeviceId] = useState(1);
  const [reason, setReason] = useState("灭火器药剂到期报废更换");
  // 表单号在重试期间保持不变：写入中断后用同一 request_id 续作，不重复登记新设备
  const [requestId, setRequestId] = useState(() => `REQ-${Date.now()}`);

  useEffect(() => {
    void loadDevices();
  }, [loadDevices]);

  const count = (status: string) => rows.filter((row) => row.status === status).length;
  const confirmThenRefresh = async (id: number) => {
    await confirmOrder(id);
    await loadDevices();
  };

  return <main className="page">
    <section className="page-head">
      <div>
        <p className="eyebrow">fire-inspect</p>
        <h1>报废更换交接账</h1>
      </div>
      <StatusBadge value="HANDOVER_LEDGER" />
    </section>

    <section className="metrics four">
      <StatCard label="已预占" value={count("PREOCCUPIED")} />
      <StatCard label="待核" value={count("PENDING_REVIEW")} />
      <StatCard label="已接管" value={count("CONFIRMED")} />
      <StatCard label="冲突" value={count("CONFLICT")} />
    </section>

    {error && <div className="error-banner">{error}</div>}
    {notice && !error && <div className="notice-banner">{notice}</div>}

    <section className="workbench">
      <div className="panel wide">
        <h2>更换单</h2>
        {rows.length === 0 && <EmptyState title="暂无更换单" />}
        <div className="table">
          {rows.map((row) => <article key={row.id} className="row replacement-row">
            <div>
              <strong>#{row.id} {row.request_id}</strong>
              <div className="hint">旧设备 #{row.old_device_id} → 新设备 {row.new_device_id ?? "待登记"} · {row.reason}</div>
              <div className="steps">{row.steps_done.map((step) => <span key={step} className="step-chip">{formatHandoverStep(step)}</span>)}</div>
              {row.pending_record_ids.length > 0 && <div className="hint">待核记录：{row.pending_record_ids.join("、")}（补齐前不能确认接管）</div>}
              {row.status === "CONFLICT" && <div className="hint">与更换单 #{row.conflict_with} 冲突，填写内容已保留</div>}
              {row.confirmed_at && <div className="hint">接管时间：{formatDate(row.confirmed_at)}</div>}
            </div>
            <StatusBadge value={row.status} />
            <span>{ReplacementStatusText[row.status as ReplacementStatus] ?? row.status}</span>
            <div className="form-row">
              {row.status === "PREOCCUPIED" && <button className="action-btn" disabled={loading} onClick={() => void confirmThenRefresh(row.id)}>确认接管</button>}
              {row.status === "PENDING_REVIEW" && <button className="action-btn" disabled={loading} onClick={() => void backfillOrder(row.id)}>补齐更换关系</button>}
            </div>
          </article>)}
        </div>
      </div>

      <div className="panel">
        <h2>提交更换单（预占新设备）</h2>
        <div className="form-row">
          <label>旧设备
            <select value={oldDeviceId} onChange={(event) => setOldDeviceId(Number(event.target.value))}>
              {devices.filter((device) => device.status === "ACTIVE").map((device) => <option key={device.id} value={device.id}>{device.device_code}</option>)}
            </select>
          </label>
          <label>报废原因
            <input value={reason} onChange={(event) => setReason(event.target.value)} />
          </label>
        </div>
        <div className="form-row">
          <button className="action-btn" disabled={loading} onClick={() => void submitForm({ request_id: requestId, old_device_id: oldDeviceId, reason })}>提交并预占</button>
          <button onClick={() => setRequestId(`REQ-${Date.now()}`)}>新表单</button>
        </div>
        <p className="hint">当前表单号 {requestId}：两台终端同时提交同一旧设备时，先完成接管者生效，另一单保留填写并标冲突。</p>
      </div>
    </section>

    <section className="panel">
      <h2>设备二维码绑定（同一时刻只绑定一台设备）</h2>
      <div className="table">
        {devices.map((device) => <article key={device.id} className="row">
          <strong>{device.device_code}</strong>
          <StatusBadge value={device.status} />
          <span>{formatQrBinding(device.qr_code)}</span>
        </article>)}
      </div>
    </section>
  </main>;
}
