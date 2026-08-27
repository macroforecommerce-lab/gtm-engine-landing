import crypto from "node:crypto";

const SESSION_COOKIE = "shopify_session";
const STATE_COOKIE = "shopify_oauth_state";

function getKey() {
  const secret = process.env.SESSION_SECRET;
  if (!secret) {
    throw new Error("SESSION_SECRET environment variable is not set");
  }
  return crypto.createHash("sha256").update(secret).digest();
}

export function encryptSession(payload) {
  const key = getKey();
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const json = JSON.stringify(payload);
  const encrypted = Buffer.concat([cipher.update(json, "utf8"), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return Buffer.concat([iv, authTag, encrypted]).toString("base64url");
}

export function decryptSession(token) {
  try {
    const key = getKey();
    const raw = Buffer.from(token, "base64url");
    const iv = raw.subarray(0, 12);
    const authTag = raw.subarray(12, 28);
    const encrypted = raw.subarray(28);
    const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
    decipher.setAuthTag(authTag);
    const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()]);
    return JSON.parse(decrypted.toString("utf8"));
  } catch {
    return null;
  }
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const part of header.split(";")) {
    const idx = part.indexOf("=");
    if (idx === -1) continue;
    const name = part.slice(0, idx).trim();
    const value = part.slice(idx + 1).trim();
    cookies[name] = decodeURIComponent(value);
  }
  return cookies;
}

export function readCookies(req) {
  return parseCookies(req.headers.cookie);
}

export function serializeCookie(name, value, { maxAge, httpOnly = true } = {}) {
  const parts = [`${name}=${encodeURIComponent(value)}`];
  parts.push("Path=/");
  if (httpOnly) parts.push("HttpOnly");
  parts.push("Secure");
  parts.push("SameSite=Lax");
  if (maxAge !== undefined) parts.push(`Max-Age=${maxAge}`);
  return parts.join("; ");
}

export function clearCookie(name) {
  return serializeCookie(name, "", { maxAge: 0 });
}

export const SESSION_COOKIE_NAME = SESSION_COOKIE;
export const STATE_COOKIE_NAME = STATE_COOKIE;
