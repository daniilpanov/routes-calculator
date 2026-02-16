const dispatchDateInput = document.getElementById("dispatchDate");
const showAllRoutesCheckbox = document.getElementById("showAllRoutes");
const departureInput = document.getElementById("departure");
const destinationInput = document.getElementById("destination");
const departureHiddenInput = document.getElementById("departureId");
const destinationHiddenInput = document.getElementById("destinationId");
const cargoWeightInput = document.getElementById("cargoWeight");
const containerTypeInput = document.getElementById("containerType");

dispatchDateInput.valueAsDate = dispatchDateInput.valueAsDate || new Date();

function getCurrencySymbol(currName, defaultCur = undefined) {
    const currMap = {RUB: "₽", USD: "$"};
    return currMap[currName] ?? defaultCur;
}

async function asyncCallOrAlert(func, ...args) {
    try {
        return await func(...args);
    } catch (e) {
        showGlobalAlert(e.message);
    }
}

async function updateDepartures() {
    if (!dispatchDateInput.validity.valid)
        return;

    const date = dispatchDateInput.value;
    store.set("departures", await asyncCallOrAlert(getDepartures, date));

    destinationInput.value = "";
    destinationHiddenInput.value = "";
    destinationInput.disabled = true;
}

dispatchDateInput.addEventListener("input", updateDepartures);

setupAutocomplete("departure", "departureList", "departures", "departureId", async () => {
    destinationInput.disabled = false;
    const date = dispatchDateInput.value;
    const departureId = departureHiddenInput.value;
    store.set("destinations", await asyncCallOrAlert(getDestinations, date, departureId));
}, () => {
    destinationInput.disabled = true;
    destinationInput.value = "";
});
setupAutocomplete("destination", "destinationList", "destinations", "destinationId");

async function calculateAndRender() {
    const routes = await asyncCallOrAlert(
        getRoutes,
        dispatchDateInput.value,
        !showAllRoutesCheckbox.checked ?? false,
        JSON.parse(departureHiddenInput.value),
        JSON.parse(destinationHiddenInput.value),
        cargoWeightInput.value,
        containerTypeInput.value,
    );

    store.set("result", routes);

    const dataEls = [routes.one_service_routes, routes.multi_service_routes];
    const wrappers = [
        document.getElementById("results-direct"),
        document.getElementById("results-other"),
    ];

    const selectedCurrency = store.get("selectedCurrency").value;

    for (let i = 0; i < dataEls.length; ++i) {
        const data = dataEls[i];
        if (!data)
            continue;

        const container = wrappers[i];
        container.innerHTML = "";

        container.append(...data.map(([route, drop, mayRouteBeInvalid]) =>
            _buildRoute(route, drop, mayRouteBeInvalid, selectedCurrency)
        ));
    }

    updateResults(document.getElementById("currencySwitcher").value);
}

function _buildRoute(route, drop, mayRouteBeInvalid, selectedCurrency) {
    const icons = store.get("icons")?.value;

    const routeEl = document.createElement("div");
    routeEl.className = "p-3 mb-4 border rounded shadow-sm result-item";

    if (mayRouteBeInvalid)
        routeEl.innerHTML = renderRouteMayBeInvalidHint();

    const segmentsEl = document.createElement("div");
    segmentsEl.className = "segments";

    segmentsEl.innerHTML = route
        .map(segment => {
            const icon = segment.type === "SEA_RAIL"
                ? "Море+ЖД"
                : icons[segment.type.toLowerCase()] || segment.type;

            return segment.price
                ? renderSinglePrice(icon, segment)
                : renderMultiPrice(icon, segment, segment.type === "SEA_RAIL", selectedCurrency);
        })
        .join("<div class='text-center mb-3 col-md-2'>↓</div>");

    routeEl.appendChild(segmentsEl);
    routeEl.appendChild(document.createElement("hr"));
    routeEl.appendChild(renderDrop(drop));

    const sumPriceEl = document.createElement("div");
    sumPriceEl.classList.add("sum-price", "mb-3");
    routeEl.appendChild(sumPriceEl);

    return routeEl;
}
