"use client";

import { useLanguage } from "@/lib/i18n";

export default function LanguageSwitch() {
    const { language, setLanguage } = useLanguage();

    return (
        <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg p-1 border border-white/20">
            <button
                onClick={() => setLanguage("en")}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${language === "en"
                        ? "bg-white/20 text-white shadow-sm"
                        : "text-gray-300 hover:text-white hover:bg-white/10"
                    }`}
                aria-label="Switch to English"
            >
                EN
            </button>
            <button
                onClick={() => setLanguage("ja")}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${language === "ja"
                        ? "bg-white/20 text-white shadow-sm"
                        : "text-gray-300 hover:text-white hover:bg-white/10"
                    }`}
                aria-label="Switch to Japanese"
            >
                日本語
            </button>
        </div>
    );
}
