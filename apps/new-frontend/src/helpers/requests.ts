export async function fetchAsJSON(url: string, options?: RequestInit): Promise<object | unknown[]> {
    const resp = await fetch(url, options);
    if (!resp.ok)
        throw new Error(
            `Got an error while executing ${options?.method ?? "GET"} ${url} [${resp.status}]\n${await resp.text()}`
        );

    return await resp.json();
}
