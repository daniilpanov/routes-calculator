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

export interface SSEEvent {
    event: string;
    data: string;
}

export async function* fetchSSE(url: string, options?: RequestInit): AsyncGenerator<SSEEvent> {
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
            `Got an error while executing ${options?.method ?? "POST"} ${url} [${resp.status}]\n${await resp.text()}`
        );

    const reader = resp.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop()!;

        for (const part of parts) {
            let event = "message";
            let data = "";
            for (const line of part.split("\n")) {
                if (line.startsWith("event: ")) event = line.slice(7);
                else if (line.startsWith("data: ")) data = line.slice(6);
            }
            if (data) yield { event, data };
        }
    }
}
