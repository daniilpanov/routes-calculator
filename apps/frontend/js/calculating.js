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

    let minSumPrice = 0, maxSumPrice = 0, sumPrice = 0;
    let minSumPriceWithConv = 0, maxSumPriceWithConv = 0, sumPriceWithConv = 0;
    let globalSum = false;

    const segmentsHtml = [];

    for (let i = 0; i < route.length; i++) {
        const segment = route[i];

        if (segment.price) {
            const { incrementation, incrementationWithConv } =
                getSimpleSegmentIncrementation(segment, selectedCurrency, needConversation);

            minSumPrice += incrementation;
            maxSumPrice += incrementation;
            minSumPriceWithConv += incrementationWithConv;
            maxSumPriceWithConv += incrementationWithConv;

            const icon = segment.type === "SEA_RAIL"
                ? "Море+ЖД"
                : icons[segment.type.toLowerCase()] || segment.type;

            segmentsHtml.push(renderSinglePrice(icon, segment));
        } else {
            if (segment.type === "SEA_RAIL")
                globalSum = true;

            const multiResult = getMultiSegmentIncrementation(
                segment,
                globalSum,
                selectedCurrency,
                needConversation
            );

            minSumPrice += multiResult.minimal;
            maxSumPrice += multiResult.maximal;
            sumPrice += multiResult.segmentSumPrice;

            minSumPriceWithConv += multiResult.minimalWithConv;
            maxSumPriceWithConv += multiResult.maximalWithConv;
            sumPriceWithConv += multiResult.segmentSumPriceWithConv;

            const icon = segment.type === "SEA_RAIL"
                ? "Море+ЖД"
                : icons[segment.type.toLowerCase()] || segment.type;

            segmentsHtml.push(renderMultiPrice(icon, segment, selectedCurrency));
        }

        if (i < route.length - 1)
            segmentsHtml.push("<div class='text-center mb-3 col-md-2'>↓</div>");
    }

    segmentsEl.innerHTML = segmentsHtml.join("");
    routeEl.appendChild(segmentsEl);

    routeEl.appendChild(document.createElement("hr"));
    routeEl.appendChild(renderDrop(drop));

    if (drop) {
        const { dropPrice, dropPriceWithConv } = getDropIncrementation(drop, selectedCurrency);

        minSumPrice += dropPrice;
        maxSumPrice += dropPrice;
        minSumPriceWithConv += dropPriceWithConv;
        maxSumPriceWithConv += dropPriceWithConv;

        if (globalSum) {
            sumPrice += dropPrice;
            sumPriceWithConv += dropPriceWithConv;
        }
    }

    const sumPriceEl = createSumPriceElement({
        minSumPrice,
        maxSumPrice,
        sumPrice,
        minSumPriceWithConv,
        maxSumPriceWithConv,
        sumPriceWithConv,
        selectedCurrency,
        needConversation
    });
    routeEl.appendChild(sumPriceEl);

    const sortValue = sumPriceWithConv || minSumPriceWithConv;
    return [sortValue, routeEl];
}

function createSumPriceElement({
    minSumPrice,
    maxSumPrice,
    sumPrice,
    minSumPriceWithConv,
    maxSumPriceWithConv,
    sumPriceWithConv,
    selectedCurrency,
    needConversation,
}) {
    const minPrice = Math.round((minSumPrice + Number.EPSILON) * 100) / 100;
    const maxPrice = Math.round((maxSumPrice + Number.EPSILON) * 100) / 100;
    const totalSumPrice = Math.round((sumPrice + Number.EPSILON) * 100) / 100;

    const minPriceWithConv = Math.round((minSumPriceWithConv + Number.EPSILON) * 100) / 100;
    const maxPriceWithConv = Math.round((maxSumPriceWithConv + Number.EPSILON) * 100) / 100;
    const totalSumPriceWithConv = Math.round((sumPriceWithConv + Number.EPSILON) * 100) / 100;

    const sumPriceEl = document.createElement("div");
    sumPriceEl.classList.add("sum-price", "mb-3");

    let content = "<div class='row'><div class='col-md-7'>Суммарная стоимость: </div><div class='col-md-5'><b>";
    content += numberWithSpaces(totalSumPrice || minPrice);
    if (minPrice !== maxPrice) {
        content += " - " + numberWithSpaces(maxPrice);
    }
    content += ` ${selectedCurrency}</b></div></div>`;

    if (needConversation) {
        content += "<div class='row'><div class='col-md-7'>Оплата в рублях по курсу ЦБ на дату выставления счёта: </div><div class='col-md-5'><b>";
        content += numberWithSpaces(totalSumPriceWithConv || minPriceWithConv);
        if (minPriceWithConv !== maxPriceWithConv) {
            content += " - " + numberWithSpaces(maxPriceWithConv);
        }
        content += ` ${selectedCurrency}</b></div></div>`;
    }

    sumPriceEl.innerHTML = content;
    return sumPriceEl;
}
