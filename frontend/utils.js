function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split("; ") : [];
  for (const cookie of cookies) {
    const [key, ...val] = cookie.split("=");
    if (key === name) return decodeURIComponent(val.join("="));
  }
  return null;
}

let authToken = null;

async function getAuthToken() {
  if (authToken) return authToken;

  const res = await fetch("/rna/auth_token/");
  if (!res.ok) throw new Error(`Auth token request failed: ${res.status}`);
  const data = await res.json();

  if (!data.token) throw new Error("No token in response");
  authToken = data.token;
  return authToken;
}

export async function authPost(url, data, isPatch = false) {
  const token = await getAuthToken();

  const headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken"),
    Authorization: `Token ${token}`,
  };

  if (isPatch) {
    headers["X-HTTP-Method-Override"] = "PATCH";
  }

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: data,
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`Request failed: ${res.status} ${msg}`);
  }

  return res;
}
