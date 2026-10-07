import type { ReplacementForm } from "../../types/ReplacementOrder";
import type { QrArchive } from "../../types/QrArchive";

type DeviceOption = { id: number; device_code: string; floor: string; location_desc: string };

type Props = {
  form: ReplacementForm;
  devices: DeviceOption[];
  qrArchives: QrArchive[];
  onChange: (form: ReplacementForm) => void;
  onSubmit: (form: ReplacementForm) => void;
};

export function ReplacementFormPanel({ form, devices, qrArchives, onChange, onSubmit }: Props) {
  const oldDevice = devices.find((d) => d.id === Number(form.old_device_id));
  const currentQr = qrArchives.find((q) => q.device_id === Number(form.old_device_id));

  function update<K extends keyof ReplacementForm>(key: K, value: ReplacementForm[K]) {
    onChange({ ...form, [key]: value });
  }

  function pickOldDevice(id: number) {
    const device = devices.find((d) => d.id === id);
    const qr = qrArchives.find((q) => q.device_id === id);
    onChange({
      ...form,
      old_device_id: id,
      qr_code: qr?.qr_code ?? "",
      building_id: form.building_id,
      floor: device?.floor ?? form.floor,
      location_desc: device?.location_desc ?? form.location_desc
    });
  }

  return (
    <form
      className="replacement-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      <label>
        旧设备（接管前继续担责）
        <select
          required
          value={form.old_device_id}
          onChange={(e) => pickOldDevice(Number(e.target.value))}
        >
          <option value={0}>请选择在用设备</option>
          {devices.map((d) => (
            <option key={d.id} value={d.id}>
              {d.device_code} · {d.location_desc}
            </option>
          ))}
        </select>
      </label>
      <label>
        新设备编号（先登记并预占）
        <input
          required
          value={form.new_device_code}
          placeholder="例如 HQ-01-001-N"
          onChange={(e) => update("new_device_code", e.target.value)}
        />
      </label>
      <label>
        二维码（接管时切换，同一时刻只绑一台）
        <input
          value={form.qr_code}
          placeholder={currentQr ? currentQr.qr_code : "留空表示新贴码"}
          onChange={(e) => update("qr_code", e.target.value)}
        />
        {oldDevice && (
          <small>
            旧设备当前二维码：{currentQr ? currentQr.qr_code : "未建档，接管时将新建绑定"}
          </small>
        )}
      </label>
      <label>
        更换原因
        <input value={form.reason} onChange={(e) => update("reason", e.target.value)} />
      </label>
      <div className="form-actions">
        <button type="submit" className="primary">
          提交更换单（预占新设备）
        </button>
        <small>
          终端令牌 <code>{form.client_token.slice(0, 18)}…</code>
          ，写入中断后凭它续作，不重复登记。
        </small>
      </div>
    </form>
  );
}
