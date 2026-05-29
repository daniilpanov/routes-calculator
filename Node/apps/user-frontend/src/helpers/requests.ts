import { useDemoAuth } from "@/stores/demoAuth";

function demoHeaders(): Record<string, string> {
    const { isDemo, demoUid } = useDemoAuth();
    if (isDemo && demoUid)
        return { "X-Demo-User-UID": demoUid };
    return {};
}

export async function fetchAsJSON(url: string, options?: RequestInit): Promise<object | unknown[]> {
    if (!options)
        options = {};
    if (!options.headers)
        options.headers = {};

    const dh = demoHeaders();
    if (Object.keys(dh).length > 0)
        options.headers = { ...options.headers, ...dh };

    const resp = await fetch(url, options);
    if (!resp.ok)
        throw new Error(
            `Got an error while executing ${options?.method ?? "GET"} ${url} [${resp.status}]\n${await resp.text()}`
        );

    return await resp.json();
}
