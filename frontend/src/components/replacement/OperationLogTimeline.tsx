import type { OperationLog } from "../../types/OperationLog";

export function OperationLogTimeline({ logs, stages }: { logs: OperationLog[]; stages: string[] }) {
  return (
    <section className="panel">
      <h2>操作日志（交接全过程留痕）</h2>
      <p style={{ color: "#8a8578" }}>阶段：{stages.join(" → ")}</p>
      {logs.length === 0 ? (
        <div className="empty">暂无日志</div>
      ) : (
        <ul className="log-timeline">
          {logs.map((log) => (
            <li key={log.id}>
              <time>{log.created_at}</time>
              <code>{log.action}</code>
              <span>{log.detail}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
