import { useEffect, useMemo, useState } from "react";
import { useReplacementStore } from "../stores/ReplacementStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { createReplacementForm } from "../constructors/ReplacementConstructor";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import {
  ReplacementStatusText,
  REPLACEMENT_STAGES,
  DEVICE_SERVICE_STATUS_TEXT
} from "../constants/ReplacementStatus";
import { ERROR_MESSAGES } from "../constants/errorMessages";
import type { ReplacementForm, ReplacementOrder } from "../types/ReplacementOrder";
import { ReplacementFormPanel } from "../components/replacement/ReplacementFormPanel";
import { ReplacementOrderCard } from "../components/replacement/ReplacementOrderCard";
import { OperationLogTimeline } from "../components/replacement/OperationLogTimeline";

export function ReplacementPage() {
  const { orders, logs, loading, lastError, load, loadLogs, submit, takeover, supplement, resolve } =
    useReplacementStore();
  const deviceStore = useFireDeviceStore();
  const [form, setForm] = useState<ReplacementForm>(() => createReplacementForm());

  useEffect(() => {
    void load();
    void deviceStore.load();
    void loadLogs();
  }, [load, loadLogs, deviceStore]);

  // 未接管的旧设备（IN_SERVICE）才能发起更换。
  const selectableOldDevices = useMemo(
    () => deviceStore.rows.filter((d) => d.status === "IN_SERVICE"),
    [deviceStore.rows]
  );

  async function handleSubmit(next: ReplacementForm) {
    const order = await submit(next);
    // 冲突草稿会保留填写：不清空 client_token，化解或改挂后继续用同一单。
    if (order && order.status !== "CONFLICT") {
      setForm(createReplacementForm());
    }
  }

  async function handleTakeover(order: ReplacementOrder) {
    await takeover(order.id);
    void loadLogs();
  }

  async function handleSupplement(order: ReplacementOrder, code: string) {
    await supplement(order.id, { new_device_code: code });
    void loadLogs();
  }

  async function handleResolve(order: ReplacementOrder, next: Partial<ReplacementForm>) {
    await resolve(order.id, next);
  }

  const pendingReview = orders.filter((o) => o.status === "PENDING_REVIEW");
  const preoccupied = orders.filter((o) => o.status === "PRE_OCCUPIED");
  const conflict = orders.filter((o) => o.status === "CONFLICT");
  const done = orders.filter((o) => o.status === "TAKEN_OVER");

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect / handover ledger</p>
          <h1>设备报废更换交接账</h1>
          <p style={{ color: "#596257" }}>
            更换单先预占新设备，接管前旧设备继续担责；接管后仅转移未开始任务和未关闭隐患，
            旧巡检结果与已关闭隐患留档，二维码同一时刻只绑定一台设备。
          </p>
        </div>
        <StatusBadge value={loading ? "SYNCING" : "LEDGER_READY"} />
      </section>

      {lastError && (
        <section className="panel" style={{ borderColor: "#c0392b", background: "#fdf1ef" }}>
          <strong>{ERROR_MESSAGES[lastError.code as keyof typeof ERROR_MESSAGES] ?? lastError.message}</strong>
          {lastError.conflictOrder && (
            <p style={{ marginBottom: 0 }}>
              保留草稿单号：{lastError.conflictOrder.order_no}（冲突单 #{String(lastError.conflictOrder.conflict_with)}），
              可在下方“冲突待处理”改挂其他旧设备。
            </p>
          )}
        </section>
      )}

      <section className="metrics">
        <Stat label="待核旧记录" value={pendingReview.length} hint="补齐更换关系前不可接管" />
        <Stat label="预占中" value={preoccupied.length} hint="旧设备仍在担责" />
        <Stat label="更换冲突" value={conflict.length} hint="第二份提交已保留填写" />
      </section>

      <section className="workbench" style={{ gridTemplateColumns: "1fr" }}>
        <div className="panel wide">
          <h2>发起报废更换（先预占）</h2>
          <ReplacementFormPanel
            form={form}
            devices={selectableOldDevices}
            qrArchives={useReplacementStore.getState().qrArchives}
            onChange={setForm}
            onSubmit={handleSubmit}
          />
        </div>

        <OrderSection
          title="关系待核（旧记录缺少更换关系）"
          orders={pendingReview}
          allOrders={orders}
          devices={deviceStore.rows}
          onSupplement={handleSupplement}
        />
        <OrderSection
          title="已预占 · 待接管确认"
          orders={preoccupied}
          allOrders={orders}
          devices={deviceStore.rows}
          onTakeover={handleTakeover}
        />
        <OrderSection
          title="冲突待处理（另一份提交保留填写）"
          orders={conflict}
          allOrders={orders}
          devices={deviceStore.rows}
          selectableOldDevices={selectableOldDevices}
          onResolve={handleResolve}
        />
        <OrderSection title="已接管留档" orders={done} allOrders={orders} devices={deviceStore.rows} />
      </section>

      <section className="panel">
        <h2>设备实时状态</h2>
        <div className="table">
          {deviceStore.rows.map((d) => (
            <article className="row" key={d.id}>
              <strong>{d.device_code}</strong>
              <span>{d.location_desc}</span>
              <StatusBadge value={DEVICE_SERVICE_STATUS_TEXT[d.status] ?? d.status} />
            </article>
          ))}
        </div>
      </section>

      <OperationLogTimeline logs={logs} stages={REPLACEMENT_STAGES.map((s) => s.text)} />
    </main>
  );
}

function Stat({ label, value, hint }: { label: string; value: number; hint: string }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
      <small style={{ color: "#8a8578" }}>{hint}</small>
    </div>
  );
}

type SectionProps = {
  title: string;
  orders: ReplacementOrder[];
  allOrders: ReplacementOrder[];
  devices: { id: number; device_code: string; status: string }[];
  onTakeover?: (o: ReplacementOrder) => void;
  onSupplement?: (o: ReplacementOrder, code: string) => void;
  onResolve?: (o: ReplacementOrder, next: Partial<ReplacementForm>) => void;
  selectableOldDevices?: { id: number; device_code: string }[];
};

function OrderSection({ title, orders, allOrders, devices, ...actions }: SectionProps) {
  return (
    <div className="panel wide">
      <h2>
        {title} <span style={{ color: "#8a8578", fontWeight: 400 }}>{orders.length} 张</span>
      </h2>
      {orders.length === 0 ? (
        <EmptyState title="暂无此类更换单" />
      ) : (
        orders.map((o) => (
          <ReplacementOrderCard
            key={o.id}
            order={o}
            conflictOrder={allOrders.find((c) => c.id === o.conflict_with)}
            deviceLabel={(id) => devices.find((d) => d.id === id)?.device_code ?? `#${id}`}
            statusText={ReplacementStatusText}
            {...actions}
          />
        ))
      )}
    </div>
  );
}
