function _parseLocations(data) {
    const parsedData = {};
    for (const loc in data)
        parsedData[loc] = JSON.stringify(data[loc]);

    return parsedData;
}

async function getDepartures(date) {
    const resp = await fetch(`/api/points/departures?date=${date}`);
    if (!resp.ok)
        throw new Error(`Got an error while getting departures [${resp.status}]\n${await resp.text()}`);

    return _parseLocations(await resp.json());
}

async function getDestinations(date, departureId) {
    const resp = await fetch(`/api/points/destinations?date=${date}&departure_point_id=${departureId}`);
    if (!resp.ok)
        throw new Error(`Got an error while getting destinations [${resp.status}]\n${await resp.text()}`);

    return _parseLocations(await resp.json());
}

async function getRoutes(
    dispatchDate,
    onlyInSelectedDateRange,
    departureId,
    destinationId,
    cargoWeight,
    containerType,
) {
    const response = await fetch("/api/routes/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            dispatchDate,
            onlyInSelectedDateRange,
            departureId,
            destinationId,
            cargoWeight,
            containerType,
        }),
    });
    if (!response.ok)
        throw new Error(`Got an error while calculating routes [${response.status}]\n` + await response.text());

    return await response.json();
}

async function getRates() {
    const response = await fetch("/api/rates/");
    if (!response.ok)
        throw new Error(`Got an error while getting rates [${response.status}]\n${await response.text()}`);

    return await response.json();
}
