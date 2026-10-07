import { useEffect, useState } from "react";
import { useDeviceReplacementStore } from "../stores/DeviceReplacementStore";
import type { DeviceReplacementPayload } from "../types/DeviceReplacement";

export function useReplacementHandover() {
  const { rows, loading, error, load, submit, confirm, backfill } = useDeviceReplacementStore();
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    void load();
  }, [load]);

  const submitForm = async (payload: DeviceReplacementPayload) => {
    setNotice(null);
    await submit(payload);
    setNotice("更换单已提交并预占新设备，确认接管前旧设备继续担责");
  };
  const confirmOrder = async (id: number) => {
    setNotice(null);
    await confirm(id);
    setNotice("接管确认完成：未开始任务与未关闭隐患已转交新设备，二维码已换绑");
  };
  const backfillOrder = async (id: number) => {
    setNotice(null);
    await backfill(id);
    setNotice("更换关系已补齐，可以确认接管");
  };

  return { rows, loading, error, notice, submitForm, confirmOrder, backfillOrder };
}
