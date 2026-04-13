import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { useAuthStore } from "../../stores/auth";
import AppShell from "../AppShell.vue";

vi.mock("vue-router", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useRoute: () => ({
      path: "/overview",
      meta: { title: "Overview" }
    })
  };
});

vi.mock("../../config/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } }
      }),
      signOut: vi.fn().mockResolvedValue({})
    }
  }
}));

describe("AppShell", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const authStore = useAuthStore();
    authStore.user = { email: "demo@local.test" };
  });

  it("renders left staggered menu without usage item", () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    });

    const menu = wrapper.get('[data-testid="staggered-menu-root"]');
    expect(menu.attributes("data-position")).toBe("left");
    expect(wrapper.get('[data-testid="staggered-menu-toggle"]').exists()).toBe(true);
    expect(wrapper.text()).not.toContain("Usage");
  });

  it("keeps header and scroll layout", () => {
    const wrapper = mount(AppShell, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          RouterView: true
        }
      }
    });

    expect(wrapper.get('[data-testid="app-shell-header"]').text()).toContain("Overview");
    expect(wrapper.get('[data-testid="app-shell-root"]').classes()).toContain("h-screen");
    expect(wrapper.get('[data-testid="app-shell-content"]').classes()).toContain("overflow-y-auto");
  });
});
