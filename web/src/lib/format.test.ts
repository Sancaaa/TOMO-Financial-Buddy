import { describe, expect, it } from "vitest";
import { dateLabel, monthLong, monthShort, rupiah, rupiahShort } from "./format";

describe("rupiah", () => {
  it("format ribuan gaya Indonesia", () => {
    expect(rupiah(1500000)).toBe("Rp1.500.000");
  });
  it("membulatkan & menangani string/null", () => {
    expect(rupiah("2500.7")).toBe("Rp2.501");
    expect(rupiah(null)).toBe("Rp0");
  });
});

describe("rupiahShort", () => {
  it("juta dengan satu desimal bila perlu", () => {
    expect(rupiahShort(1500000)).toBe("Rp1,5jt");
    expect(rupiahShort(2000000)).toBe("Rp2jt");
  });
  it("ribuan dibulatkan", () => {
    expect(rupiahShort(18000)).toBe("Rp18rb");
  });
  it("nilai kecil apa adanya", () => {
    expect(rupiahShort(500)).toBe("Rp500");
  });
});

describe("label bulan", () => {
  it("monthShort & monthLong", () => {
    expect(monthShort("2026-07")).toBe("Jul");
    expect(monthLong("2026-07")).toBe("Jul 2026");
  });
});

describe("dateLabel", () => {
  it("tanggal + bulan singkat", () => {
    expect(dateLabel("2026-07-05T12:00:00Z")).toMatch(/^\d{1,2} [A-Za-z]{3}$/);
  });
});
