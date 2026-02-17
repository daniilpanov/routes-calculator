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

async function updateRoutes(
    dispatchDate,
    showAllRoutes,
    departureDescriptor,
    destinationDescriptor,
    containerWeight,
    containerType,
) {
    const routes = await asyncCallOrAlert(
        getRoutes,
        dispatchDate,
        !showAllRoutes,
        departureDescriptor,
        destinationDescriptor,
        containerWeight,
        containerType,
    );

    store.set("result", routes);
}

function renderRoutes() {
    const routes = store.get("result")?.value;
    if (!routes)
        return;

    const dataWithElements = [
        [routes.one_service_routes, document.getElementById("results-direct")],
        [routes.multi_service_routes, document.getElementById("results-other")],
    ];

    const selectedCurrency = store.get("selectedCurrency").value;
    const needConversation = selectedCurrency === "RUB";

    for (const [data, container] of dataWithElements) {
        container.innerHTML = "";

        const results = data.map(([route, drop, mayRouteBeInvalid]) =>
            _buildRoute(route, drop, mayRouteBeInvalid, selectedCurrency, needConversation)
        );

        const keys = new Array(results.length);
        for (let i = 0; i < keys.length; ++i)
            keys[i] = i;

        keys.sort((a, b) => results[a][0] - results[b][0]);

        for (const key of keys)
            container.appendChild(results[key][1]);
    }
}

function _buildRoute(route, drop, mayRouteBeInvalid, selectedCurrency, needConversation) {
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

    const [value, sumPriceEl] = createSumPrice(routeEl, selectedCurrency, needConversation);
    routeEl.appendChild(sumPriceEl);

    return [value, routeEl];
}
