import { NextResponse } from "next/server";

/**
 * Debug endpoint to test CelesTrak connectivity from Vercel.
 * Visit /api/debug on the deployed URL to diagnose issues.
 */
export async function GET() {
    const results: Record<string, unknown> = {
        timestamp: new Date().toISOString(),
        env: process.env.NODE_ENV,
    };

    // Test CelesTrak connectivity
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(
            "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE",
            {
                signal: controller.signal,
                headers: {
                    "User-Agent": "SatelliteAltitudeApp/1.0 (diagnostic)",
                },
            }
        );
        clearTimeout(timeoutId);

        const text = await res.text();
        results.celestrak = {
            ok: res.ok,
            status: res.status,
            statusText: res.statusText,
            bodyPreview: text.slice(0, 200),
        };
    } catch (err) {
        results.celestrak = {
            ok: false,
            error: err instanceof Error ? err.message : String(err),
        };
    }

    return NextResponse.json(results);
}
