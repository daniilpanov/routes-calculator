import "../resources/scss/page/route/index.scss";
import "../resources/scss/components/modal_style.scss";

import React, { useEffect, useState } from "react";
import { CreatePointModal } from "./CreatePointModal";
import { routesService } from "../api/Routes";
import { Dropdown } from "../components/Dropdown";
import { SearchableDropdown } from "../components/SearchableDropdown";

import copying from "../resources/images/copying.png";
import trashcan from "../resources/images/trashcan.png";
import accessMarks from "../resources/images/accessMarks.png";
import cross from "../resources/images/cross.png";
import { PriceItem, Route } from "../interfaces/Routes";
import { formatDate } from "../utils/Date";

const PAGE_SIZE = 25;

export function RoutesTable() {
    const [ routes, setRoutes ] = useState<Route[]>([]);
    const [ loading, setLoading ] = useState(true);
    const [ error, setError ] = useState<string | null>(null);
    const [ addingRoutes, setAddingRoutes ] = useState<Omit<Route, "id">[]>([]);
    const [ isModalOpen, setIsModalOpen ] = useState(false);
    const [ plug, setPlug ] = useState<string>("");
    const [ selectedFilter, setSelectedFilter ] = useState<string>("Поиск по...");
    const [ bodyFilter, setBodyFilter ] = useState<string>("");

    const [ page, setPage ] = useState(1);
    const [ totalPages, setTotalPages ] = useState(1);

    const [ optionsDropdown, setOptionsDropdown ] = useState<{ [key: string]: string[] }>({
        company: [ "HUB", "FESCO", "TLC" ],
        container: [ "20'DC ≥24t", "20'DC ≥28t", "40'HC ≥28t" ],
        routeType: [ "ЖД", "Морской" ],
        currency: [ "RUB", "USD", "EUR" ],
        filter: [ "Компания", "Тип маршрута", "Контейнер", "Диапазон дат", "Точка отправления", "Точка прибытия" ],
    });

    const emptyRoute: Omit<Route, "id"> = {
        company: { id: 0, name: "" },
        container: { id: 0, name: "", weight_from: 0, weight_to: 0, size: 0, type: "" },
        start_point: { id: 0, RU_city: "", RU_country: "", city: "", country: "" },
        end_point: { id: 0, RU_city: "", RU_country: "", city: "", country: "" },
        effective_from: "",
        effective_to: "",
        price: [
            { type: "price", value: 0, currency: "RUB" },
            { type: "drop", value: 0, currency: "USD" },
            { type: "guard", value: 0, currency: "USD" },
            { type: "fifo", value: 0, currency: "USD" },
            { type: "filo", value: 0, currency: "USD" },
        ],
        route_type: "sea",
    };

    useEffect(() => {
        fetchRoutes();
    }, [ page ]);

    const fetchRoutes = async () => {
        try {
            setLoading(true);
            const response = await routesService.getRoutes(page, PAGE_SIZE);
            if (response.status === "OK") {
                const normalizedRoutes = response.routes.map((route: any) => {
                    const prices = Array.isArray(route.prices) ? route.prices : [];

                    if (route.route_type === "rail") {
                        const priceItem = prices.find((p: any) => p.type === "price");
                        if (priceItem) {
                            const hasFobfor = prices.some((p: any) => p.type === "fobfor");
                            if (!hasFobfor) {
                                prices.push({ ...priceItem, type: "fobfor" });
                            }
                        }
                    }

                    return { ...route, prices };
                });
                setRoutes(normalizedRoutes);
                setTotalPages(Math.ceil(response.count / PAGE_SIZE));
            } else {
                setError("Не удалось загрузить маршруты");
            }
        } catch (err) {
            setError("Ошибка при загрузке маршрутов");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddRoute = () => {
        setAddingRoutes((prev) => [ ...prev, { ...emptyRoute } ]);
    };

    const handleSaveNewRoute = (index: number) => {
        const newRoute = addingRoutes[index];
        if (
            !newRoute.company.name ||
            !newRoute.container.name ||
            !newRoute.start_point.RU_city ||
            !newRoute.end_point.RU_city ||
            !newRoute.effective_from ||
            !newRoute.effective_to
        ) {
            alert("Все поля обязательны для заполнения");
            return;
        }

        const filteredPrices = newRoute.price
            .filter((price) => {
                if (newRoute.route_type === "sea") {
                    return [ "fifo", "filo", "drop", "guard" ].includes(price.type);
                } else {
                    return price.type === "fobfor" || price.type === "price";
                }
            })
            .map((price) => {
                if (newRoute.route_type === "rail" && price.type === "fobfor") {
                    return { ...price, type: "price" };
                }
                return price;
            });

        const cleanedRoute = { ...newRoute, prices: filteredPrices };
        setRoutes((prev) => [ ...prev, { ...cleanedRoute, id: Date.now() } ]);
        setAddingRoutes((prev) => prev.filter((_, i) => i !== index));
    };

    const handleCancelNewRoute = (index: number) =>
        setAddingRoutes((prev) => prev.filter((_, i) => i !== index));

    const handleChangeNewRouteField = <K extends keyof Omit<Route, "id">>(
        index: number,
        field: K,
        value: any,
    ) => {
        setAddingRoutes((prev) =>
            prev.map((route, i) => (i === index ? { ...route, [field]: value } : route)),
        );
    };

    const handleChangePriceValue = (index: number, type: string, value: number) => {
        setAddingRoutes((prev) =>
            prev.map((route, i) => {
                if (i !== index) return route;
                return {
                    ...route,
                    prices: route.price.map((p) =>
                        p.type === type ? { ...p, value } : p,
                    ),
                };
            }),
        );
    };

    const handleChangePriceCurrency = (index: number, type: string, currency: string) => {
        setAddingRoutes((prev) =>
            prev.map((route, i) => {
                if (i !== index) return route;
                return {
                    ...route,
                    prices: route.price.map((p) =>
                        p.type === type ? { ...p, currency } : p,
                    ),
                };
            }),
        );
    };

    const handleRoutesDelete = async (id: number) => {
        if (!window.confirm("Удалить маршрут?")) return;
        const response = await routesService.deleteRoute(id).catch(() => fetchRoutes());
        if (response?.status === "OK") {
            setRoutes((prev) => prev.filter((route) => route.id !== id));
            alert("Маршрут успешно удален");
        } else {
            alert("Неизвестная ошибка, удаление отменено.");
        }
    };

    const handleCopyRoute = (routeToCopy: Route) => {
        const { id, ...withoutId } = routeToCopy;
        const copiedRoute = {
            ...withoutId,
            company: { ...withoutId.company },
            container: { ...withoutId.container },
            start_point: { ...withoutId.start_point },
            end_point: { ...withoutId.end_point },
            prices: withoutId.price.map((p) => ({ ...p })),
        };
        setAddingRoutes((prev) => [ ...prev, copiedRoute ]);
    };

    const getPaginationPages = () => {
        const pages = [];
        const maxVisiblePages = 5;

        if (totalPages <= maxVisiblePages) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            pages.push(1);
            let startPage = Math.max(2, page - 1);
            let endPage = Math.min(totalPages - 1, page + 1);

            if (page <= 3) endPage = 4;
            else if (page >= totalPages - 2) startPage = totalPages - 3;

            if (startPage > 2) pages.push("...");
            for (let i = startPage; i <= endPage; i++) pages.push(i);
            if (endPage < totalPages - 1) pages.push("...");
            pages.push(totalPages);
        }

        return pages;
    };

    const renderPrice = (prices: PriceItem[], type: string, label: string) => {
        const price = prices.find((p) => {
            if (type === "fobfor") {
                return p.type === "fobfor" || p.type === "price";
            }
            return p.type === type;
        });

        if (!price || price.value === null) return null;
        return <div>{label}: {price.value} {price.currency}</div>;
    };

    if (loading) return <div className="page_div">Загрузка...</div>;

    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление маршрутами</h1></div>

            <div className="control_panel_div">
                <button className="control_btn" onClick={ () => setIsModalOpen(true) }>Создать точку</button>
                <button onClick={ handleAddRoute } className="control_btn">Создать маршрут</button>
            </div>
            <div className="filter_div">
                <Dropdown
                    options={ optionsDropdown.filter }
                    selected={ selectedFilter }
                    className="filter-dropdown-wrapper"
                    onSelect={ setSelectedFilter } />
                {selectedFilter == "Тип маршрута" && (
                    <Dropdown
                        options={ optionsDropdown.routeType }
                        selected="ЖД"
                        className="input-dropdown-wrapper"
                        onSelect={ setBodyFilter } />
                )}
                <button
                    className="actions_cancel_btn"
                    //onClick={() => handleCancelNewRoute(index)}
                >
                    Лупа
                </button>
                <button
                    className="actions_cancel_btn"
                    //onClick={() => handleCancelNewRoute(index)}
                >
                    <img src={ cross } alt="отменить" className="actions_img" />
                </button>
            </div>

            {error && <div className="error_message">{error}</div>}

            <div className="table_div">
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>Компания</th>
                            <th>Тип маршрута</th>
                            <th>Контейнер</th>
                            <th>Диапазон дат</th>
                            <th>Точка отправки</th>
                            <th>Точка прибытия</th>
                            <th>Цены</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {routes.map((route) => {
                            const isSea = route.route_type === "sea";
                            const priceItems = route.price || [];

                            return (
                                <tr key={ route.id }>
                                    <td><input type="checkbox" /></td>
                                    <td>{route.company.name}</td>
                                    <td>{isSea ? "Морской" : "ЖД"}</td>
                                    <td>{route.container.name}</td>
                                    <td>{formatDate(route.effective_from)} - {formatDate(route.effective_to)}</td>
                                    <td>{route.start_point.RU_country}, {route.start_point.RU_city}</td>
                                    <td>{route.end_point.RU_country}, {route.end_point.RU_city}</td>
                                    <td className="price-cell">
                                        {isSea ? (
                                            <div className="sea-prices">
                                                {renderPrice(priceItems, "fifo", "FIFO")}
                                                {renderPrice(priceItems, "filo", "FILO")}
                                                {renderPrice(priceItems, "drop", "Drop")}
                                            </div>
                                        ) : (
                                            <div className="rail-prices">
                                                {renderPrice(priceItems, "fobfor", "Fobfor")}
                                                {renderPrice(priceItems, "guard", "Guard")}
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <div className="action_div">
                                            <button
                                                className="actions_trashcan_btn"
                                                onClick={ () => handleRoutesDelete(route.id) }
                                            >
                                                <img src={ trashcan } alt="удалить" className="actions_img" />
                                            </button>
                                            <button
                                                className="actions_copying_btn"
                                                onClick={ () => handleCopyRoute(route) }
                                            >
                                                <img src={ copying } alt="копировать" className="actions_img" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}

                        {addingRoutes.map((newRoute, index) => {
                            const isSea = newRoute.route_type === "sea";

                            return (
                                <tr key={ `adding-${index}` }>
                                    <td></td>
                                    <td>
                                        <Dropdown
                                            options={ optionsDropdown.company }
                                            selected={ newRoute.company.name }
                                            className="add-route-dropdown-wrapper"
                                            onSelect={ (val) => handleChangeNewRouteField(index, "company", { id: 0, name: val }) }
                                        />
                                    </td>
                                    <td>
                                        <Dropdown
                                            options={ optionsDropdown.routeType }
                                            selected={ isSea ? "Морской" : "ЖД" }
                                            className="add-route-dropdown-wrapper"
                                            onSelect={ (val) => {
                                                const newType = val === "ЖД" ? "rail" : "sea";
                                                handleChangeNewRouteField(index, "route_type", newType);
                                            } }
                                        />
                                    </td>
                                    <td>
                                        <Dropdown
                                            options={ optionsDropdown.container }
                                            selected={ newRoute.container.name }
                                            className="add-route-dropdown-wrapper"
                                            onSelect={ (val) => handleChangeNewRouteField(index, "container", { ...newRoute.container, name: val }) }
                                        />
                                    </td>
                                    <td>
                                        <input
                                            type="date"
                                            value={ newRoute.effective_from }
                                            className="date-input"
                                            onChange={ (e) => handleChangeNewRouteField(index, "effective_from", e.target.value) }
                                        />
                                        <input
                                            type="date"
                                            value={ newRoute.effective_to }
                                            className="date-input"
                                            onChange={ (e) => handleChangeNewRouteField(index, "effective_to", e.target.value) }
                                        />
                                    </td>
                                    <td>
                                        <SearchableDropdown
                                            value={ newRoute.start_point }
                                            className="add-route-dropdown-wrapper"
                                            onSelect={ (point) => handleChangeNewRouteField(index, "start_point", point) }
                                        />
                                    </td>
                                    <td>
                                        <SearchableDropdown
                                            value={ newRoute.end_point }
                                            className="add-route-dropdown-wrapper"
                                            onSelect={ (point) => handleChangeNewRouteField(index, "end_point", point) }
                                        />
                                    </td>
                                    <td>
                                        {isSea ? (
                                            <div className="price-edit-grid">
                                                {[ "fifo", "filo", "drop", "guard" ].map((type) => (
                                                    <div key={ type } className="price-row">
                                                        <span className="price-label">
                                                            {type === "fifo" ? "FIFO" :
                                                                type === "filo" ? "FILO" :
                                                                    type === "drop" ? "Drop" : "Guard"}:
                                                        </span>
                                                        <input
                                                            type="number"
                                                            value={ newRoute.price.find(p => p.type === type)?.value ?? 0 }
                                                            className="table_input price-input"
                                                            onChange={ (e) => handleChangePriceValue(index, type, Number(e.target.value)) }
                                                        />
                                                        <Dropdown
                                                            options={ optionsDropdown.currency }
                                                            selected={ newRoute.price.find(p => p.type === type)?.currency || "USD" }
                                                            className="currency-dropdown"
                                                            onSelect={ (currency) => handleChangePriceCurrency(index, type, currency) }
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="price-edit-grid">
                                                <div className="price-row">
                                                    <span className="price-label">Fobfor:</span>
                                                    <input
                                                        type="number"
                                                        value={
                                                            newRoute.price.find(p => p.type === "fobfor" || p.type === "price")?.value ?? 0
                                                        }
                                                        className="table_input price-input"
                                                        onChange={ (e) => handleChangePriceValue(index, "fobfor", Number(e.target.value)) }
                                                    />
                                                    <Dropdown
                                                        options={ optionsDropdown.currency }
                                                        selected={
                                                            newRoute.price.find(p => p.type === "fobfor" || p.type === "price")?.currency || "RUB"
                                                        }
                                                        className="currency-dropdown"
                                                        onSelect={ (currency) => handleChangePriceCurrency(index, "fobfor", currency) }
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <div className="action_div">
                                            <button
                                                className="actions_save_btn"
                                                onClick={ () => handleSaveNewRoute(index) }
                                            >
                                                <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                            </button>
                                            <button
                                                className="actions_cancel_btn"
                                                onClick={ () => handleCancelNewRoute(index) }
                                            >
                                                <img src={ cross } alt="отменить" className="actions_img" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>

                <div className="pagination_controls">
                    <button disabled={ page === 1 } className="control_btn" onClick={ () => setPage(page - 1) }>
                        Назад
                    </button>
                    {getPaginationPages().map((pageNumber, index) => (
                        <button
                            key={ index }
                            className={ `control_btn ${pageNumber === page ? "active" : ""} ${pageNumber === "..." ? "ellipsis" : ""}` }
                            disabled={ pageNumber === "..." }
                            onClick={ () => typeof pageNumber === "number" && setPage(pageNumber) }
                        >
                            {pageNumber}
                        </button>
                    ))}
                    <button disabled={ page === totalPages } className="control_btn" onClick={ () => setPage(page + 1) }>
                        Вперёд
                    </button>
                </div>

                <CreatePointModal isOpen={ isModalOpen } onClose={ () => setIsModalOpen(false) } />
            </div>
        </div>
    );
}
