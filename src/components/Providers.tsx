"use client";

import { LanguageProvider as Provider } from "@/lib/i18n";

export function Providers({ children }: { children: React.ReactNode }) {
    return <Provider>{children}</Provider>;
}
