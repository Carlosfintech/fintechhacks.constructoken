import { tokenParser } from "./generic"

function tokenIsTOTP(token: string) {
  // https://stackoverflow.com/a/60758392/295606
  // https://stackoverflow.com/a/71953677/295606
  const obj = tokenParser(token)
  if (obj.hasOwnProperty("totp")) return obj.totp
  else return false
}

function tokenIsMagic(token: string) {
  // https://stackoverflow.com/a/60758392/295606
  // https://stackoverflow.com/a/71953677/295606
  const obj = tokenParser(token)
  return obj.hasOwnProperty("fingerprint")
}

export { tokenIsTOTP, tokenIsMagic }
