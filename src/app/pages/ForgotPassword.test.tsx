import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ForgotPassword } from "./ForgotPassword";

vi.mock("../services/api", () => ({
  authAPI: {
    forgotPassword: vi.fn(),
    resendOtp: vi.fn(),
    resetPassword: vi.fn(),
  },
}));

import { authAPI } from "../services/api";

describe("ForgotPassword", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a helpful error for non-RVU emails", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>,
    );

    await user.type(screen.getByPlaceholderText("yourname@rvu.edu.in"), "test@gmail.com");
    await user.click(screen.getByRole("button", { name: /send reset code/i }));

    expect(await screen.findByText(/Please use your RV University email/i)).toBeInTheDocument();
  });

  it("shows the backend dev otp fallback when email sending fails", async () => {
    vi.mocked(authAPI.forgotPassword).mockResolvedValue({
      email_sent: false,
      message: "Password reset code generated but email was not sent.",
      dev_otp: "123456",
    } as any);

    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>,
    );

    await user.type(screen.getByPlaceholderText("yourname@rvu.edu.in"), "student@rvu.edu.in");
    await user.click(screen.getByRole("button", { name: /send reset code/i }));

    await waitFor(() => {
      expect(screen.getByText(/Development code:/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/123456/)).toBeInTheDocument();
    expect(screen.getByText(/reset code generated/i)).toBeInTheDocument();
  });
});
