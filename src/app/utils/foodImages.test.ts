import { describe, expect, it } from "vitest";

import { FALLBACK_FOOD_IMAGE, getFoodImageUrl } from "./foodImages";

describe("getFoodImageUrl", () => {
  it("returns the provided image url when available", () => {
    expect(getFoodImageUrl("https://example.com/food.jpg", "Burgers")).toBe("https://example.com/food.jpg");
  });

  it("falls back to a category image when the image is missing", () => {
    expect(getFoodImageUrl("", "Pizza & Bread")).toContain("images.unsplash.com");
  });

  it("falls back to the global default when category is unknown", () => {
    expect(getFoodImageUrl(undefined, "Unknown Category")).toBe(FALLBACK_FOOD_IMAGE);
  });
});
