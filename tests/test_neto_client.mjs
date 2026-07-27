import assert from "node:assert/strict";
import test from "node:test";

import { NetoClient } from "../assets/neto-client.ts";

async function captureEndpoint(storeUrl) {
  let endpoint;
  const client = new NetoClient({
    storeUrl,
    auth: {
      type: "api-key",
      username: "test-user",
      apiKey: "test-key",
    },
    fetchImpl: async (input) => {
      endpoint = String(input);
      return new Response(JSON.stringify({ Item: [] }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    },
  });

  await client.request("GetItem", {
    Filter: {
      SKU: ["TEST-SKU"],
      OutputSelector: ["SKU"],
    },
  });

  return endpoint;
}

test("always constructs an HTTPS Neto endpoint", async () => {
  const cases = [
    ["store.example", "https://store.example/do/WS/NetoAPI"],
    ["http://store.example/old-path?query=1#fragment", "https://store.example/do/WS/NetoAPI"],
    ["https://store.example/old-path", "https://store.example/do/WS/NetoAPI"],
    ["javascript://store.example/unsafe", "https://store.example/do/WS/NetoAPI"],
  ];

  for (const [storeUrl, expectedEndpoint] of cases) {
    assert.equal(await captureEndpoint(storeUrl), expectedEndpoint);
  }
});
