import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Overview from "../Overview.vue";

describe("Overview", () => {
  it("renders overview title", () => {
    const wrapper = mount(Overview);
    expect(wrapper.get('[data-testid="overview-title"]').text()).toContain("系统概览");
  });
});
