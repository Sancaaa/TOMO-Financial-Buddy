import { describe, expect, it } from "vitest";
import { clampOffset, detectIntent, resolveOffset, tapAction } from "./swipe";

describe("detectIntent", () => {
  it("pending saat gerakan di bawah ambang", () => {
    expect(detectIntent(3, 2)).toBe("pending");
  });
  it("horizontal saat |dx| dominan", () => {
    expect(detectIntent(-30, 5)).toBe("horizontal");
  });
  it("vertical saat |dy| dominan (biar scroll jalan)", () => {
    expect(detectIntent(4, 25)).toBe("vertical");
  });
});

describe("clampOffset", () => {
  it("hanya mengizinkan geser ke kiri, dibatasi -width", () => {
    expect(clampOffset(0, -50, 152)).toBe(-50);
    expect(clampOffset(0, -999, 152)).toBe(-152);
    expect(clampOffset(0, 40, 152)).toBe(0); // ke kanan tidak diizinkan
  });
  it("menambah dari base yang sudah terbuka", () => {
    expect(clampOffset(-152, 30, 152)).toBe(-122);
  });
});

describe("resolveOffset", () => {
  it("snap terbuka bila lewat separuh", () => {
    expect(resolveOffset(-90, 152)).toBe(-152);
  });
  it("snap tertutup bila belum separuh", () => {
    expect(resolveOffset(-40, 152)).toBe(0);
  });
});

describe("tapAction", () => {
  it("abaikan bila baru saja digeser", () => {
    expect(tapAction(true, false)).toBe("noop");
  });
  it("tutup bila baris terbuka", () => {
    expect(tapAction(false, true)).toBe("close");
  });
  it("pilih (buka edit) bila tap biasa saat tertutup", () => {
    expect(tapAction(false, false)).toBe("select");
  });
});
