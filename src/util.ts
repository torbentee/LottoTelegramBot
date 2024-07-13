export function toBeautyString(obj: unknown) {
  return JSON.stringify(obj, null, "\t");
}

export function hasMessageParameter(message: string, command: string) {
  return !(message.replace(`/${command}`, "") === "");
}

export function getMessageparameter(message: string, command: string) {
  return message.replace(`/${command} `, "");
}
