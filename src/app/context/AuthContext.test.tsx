import { render, screen, act, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider, useAuth } from "./AuthContext";

vi.mock("../services/api", () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    verifyOtp: vi.fn(),
    getCurrentUser: vi.fn(),
    logout: vi.fn(),
    updateProfile: vi.fn(),
  },
  getToken: vi.fn(),
  setToken: vi.fn(),
  removeToken: vi.fn(),
  API_BASE_URL: "http://localhost:5000/api",
}));

vi.mock("../services/socket", () => ({ disconnectSocket: vi.fn() }));

import { authAPI, getToken, setToken, removeToken } from "../services/api";

function TestConsumer() {
  const { isLoggedIn, user, login, logout, register } = useAuth();
  return (
    <div>
      <span data-testid="logged-in">{String(isLoggedIn)}</span>
      <span data-testid="user-name">{user?.name ?? "none"}</span>
      <button onClick={() => login("a@rvu.edu.in", "pass123")}>Login</button>
      <button onClick={() => logout()}>Logout</button>
      <button onClick={() => register("New User", "new@rvu.edu.in", "pass123")}>Register</button>
    </div>
  );
}

function renderWithAuth() {
  return render(
    <AuthProvider>
      <TestConsumer />
    </AuthProvider>,
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getToken).mockReturnValue(null);
  });

  it("starts logged out when no token exists", async () => {
    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId("logged-in").textContent).toBe("false");
    });
  });

  it("restores session from existing token on mount", async () => {
    vi.mocked(getToken).mockReturnValue("existing-token");
    vi.mocked(authAPI.getCurrentUser).mockResolvedValue({
      id: "1",
      name: "Returning User",
      email: "r@rvu.edu.in",
      role: "customer",
      wallet_balance: 0,
    });

    renderWithAuth();

    await waitFor(() => {
      expect(screen.getByTestId("logged-in").textContent).toBe("true");
      expect(screen.getByTestId("user-name").textContent).toBe("Returning User");
    });
  });

  it("clears session when token is invalid on mount", async () => {
    vi.mocked(getToken).mockReturnValue("bad-token");
    vi.mocked(authAPI.getCurrentUser).mockRejectedValue(new Error("401"));

    renderWithAuth();

    await waitFor(() => {
      expect(removeToken).toHaveBeenCalled();
      expect(screen.getByTestId("logged-in").textContent).toBe("false");
    });
  });

  it("sets user and token on successful login", async () => {
    vi.mocked(authAPI.login).mockResolvedValue({
      access_token: "tok-abc",
      user: { id: "2", name: "Campus Student", email: "s@rvu.edu.in", role: "customer", wallet_balance: 0 },
    });

    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("logged-in").textContent).toBe("false"));

    await act(async () => {
      screen.getByRole("button", { name: "Login" }).click();
    });

    expect(setToken).toHaveBeenCalledWith("tok-abc");
    expect(screen.getByTestId("logged-in").textContent).toBe("true");
    expect(screen.getByTestId("user-name").textContent).toBe("Campus Student");
  });

  it("clears user and token on logout", async () => {
    vi.mocked(getToken).mockReturnValue("tok-abc");
    vi.mocked(authAPI.getCurrentUser).mockResolvedValue({
      id: "2",
      name: "Campus Student",
      email: "s@rvu.edu.in",
      role: "customer",
      wallet_balance: 0,
    });
    vi.mocked(authAPI.logout).mockResolvedValue({});

    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("logged-in").textContent).toBe("true"));

    await act(async () => {
      screen.getByRole("button", { name: "Logout" }).click();
    });

    await waitFor(() => {
      expect(removeToken).toHaveBeenCalled();
      expect(screen.getByTestId("logged-in").textContent).toBe("false");
      expect(screen.getByTestId("user-name").textContent).toBe("none");
    });
  });

  it("returns requires_verification on register without immediate token", async () => {
    vi.mocked(authAPI.register).mockResolvedValue({
      requires_verification: true,
      message: "User registered successfully. Please verify your email.",
      user: { id: "3", name: "New User", email: "new@rvu.edu.in", is_verified: false },
    });

    let result: any;
    function CapturingConsumer() {
      const { register } = useAuth();
      return (
        <button
          onClick={async () => {
            result = await register("New User", "new@rvu.edu.in", "pass123");
          }}
        >
          Register
        </button>
      );
    }

    render(<AuthProvider><CapturingConsumer /></AuthProvider>);
    await act(async () => {
      screen.getByRole("button", { name: "Register" }).click();
    });

    expect(result.requires_verification).toBe(true);
    expect(setToken).not.toHaveBeenCalled();
  });

  it("throws when useAuth is used outside AuthProvider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow("useAuth must be used within an AuthProvider");
    spy.mockRestore();
  });
});
