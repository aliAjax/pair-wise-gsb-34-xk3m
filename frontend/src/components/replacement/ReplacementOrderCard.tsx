import { useState } from "react";
import type { ReplacementOrder, ReplacementForm } from "../../types/ReplacementOrder";
import { REPLACEMENT_STAGES } from "../../constants/ReplacementStatus";

type Props = {
  order: ReplacementOrder;
  conflictOrder?: ReplacementOrder;
  deviceLabel: (id: number) => string;
  statusText: Record<string, string>;
  onTakeover?: (o: ReplacementOrder) => void;
  onSupplement?: (o: ReplacementOrder, code: string) => void;
  onResolve?: (o: ReplacementOrder, next: Partial<ReplacementForm>) => void;
  selectableOldDevices?: { id: number; device_code: string }[];
};

export function ReplacementOrderCard({
  order,
  conflictOrder,
  deviceLabel,
  statusText,
  onTakeover,
  onSupplement,
  onResolve,
  selectableOldDevices = []
}: Props) {
  const [newCode, setNewCode] = useState(order.new_device_code);
  const [retargetId, setRetargetId] = useState(0);

  return (
    <article className={`order-card status-${order.status.toLowerCase()}`}>
      <header>
        <div>
          <strong>{order.order_no}</strong>
          <span className="order-state">{statusText[order.status] ?? order.status}</span>
        </div>
        <div className="devices">
          旧设备 <b>{deviceLabel(order.old_device_id)}</b>
          {" → "}
          新设备{" "}
          <b>{order.new_device_id ? deviceLabel(order.new_device_id) : order.new_device_code || "待登记"}</b>
        </div>
      </header>

      <ol className="stages">
        {REPLACEMENT_STAGES.map((s) => {
          const done = order.staged_steps.includes(s.stage);
          return (
            <li key={s.stage} className={done ? "done" : "todo"}>
              {done ? "✓" : "○"} {s.text}
            </li>
          );
        })}
      </ol>

      {order.status === "CONFLICT" && (
        <div className="conflict-box">
          <p>
            本单与 <b>{conflictOrder?.order_no ?? `#${order.conflict_with}`}</b>{" "}
            冲突：对方已对同一旧设备完成更换。填写内容已保留，可改挂其他旧设备后重新预占。
          </p>
          <select value={retargetId} onChange={(e) => setRetargetId(Number(e.target.value))}>
            <option value={0}>选择改挂的旧设备</option>
            {selectableOldDevices
              .filter((d) => d.id !== order.old_device_id)
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.device_code}
                </option>
              ))}
          </select>
          <button
            type="button"
            className="primary"
            disabled={retargetId === 0}
            onClick={() => onResolve?.(order, { old_device_id: retargetId })}
          >
            化解冲突并重新预占
          </button>
        </div>
      )}

      {order.status === "PENDING_REVIEW" && (
        <div className="pending-box">
          <p>{order.reason || "旧记录缺少更换关系"}。补齐新设备编号前不能确认接管。</p>
          <input
            value={newCode}
            placeholder="补齐新设备编号"
            onChange={(e) => setNewCode(e.target.value)}
          />
          <button
            type="button"
            className="primary"
            disabled={!newCode.trim()}
            onClick={() => onSupplement?.(order, newCode.trim())}
          >
            补齐更换关系
          </button>
        </div>
      )}

      {order.status === "PRE_OCCUPIED" && (
        <div className="preoccupy-box">
          <p>新设备已预占，旧设备仍在担责。确认后：未开始任务/未关闭隐患转新设备，二维码切换。</p>
          <button type="button" className="primary" onClick={() => onTakeover?.(order)}>
            确认接管
          </button>
        </div>
      )}

      {order.status === "TAKEN_OVER" && (
        <dl className="takeover-detail">
          <dt>转移的未开始任务</dt>
          <dd>{order.transferred_task_ids.length ? order.transferred_task_ids.join(", ") : "无"}</dd>
          <dt>转移的未关闭隐患</dt>
          <dd>{order.transferred_hazard_ids.length ? order.transferred_hazard_ids.join(", ") : "无"}</dd>
          <dt>接管时间</dt>
          <dd>{order.taken_over_at}</dd>
        </dl>
      )}
    </article>
  );
}
