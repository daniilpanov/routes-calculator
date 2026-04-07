function _parseLocations(data) {
    const parsedData = {};
    for (const loc in data)
        parsedData[loc] = JSON.stringify(data[loc]);

    return parsedData;
}

async function getDepartures(date) {
    const resp = await fetch(`/api/v1/points/departures?date=${date}`);
    if (!resp.ok)
        throw new Error(`Got an error while getting departures [${resp.status}]\n${await resp.text()}`);

    return _parseLocations(await resp.json());
}

async function getDestinations(date, departureId) {
    const resp = await fetch(`/api/v1/points/destinations?date=${date}&departure_point_id=${departureId}`);
    if (!resp.ok)
        throw new Error(`Got an error while getting destinations [${resp.status}]\n${await resp.text()}`);

    return _parseLocations(await resp.json());
}

async function getRoutes(
    dispatchDate,
    departureId,
    destinationId,
    cargoWeight,
    containerType,
) {
    const response = await fetch("/api/v1/routes/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            dispatchDate,
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
    const response = await fetch("/api/v1/rates/");
    if (!response.ok)
        throw new Error(`Got an error while getting rates [${response.status}]\n${await response.text()}`);

    return await response.json();
}
