export type NetoAction =
  | "GetItem"
  | "AddItem"
  | "UpdateItem"
  | "GetContent"
  | "AddContent"
  | "UpdateContent";

export interface NetoApiKeyAuth {
  type: "api-key";
  username: string;
  apiKey: string;
}

export interface NetoMessage {
  Message?: string;
  SeverityCode?: string;
  Description?: string;
}

export interface NetoMessages {
  Error?: NetoMessage | NetoMessage[];
  Warning?: NetoMessage | NetoMessage[];
}

export interface NetoResponseBase {
  Messages?: NetoMessages;
  [key: string]: unknown;
}

export class NetoApiError extends Error {
  public readonly action: NetoAction;
  public readonly status?: number;
  public readonly messages: NetoMessage[];

  public constructor(options: {
    action: NetoAction;
    message: string;
    status?: number;
    messages?: NetoMessage[];
    cause?: unknown;
  }) {
    super(options.message, { cause: options.cause });
    this.name = "NetoApiError";
    this.action = options.action;
    this.status = options.status;
    this.messages = options.messages ?? [];
  }
}

export interface NetoClientOptions {
  storeUrl: string;
  auth: NetoApiKeyAuth;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
  maxRetries?: number;
}

function asArray<T>(value: T | T[] | null | undefined): T[] {
  if (value == null) return [];
  return Array.isArray(value) ? value : [value];
}

function buildEndpoint(storeUrl: string): string {
  const url = new URL(storeUrl.includes("://") ? storeUrl : `https://${storeUrl}`);
  url.pathname = "/do/WS/NetoAPI";
  url.search = "";
  url.hash = "";
  return url.toString();
}

function getMessageText(message: NetoMessage): string {
  return message.Description || message.Message || "Unknown Neto API error";
}

function parseRetryAfter(response: Response): number | null {
  const value = response.headers.get("retry-after");
  if (!value) return null;

  const seconds = Number(value);
  if (Number.isFinite(seconds)) return Math.max(0, seconds * 1000);

  const dateMs = Date.parse(value);
  return Number.isFinite(dateMs) ? Math.max(0, dateMs - Date.now()) : null;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class NetoClient {
  private readonly endpoint: string;
  private readonly auth: NetoApiKeyAuth;
  private readonly fetchImpl: typeof fetch;
  private readonly timeoutMs: number;
  private readonly maxRetries: number;

  public constructor(options: NetoClientOptions) {
    this.endpoint = buildEndpoint(options.storeUrl);
    this.auth = options.auth;
    this.fetchImpl = options.fetchImpl ?? fetch;
    this.timeoutMs = options.timeoutMs ?? 30_000;
    this.maxRetries = options.maxRetries ?? 3;
  }

  public async request<T extends NetoResponseBase>(
    action: NetoAction,
    payload: unknown,
    options: { retryMutations?: boolean } = {},
  ): Promise<{ data: T; warnings: NetoMessage[] }> {
    const isRead = action === "GetItem" || action === "GetContent";
    const allowRetry = isRead || options.retryMutations === true;

    for (let attempt = 0; ; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

      try {
        const response = await this.fetchImpl(this.endpoint, {
          method: "POST",
          headers: this.buildHeaders(action),
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        const retryableStatus =
          response.status === 429 ||
          response.status === 408 ||
          response.status === 502 ||
          response.status === 503 ||
          response.status === 504;

        if (!response.ok) {
          if (allowRetry && retryableStatus && attempt < this.maxRetries) {
            const retryAfter = parseRetryAfter(response);
            const backoff = retryAfter ?? Math.min(10_000, 500 * 2 ** attempt + Math.random() * 250);
            await sleep(backoff);
            continue;
          }

          throw new NetoApiError({
            action,
            status: response.status,
            message: `Neto API request failed with HTTP ${response.status}`,
          });
        }

        const data = (await response.json()) as T;
        const errors = asArray(data.Messages?.Error);
        const warnings = asArray(data.Messages?.Warning);

        if (errors.length > 0) {
          throw new NetoApiError({
            action,
            status: response.status,
            messages: errors,
            message: errors.map(getMessageText).join("; "),
          });
        }

        return { data, warnings };
      } catch (error) {
        if (error instanceof NetoApiError) throw error;

        if (allowRetry && attempt < this.maxRetries) {
          await sleep(Math.min(10_000, 500 * 2 ** attempt + Math.random() * 250));
          continue;
        }

        throw new NetoApiError({
          action,
          message: error instanceof Error ? error.message : "Neto API network failure",
          cause: error,
        });
      } finally {
        clearTimeout(timeout);
      }
    }
  }

  private buildHeaders(action: NetoAction): Record<string, string> {
    const headers: Record<string, string> = {
      Accept: "application/json",
      "Content-Type": "application/json",
      NETOAPI_ACTION: action,
    };

    headers.NETOAPI_USERNAME = this.auth.username;
    headers.NETOAPI_KEY = this.auth.apiKey;

    return headers;
  }
}
