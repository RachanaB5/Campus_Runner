import { render, screen, act, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CartProvider, useCart } from "./CartContext";

vi.mock("../services/api", () => ({
  getToken: vi.fn(),
  removeToken: vi.fn(),
  API_BASE_URL: "http://localhost:5000/api",
}));

import { getToken } from "../services/api";

const mockCart = (overrides = {}) => ({
  id: "cart-1",
  user_id: "user-1",
  total_price: 140,
  item_count: 2,
  items: [
    {
      id: "item-1",
      cart_id: "cart-1",
      food_id: "food-1",
      food_name: "Veg Burger",
      quantity: 2,
      price: 70,
      total: 140,
      created_at: "",
      updated_at: "",
    },
  ],
  created_at: "",
  updated_at: "",
  ...overrides,
});

function TestConsumer() {
  const { cart, addToCart, removeFromCart, clearCart, getTotalItems, getTotalPrice } = useCart();
  return (
    <div>
      <span data-testid="item-count">{getTotalItems()}</span>
      <span data-testid="total-price">{getTotalPrice()}</span>
      <span data-testid="cart-null">{cart === null ? "null" : "loaded"}</span>
      <button onClick={() => addToCart("food-1", 2)}>Add</button>
      <button onClick={() => removeFromCart("item-1")}>Remove</button>
      <button onClick={() => clearCart()}>Clear</button>
    </div>
  );
}

function renderWithCart() {
  return render(
    <CartProvider>
      <TestConsumer />
    </CartProvider>,
  );
}

describe("CartContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getToken).mockReturnValue(null);
    global.fetch = vi.fn();
  });

  it("starts with null cart when unauthenticated", async () => {
    renderWithCart();
    await waitFor(() => {
      expect(screen.getByTestId("cart-null").textContent).toBe("null");
      expect(screen.getByTestId("item-count").textContent).toBe("0");
    });
  });

  it("loads cart on mount when token exists", async () => {
    vi.mocked(getToken).mockReturnValue("tok");
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockCart(),
    } as Response);

    renderWithCart();

    await waitFor(() => {
      expect(screen.getByTestId("item-count").textContent).toBe("2");
      expect(screen.getByTestId("total-price").textContent).toBe("140");
    });
  });

  it("updates cart state after addToCart", async () => {
    vi.mocked(getToken).mockReturnValue("tok");
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => mockCart({ item_count: 0, total_price: 0, items: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ cart: mockCart() }) } as Response);

    renderWithCart();
    await waitFor(() => expect(screen.getByTestId("item-count").textContent).toBe("0"));

    await act(async () => {
      screen.getByRole("button", { name: "Add" }).click();
    });

    expect(screen.getByTestId("item-count").textContent).toBe("2");
  });

  it("updates cart state after removeFromCart", async () => {
    vi.mocked(getToken).mockReturnValue("tok");
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => mockCart() } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ cart: mockCart({ item_count: 0, total_price: 0, items: [] }) }) } as Response);

    renderWithCart();
    await waitFor(() => expect(screen.getByTestId("item-count").textContent).toBe("2"));

    await act(async () => {
      screen.getByRole("button", { name: "Remove" }).click();
    });

    expect(screen.getByTestId("item-count").textContent).toBe("0");
  });

  it("clears cart state after clearCart", async () => {
    vi.mocked(getToken).mockReturnValue("tok");
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => mockCart() } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ cart: mockCart({ item_count: 0, total_price: 0, items: [] }) }) } as Response);

    renderWithCart();
    await waitFor(() => expect(screen.getByTestId("item-count").textContent).toBe("2"));

    await act(async () => {
      screen.getByRole("button", { name: "Clear" }).click();
    });

    expect(screen.getByTestId("item-count").textContent).toBe("0");
  });

  it("resets cart to null on auth:logout event", async () => {
    vi.mocked(getToken).mockReturnValue("tok");
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockCart(),
    } as Response);

    renderWithCart();
    await waitFor(() => expect(screen.getByTestId("item-count").textContent).toBe("2"));

    act(() => {
      window.dispatchEvent(new Event("auth:logout"));
    });

    await waitFor(() => {
      expect(screen.getByTestId("cart-null").textContent).toBe("null");
    });
  });

  it("throws when useCart is used outside CartProvider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow("useCart must be used within a CartProvider");
    spy.mockRestore();
  });
});
