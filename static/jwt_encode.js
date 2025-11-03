function base64url(input) {
  return btoa(input).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

// Convert UTF-8 string to Uint8Array
function toUint8Array(str) {
  return new TextEncoder().encode(str);
}

// HMAC SHA-256 using Web Crypto API
async function hmacSha256(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    toUint8Array(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    toUint8Array(message)
  );
  return btoa(String.fromCharCode(...new Uint8Array(signature)))
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

async function jwtEncode(payload, secret) {
  const header = {
    alg: "HS256",
    typ: "JWT",
  };

  const now = Math.floor(Date.now() / 1000);
  payload.exp = now + 60 * 60; // 1 hour expiry

  const headerB64 = base64url(JSON.stringify(header));
  const payloadB64 = base64url(JSON.stringify(payload));
  const unsignedToken = `${headerB64}.${payloadB64}`;
  const signature = await hmacSha256(secret, unsignedToken);
  return `${unsignedToken}.${signature}`;
}
