import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getToken, setToken, removeToken, authAPI, menuAPI } from "./api";

describe("token helpers", () => {
  afterEach(() => localStorage.clear());

  it("setToken stores the token in localStorage", () => {
    setToken("my-token");
    expect(localStorage.getItem("access_token")).toBe("my-token");
  });

  it("getToken retrieves the stored token", () => {
    localStorage.setItem("access_token", "stored-token");
    expect(getToken()).toBe("stored-token");
  });

  it("getToken returns null when no token is stored", () => {
    expect(getToken()).toBeNull();
  });

  it("removeToken deletes the token from localStorage", () => {
    localStorage.setItem("access_token", "to-remove");
    removeToken();
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});

describe("apiRequest error handling", () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("throws an error with the backend error message on non-ok response", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ error: "Invalid credentials" }),
    } as Response);

    await expect(authAPI.login("bad@rvu.edu.in", "wrong")).rejects.toThrow("Invalid credentials");
  });

  it("attaches status code to thrown error", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ error: "Validation failed" }),
    } as Response);

    const err = await authAPI.login("x@rvu.edu.in", "y").catch((e) => e);
    expect(err.status).toBe(422);
  });

  it("attaches retry_after to rate-limit errors", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({ error: "Too many requests", retry_after: 60 }),
    } as Response);

    const err = await authAPI.login("x@rvu.edu.in", "y").catch((e) => e);
    expect(err.retry_after).toBe(60);
  });

  it("falls back to generic message when backend returns no error field", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    } as Response);

    await expect(menuAPI.getAllFoods()).rejects.toThrow("API request failed");
  });

  it("sends Authorization header when token is present", async () => {
    localStorage.setItem("access_token", "bearer-tok");
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ foods: [] }),
    } as Response);

    await menuAPI.getAllFoods();

    const [, options] = vi.mocked(global.fetch).mock.calls[0];
    const headers = options?.headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer bearer-tok");
  });

  it("omits Authorization header when no token is stored", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ foods: [] }),
    } as Response);

    await menuAPI.getAllFoods();

    const [, options] = vi.mocked(global.fetch).mock.calls[0];
    const headers = options?.headers as Record<string, string>;
    expect(headers["Authorization"]).toBeUndefined();
  });
});
