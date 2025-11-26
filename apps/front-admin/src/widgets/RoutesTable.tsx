import React, { useEffect, useState } from "react";

import copying from "@/resources/images/copying.png";
import trashcan from "@/resources/images/trashcan.png";
import accessMarks from "@/resources/images/accessMarks.png";
import cross from "@/resources/images/cross.png";
import magnifier from "@/resources/images/magnifier.png";
import changeMarker from "@/resources/images/changeMarker.png";

import { companiesService } from "@/api/Companies";
import { Route, RouteEditRequest } from "@/interfaces/Routes";
import { Company } from "@/interfaces/Companies";
import { Container } from "@/interfaces/Containers";
import { Dropdown } from "@/components/Dropdown";
import { SearchableDropdown } from "@/components/SearchableDropdown";
import { formatDate, formatDateForServerFromInput, formatDateISO } from "@/utils/Date";
import { Pagination } from "./Pagination";
import { CreatePoint } from "./modals/CreatePoint";
import { containersApi } from "@/api/ContainersApi";
import { routesApi } from "@/api/RoutesApi";

const PAGE_SIZE = 25;

export function RoutesTable() {
    const [ routes, setRoutes ] = useState<Route[]>([]);
    const [ loading, setLoading ] = useState(true);
    const [ error, setError ] = useState<string | null>(null);
    const [ addingRoutes, setAddingRoutes ] = useState<Omit<Route, "id">[]>([]);
    const [ isModalOpen, setIsModalOpen ] = useState(false);
    const [ selectedRouteIds, setSelectedRouteIds ] = useState<number[]>([]);

    const [ totalPage, setTotalPages ] = useState<number>(0);
    const [ page, setPage ] = useState(1);

    const [ companies, setCompanies ] = useState<Company[]>([]);
    const [ containers, setContainers ] = useState<Container[]>([]);
    const [ editingRouteId, setEditingRouteId ] = useState<number | null>(null);
    const [ editedRoute, setEditedRoute ] = useState<Omit<Route, "id"> | null>(null);

    const [ activeFilters, setActiveFilters ] = useState<{ field: string; value: any }[]>([]);

    const [ optionsDropdown ] = useState({
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
            { type: "guard", value: 0, currency: "USD" },
            { type: "drop", value: 0, currency: "USD" },
            { type: "fifo", value: 0, currency: "USD" },
            { type: "filo", value: 0, currency: "USD" },
        ],
        route_type: "sea",
    };

    const routeTypeMapping = { "ЖД": "rail", "Морской": "sea" };
    const reverseRouteTypeMapping = { "rail": "ЖД", "sea": "Морской" };

    const handleEditRoute = (route: Route) => {
        setEditingRouteId(route.id);
        setEditedRoute({
            company: { ...route.company },
            container: { ...route.container },
            start_point: { ...route.start_point },
            end_point: { ...route.end_point },
            effective_from: formatDate(route.effective_from),
            effective_to: formatDate(route.effective_to),
            price: route.price.map(p => ({ ...p })),
            route_type: route.route_type,
        });
    };

    const handleSaveEditedRoute = async (routeId: number) => {
        if (!editedRoute) return;

        try {
            const pricePayload = editedRoute.route_type === "rail"
                ? {
                    price: editedRoute.price.find(p => p.type === "price")?.value || 0,
                    drop: editedRoute.price.find(p => p.type === "drop")?.value || 0,
                    guard: editedRoute.price.find(p => p.type === "guard")?.value || 0,
                }
                : {
                    fifo: editedRoute.price.find(p => p.type === "fifo")?.value || 0,
                    filo: editedRoute.price.find(p => p.type === "filo")?.value || 0,
                };
            const originalRoute = routes.find(el => el.id === routeId);
            if (!originalRoute) throw new Error("Маршрут не найден");

            const effective_from = formatDateForServerFromInput(editedRoute.effective_from);
            const effective_to = formatDateForServerFromInput(editedRoute.effective_to);
            const payload: RouteEditRequest = {
                route_id: routeId,
                edit_params: {
                    company_id: editedRoute.company.id,
                    container_id: editedRoute.container.id,
                    start_point_id: editedRoute.start_point.id,
                    end_point_id: editedRoute.end_point.id,
                    route_type: editedRoute.route_type,
                    effective_from: effective_from,
                    effective_to: effective_to,
                    price: pricePayload,
                },
            };


            const response = await routesApi.editRoute(payload);

            if (response.status === "OK") {
                setRoutes(prev =>
                    prev.map(r => r.id === routeId ? { ...r, ...response.edit_params } : r),
                );
                setEditingRouteId(null);
                setEditedRoute(null);
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка при редактировании маршрута");
        } finally {
            fetchRoutes();
        }
    };


    const handleCancelEdit = () => {
        setEditingRouteId(null);
        setEditedRoute(null);
    };


    useEffect(() => {
        fetchRoutes();
        fetchCompanies();
        fetchContainers();
    }, [ page ]);

    const fetchRoutes = async () => {
        try {
            setLoading(true);
            const response = await routesApi.getRoutes(page, PAGE_SIZE, buildFilterFields());
            if (response.status === "OK") {
                setRoutes(response.routes);
                setTotalPages(Math.ceil(response.count / PAGE_SIZE));
            } else setError("Не удалось загрузить маршруты");
        } catch (err) {
            setError("Ошибка при загрузке маршрутов");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchCompanies = async () => {
        try {
            const res = await companiesService.getCompanies();
            if (res.status === "OK") setCompanies(res.companies);
        } catch (err) { console.error(err); }
    };

    const fetchContainers = async () => {
        try {
            const res = await containersApi.getContainers();
            setContainers(res.containers);
        } catch (err) { console.error(err); }
    };



    const handleAddRoute = () => {
        setAddingRoutes(prev => [ ...prev, { ...emptyRoute } ]);
        document.querySelector(".table_div tbody tr:last-child")?.scrollIntoView();
    };

    const handleSaveNewRoute = async (index: number) => {
        const newRoute = addingRoutes[index];
        if (!newRoute.company.id || !newRoute.container.id || !newRoute.start_point.id || !newRoute.end_point.id || !newRoute.effective_from || !newRoute.effective_to)
            return alert("Все поля обязательны для заполнения");

        const requestData = {
            route_type: newRoute.route_type,
            company_id: newRoute.company.id,
            container_id: newRoute.container.id,
            start_point_id: newRoute.start_point.id,
            end_point_id: newRoute.end_point.id,
            effective_from: formatDate(newRoute.effective_from),
            effective_to: formatDate(newRoute.effective_to),
            price: newRoute.price.reduce((acc, p) => {
                if (p.value) acc[p.type] = p.value;
                return acc;
            }, {} as Record<string, number>),
        };
        try {
            const response = await routesApi.createRoute(requestData);
            if (response.status === "OK") {
                setRoutes(prev => [ ...prev, response.new_route ]);
                alert("Маршрут успешно добавлен");
                setAddingRoutes(prev => prev.filter((_, i) => i !== index));
            } else {
                alert("Ошибка при создании маршрута");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка запроса при создании маршрута");
        }
    };


    const handleCancelNewRoute = (index: number) => setAddingRoutes(prev => prev.filter((_, i) => i !== index));
    const handleChangeNewRouteField = <K extends keyof Omit<Route, "id">>(index: number, field: K, value: any) => {
        setAddingRoutes(prev =>
            prev.map((route, i) => {
                if (i !== index) return route;

                if (field === "route_type") {
                    const newPrice = value === "rail"
                        ? [
                            { type: "price", value: 0, currency: "RUB" },
                            { type: "guard", value: 0, currency: "USD" },
                            { type: "drop", value: 0, currency: "USD" },
                        ]
                        : [
                            { type: "fifo", value: 0, currency: "USD" },
                            { type: "filo", value: 0, currency: "USD" },
                        ];
                    return { ...route, route_type: value, price: newPrice };
                }

                return { ...route, [field]: value };
            }),
        );
    };


    const handleChangePriceValue = (index: number, type: string, value: number) => {
        setAddingRoutes(prev => prev.map((route, i) => i === index ? { ...route, price: route.price.map(p => (p.type === type ? { ...p, value } : p)) } : route));
    };

    const handleChangePriceCurrency = (index: number, type: string, currency: string) => {
        setAddingRoutes(prev => prev.map((route, i) => i === index ? { ...route, price: route.price.map(p => (p.type === type ? { ...p, currency } : p)) } : route));
    };

    const formatDateForInput = (date: string) => {
        if (!date) return "";
        const parts = date.includes(".") ? date.split(".") : date.split("-");
        if (parts.length === 3) {
            if (date.includes(".")) return `${parts[2]}-${parts[1]}-${parts[0]}`;
            else return date;
        }
        return date;
    };

    const handleCopyRoute = (routeToCopy: Route) => {
        const { id, ...withoutId } = routeToCopy;

        const copiedRoute: Omit<Route, "id"> = {
            ...withoutId,
            company: { ...withoutId.company },
            container: { ...withoutId.container },
            start_point: { ...withoutId.start_point },
            end_point: { ...withoutId.end_point },
            price: withoutId.price.map(p => ({ ...p })),
            effective_from: withoutId.effective_from ? formatDateForInput(withoutId.effective_from) : "",
            effective_to: withoutId.effective_to ? formatDateForInput(withoutId.effective_to) : "",
        };
        console.log(formatDateISO(formatDate(copiedRoute.effective_to)));


        setAddingRoutes(prev => [ ...prev, copiedRoute ]);
    };



    const formatDateForServer = (date: string) => {
        const [ year, month, day ] = date.split("-");
        return `${day}.${month}.${year}`;
    };

    const buildFilterFields = () => {
        const filter: Record<string, any> = {};

        activeFilters.forEach(f => {
            if (!f.value) return;
            switch (f.field) {
            case "Компания":
                if (typeof f.value === "string") {
                    const company = companies.find(c => c.name === f.value);
                    if (company) filter.company_id = company.id;
                }
                break;
            case "Контейнер":
                if (typeof f.value === "string") {
                    const container = containers.find(c => c.name === f.value);
                    if (container) filter.container_id = container.id;
                }
                break;
            case "Тип маршрута":
                if (typeof f.value === "string") filter.route_type = f.value;
                break;
            case "Точка отправления":
                if (typeof f.value === "object" && f.value.id) filter.start_point_id = f.value.id;
                break;
            case "Точка прибытия":
                if (typeof f.value === "object" && f.value.id) filter.end_point_id = f.value.id;
                break;
            case "Диапазон дат":
                if (typeof f.value === "string") {
                    const [ from, to ] = f.value.split("|");
                    if (from) filter.effective_from = formatDateForServer(from);
                    if (to) filter.effective_to = formatDateForServer(to);
                }
                break;
            default:
                break;
            }
        });

        return filter;
    };


    if (loading) return <div className="page_div">Загрузка...</div>;

    const availableFilterFields = optionsDropdown.filter.filter(
        f => !activeFilters.some(af => af.field === f),
    );

    const handleAddFilter = () => {
        if (availableFilterFields.length > 0) {
            setActiveFilters([ ...activeFilters, { field: availableFilterFields[0], value: "" } ]);
        }
    };
    const handleRoutesDelete = async (route: Route) => {
        console.log("234");
        if (!window.confirm("Удалить маршрут?")) return;
        console.log("1111111");

        try {
            console.log("222222");

            const payload = {
                rail: route.route_type === "rail" ? [ route.id ] : [],
                sea: route.route_type === "sea" ? [ route.id ] : [],
            };

            const response = await routesApi.deleteRoute(payload);

            if (response.status === "OK") {
                setRoutes(prev => prev.filter(r => r.id !== route.id));
            } else {
                alert("Неизвестная ошибка, удаление отменено.");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка сети при удалении маршрута");
            fetchRoutes();
        }
    };

    const handleRemoveFilter = (index: number) => {
        setActiveFilters(prev => prev.filter((_, i) => i !== index));
    };

    const handleChangeFilterField = (index: number, newField: string) => {
        setActiveFilters(prev => {
            const copy = [ ...prev ];
            copy[index].field = newField;
            copy[index].value = "";
            return copy;
        });

    };
    const handlePriceFocus = (index: number, type: string) => {
        setAddingRoutes(prev =>
            prev.map((route, i) =>
                i === index
                    ? {
                        ...route,
                        price: route.price.map(p =>
                            p.type === type && p.value === 0 ? { ...p, value: null } : p,
                        ),
                    }
                    : route,
            ),
        );
    };
    const handleSelectRoute = (routeId: number, checked: boolean) => {
        setSelectedRouteIds(prev => {
            if (checked) return [ ...prev, routeId ];
            return prev.filter(id => id !== routeId);
        });
    };

    const handleDeleteSelectedRoutes = async () => {
        try {
            const payload: { rail: number[]; sea: number[] } = { rail: [], sea: [] };

            selectedRouteIds.forEach(id => {
                const route = routes.find(r => r.id === id);
                if (route) payload[route.route_type].push(route.id);
            });

            const response = await routesApi.deleteRoute(payload);

            if (response.status === "OK") {
                setRoutes(prev => prev.filter(r => !selectedRouteIds.includes(r.id)));
                setSelectedRouteIds([]);
            } else {
                alert("Не удалось удалить все маршруты");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка сети при удалении маршрутов");
            fetchRoutes();
        }
    };

    const handlePriceBlur = (index: number, type: string) => {
        setAddingRoutes(prev =>
            prev.map((route, i) =>
                i === index
                    ? {
                        ...route,
                        price: route.price.map(p =>
                            p.type === type && (p.value === null || p.value === undefined) ? { ...p, value: 0 } : p,
                        ),
                    }
                    : route,
            ),
        );
    };

    const handleChangeFilterValue = (index: number, value: any) => {
        setActiveFilters(prev => {
            const copy = [ ...prev ];
            copy[index].value = value;
            return copy;
        });
    };
    const handleApplyFilters = () => { setPage(1); fetchRoutes(); };

    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление маршрутами</h1></div>

            <div className="control_panel_div">
                <button className="control_btn" onClick={ () => setIsModalOpen(true) }>Создать точку</button>
                <button onClick={ handleAddRoute } className="control_btn">Создать маршрут</button>
                <button
                    className="control_btn"
                    onClick={ handleDeleteSelectedRoutes }
                    disabled={ selectedRouteIds.length === 0 }
                >
                    Удалить выбранные
                </button>
                {availableFilterFields.length > 0 && (
                    <button className="control_btn" onClick={ handleAddFilter }>
                        + Добавить фильтр
                    </button>
                )}

                <button className="control_btn" onClick={ handleApplyFilters }>
                    <img src={ magnifier } alt="Поиск" className="actions_img" />
                </button>
            </div>

            <div className="filter_div">
                {activeFilters.map((filter, index) => {
                    const remainingFields = optionsDropdown.filter.filter(
                        f => f === filter.field || !activeFilters.some(af => af.field === f),
                    );

                    return (
                        <div key={ index } className="filter_div">
                            <div className="filter_item_div">
                                <Dropdown
                                    options={ remainingFields }
                                    selected={ filter.field }
                                    onSelect={ val => handleChangeFilterField(index, val) }
                                    className="dropdown-container"
                                />

                                {filter.field === "Тип маршрута" && (
                                    <Dropdown
                                        options={ [ "ЖД", "Морской" ] }
                                        selected={ typeof filter.value === "string" ? reverseRouteTypeMapping[filter.value as keyof typeof reverseRouteTypeMapping] || "" : "" }
                                        onSelect={ val => handleChangeFilterValue(index, routeTypeMapping[val as keyof typeof routeTypeMapping]) }
                                        className="dropdown-container"
                                        placeholder="Выберите тип"
                                    />
                                )}

                                {filter.field === "Компания" && (
                                    <Dropdown
                                        options={ companies.map(c => c.name) }
                                        selected={ typeof filter.value === "string" ? filter.value : "" }
                                        onSelect={ val => handleChangeFilterValue(index, val) }
                                        className="dropdown-container"
                                        placeholder="Выберите компанию"
                                    />
                                )}

                                {filter.field === "Контейнер" && (
                                    <Dropdown
                                        options={ containers.map(c => c.name) }
                                        selected={ typeof filter.value === "string" ? filter.value : "" }
                                        onSelect={ val => handleChangeFilterValue(index, val) }
                                        className="dropdown-container"
                                        placeholder="Выберите контейнер"
                                    />
                                )}

                                {filter.field === "Диапазон дат" && (
                                    <div>
                                        <input
                                            type="date"
                                            value={ typeof filter.value === "string" ? filter.value.split("|")[0] || "" : "" }
                                            onChange={ e => handleChangeFilterValue(index, `${e.target.value}|${typeof filter.value === "string" ? filter.value.split("|")[1] || "" : ""}`) }
                                            className="date-input"
                                            placeholder="Дата начала"
                                        />
                                        {"  -  "}
                                        <input
                                            type="date"
                                            value={ typeof filter.value === "string" ? filter.value.split("|")[1] || "" : "" }
                                            onChange={ e => handleChangeFilterValue(index, `${typeof filter.value === "string" ? filter.value.split("|")[0] || "" : ""}|${e.target.value}`) }
                                            className="date-input"
                                            placeholder="Дата окончания"
                                        />
                                    </div>
                                )}

                                {(filter.field === "Точка отправления" || filter.field === "Точка прибытия") && (
                                    <SearchableDropdown
                                        value={ typeof filter.value === "object" ? filter.value : null }
                                        onSelect={ point => handleChangeFilterValue(index, point) }
                                        className="dropdown-container"
                                        placeholder={ filter.field === "Точка отправления" ? "Выберите точку отправления" : "Выберите точку прибытия" }
                                    />
                                )}

                                <button className="actions_btn cancel" onClick={ () => handleRemoveFilter(index) }>
                                    <img src={ cross } className="actions_img" />
                                </button>
                            </div>
                        </div>
                    );
                })}

                <div className="control_filter_div">

                </div>
            </div>

            <div className="table_div">
                <table>
                    <thead>
                        <tr>
                            <th className="cell_cb"></th>
                            <th className="cell">Компания</th>
                            <th className="cell">Тип<br />маршрута</th>
                            <th className="cell">Контейнер</th>
                            <th className="cell">Диапазон<br />дат</th>
                            <th className="cell">Точка<br />отправки</th>
                            <th className="cell">Точка<br />прибытия</th>
                            <th className="cell">Цены</th>
                            <th className="cell">Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {routes.map(route => {
                            return (
                                <tr key={ route.id }>
                                    <td className="cell_cb">
                                        <input
                                            type="checkbox"
                                            checked={ selectedRouteIds.includes(route.id) }
                                            onChange={ e => handleSelectRoute(route.id, e.target.checked) }
                                        />
                                    </td>
                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <Dropdown
                                                options={ companies.map(c => c.name) }
                                                selected={ editedRoute?.company.name || "" }
                                                onSelect={ val => setEditedRoute(prev => prev ? { ...prev, company: companies.find(c => c.name === val)! } : prev) }
                                            />
                                        ) : (
                                            route.company.name
                                        )}
                                    </td>

                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <Dropdown
                                                options={ [ "ЖД", "Морской" ] }
                                                selected={ editedRoute?.route_type === "sea" ? "Морской" : "ЖД" }
                                                onSelect={ () => alert("Нельзя изменять тип маршрута") }
                                            />
                                        ) : (
                                            route.route_type === "sea" ? "Морской" : "ЖД"
                                        )}
                                    </td>

                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <Dropdown
                                                options={ containers.map(c => c.name) }
                                                selected={ editedRoute?.container.name || "" }
                                                onSelect={ val => setEditedRoute(prev => prev ? { ...prev, container: containers.find(c => c.name === val)! } : prev) }
                                            />
                                        ) : (
                                            route.container.name
                                        )}
                                    </td>

                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <>
                                                <input
                                                    type="date"
                                                    value={ formatDateISO(editedRoute?.effective_from || route.effective_from) }
                                                    className="date-input"
                                                    onChange={ e => setEditedRoute(prev => prev ? { ...prev, effective_from: e.target.value } : prev) }
                                                />
                                                <br />
                                                -
                                                <br />
                                                <input
                                                    type="date"
                                                    className="date-input"
                                                    value={ formatDateISO(editedRoute?.effective_to || route.effective_to)  }
                                                    onChange={ e => setEditedRoute(prev => prev ? { ...prev, effective_to: e.target.value } : prev) }
                                                />
                                            </>
                                        ) : (
                                            <>
                                                {formatDate(route.effective_from)}
                                                <br />
                                                -
                                                <br />
                                                {formatDate(route.effective_to)}
                                            </>
                                        )}
                                    </td>

                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <SearchableDropdown
                                                value={ editedRoute?.start_point || null }
                                                onSelect={ p => setEditedRoute(prev => prev ? { ...prev, start_point: p } : prev) }
                                            />
                                        ) : (
                                            `${route.start_point.RU_country}, ${route.start_point.RU_city}`
                                        )}
                                    </td>

                                    <td className="cell">
                                        {editingRouteId === route.id ? (
                                            <SearchableDropdown
                                                value={ editedRoute?.end_point || null }
                                                onSelect={ p => setEditedRoute(prev => prev ? { ...prev, end_point: p } : prev) }
                                            />
                                        ) : (
                                            `${route.end_point.RU_country}, ${route.end_point.RU_city}`
                                        )}
                                    </td>

                                    <td>
                                        {editingRouteId === route.id ? (
                                            <div className="price-edit-grid">
                                                {(route.route_type === "sea" ? [ "fifo","filo" ] : [ "price","guard","drop" ]).map(type => (
                                                    <div key={ type } className="price-row">
                                                        <span className="price-label">{type.toUpperCase()}:</span>
                                                        <input
                                                            type="number"
                                                            value={ editedRoute?.price.find(p => p.type === type)?.value ?? "" }
                                                            className="cell_input price-input"
                                                            onChange={ e => setEditedRoute(prev => prev ? {
                                                                ...prev,
                                                                price: prev.price.map(p => p.type === type ? { ...p, value: Number(e.target.value) } : p),
                                                            } : prev) }
                                                        />
                                                        <Dropdown
                                                            options={ [ "RUB","USD","EUR" ] }
                                                            selected={ editedRoute?.price.find(p => p.type === type)?.currency || "USD" }
                                                            className="dropdown-container"
                                                            onSelect={ currency => setEditedRoute(prev => prev ? {
                                                                ...prev,
                                                                price: prev.price.map(p => p.type === type ? { ...p, currency } : p),
                                                            } : prev) }
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <>
                                                {(route.route_type === "sea" ? [ "fifo","filo" ] : [ "price","guard","drop" ]).map(type => {
                                                    const p = route.price.find(p => p.type === type);
                                                    if (!p || p.value === null) return null;
                                                    return <div key={ type }>{type.toUpperCase()}: {p.value} {p.currency}</div>;
                                                })}
                                            </>
                                        )}
                                    </td>

                                    <td className="cell">
                                        <div className="action_div">
                                            {editingRouteId === route.id ? (
                                                <>
                                                    <button className="actions_btn save" onClick={ () => handleSaveEditedRoute(route.id) }>
                                                        <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                                    </button>
                                                    <button className="actions_btn cancel" onClick={ handleCancelEdit }>
                                                        <img src={ cross } alt="отменить" className="actions_img" />
                                                    </button>
                                                </>
                                            ) : (
                                                <>
                                                    <button className="actions_btn edit" onClick={ () => handleEditRoute(route) }>
                                                        <img src={ changeMarker } alt="изменить" className="actions_img" />
                                                    </button>
                                                    <button className="actions_btn cancel" onClick={ () => handleRoutesDelete(route) }>
                                                        <img src={ trashcan } alt="удалить" className="actions_img" />
                                                    </button>
                                                    <button className="actions_btn copy" onClick={ () => handleCopyRoute(route) }>
                                                        <img src={ copying } alt="копировать" className="actions_img" />
                                                    </button>
                                                </>
                                            )}
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
                                            options={ companies.map(c => c.name) }
                                            selected={ newRoute.company.name }
                                            onSelect={ val => handleChangeNewRouteField(index, "company", companies.find(c => c.name === val)) }
                                        />
                                    </td>
                                    <td>
                                        <Dropdown
                                            options={ optionsDropdown.routeType }
                                            selected={ isSea ? "Морской" : "ЖД" }
                                            onSelect={ val => handleChangeNewRouteField(index, "route_type", val === "ЖД" ? "rail" : "sea") }
                                        />
                                    </td>
                                    <td>
                                        <Dropdown
                                            options={ containers.map(c => c.name) }
                                            selected={ newRoute.container.name }
                                            onSelect={ val => handleChangeNewRouteField(index, "container", containers.find(c => c.name === val)) }
                                        />
                                    </td>
                                    <td>
                                        <input
                                            type="date"
                                            value={ formatDateISO(formatDate(newRoute.effective_from)) }
                                            className="date-input"
                                            onChange={ e => handleChangeNewRouteField(index, "effective_from", e.target.value) } />
                                        -<br />
                                        <input type="date"
                                            className="date-input"
                                            value={ formatDateISO(formatDate(newRoute.effective_to)) }
                                            onChange={ e => handleChangeNewRouteField(index, "effective_to", e.target.value) } />
                                    </td>
                                    <td>
                                        <SearchableDropdown value={ newRoute.start_point } onSelect={ p => handleChangeNewRouteField(index, "start_point", p) } />
                                    </td>
                                    <td>
                                        <SearchableDropdown value={ newRoute.end_point } onSelect={ p => handleChangeNewRouteField(index, "end_point", p) } />
                                    </td>
                                    <td>
                                        {isSea ? (
                                            <div className="price-edit-grid">
                                                {[ "fifo", "filo" ].map(type => (
                                                    <div key={ type } className="price-row">
                                                        <span className="price-label">{type.toUpperCase()}:</span>
                                                        <input
                                                            type="number"
                                                            value={ newRoute.price.find(p => p.type === type)?.value ?? "" }
                                                            className="cell_input price-input"
                                                            onFocus={ () => handlePriceFocus(index, type) }
                                                            onBlur={ () => handlePriceBlur(index, type) }
                                                            onChange={ e => handleChangePriceValue(index, type, Number(e.target.value)) }
                                                        />
                                                        <Dropdown
                                                            options={ optionsDropdown.currency }
                                                            selected={ newRoute.price.find(p => p.type === type)?.currency || "USD" }
                                                            className="dropdown-container"
                                                            onSelect={ currency => handleChangePriceCurrency(index, type, currency) }
                                                            placeholder="Валюта" />
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="price-edit-grid">
                                                {[ "price", "guard", "drop" ].map(type => (
                                                    <div key={ type } className="price-row">
                                                        <span className="price-label">{type.charAt(0).toUpperCase() + type.slice(1)}:</span>
                                                        <input
                                                            type="number"
                                                            value={ newRoute.price.find(p => p.type === type)?.value ?? "" }
                                                            className="input"
                                                            onFocus={ () => handlePriceFocus(index, type) }
                                                            onBlur={ () => handlePriceBlur(index, type) }
                                                            onChange={ e => handleChangePriceValue(index, type, Number(e.target.value)) }
                                                        />
                                                        <Dropdown options={ optionsDropdown.currency } selected={ newRoute.price.find(p => p.type === type)?.currency || (type === "price" ? "RUB" : "USD") } className="dropdown-container" onSelect={ currency => handleChangePriceCurrency(index, type, currency) } placeholder="Валюта" />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </td>
                                    <td>
                                        <div className="action_div">
                                            <button className="actions_btn save" onClick={ () => handleSaveNewRoute(index) }>
                                                <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                            </button>
                                            <button className="actions_btn cancel" onClick={ () => handleCancelNewRoute(index) }>
                                                <img src={ cross } alt="отменить" className="actions_img" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>

                <div className="pagination_div">
                    <Pagination
                        currentPage={ page }
                        totalPages={ totalPage }
                        onPageChange={ setPage } />
                </div>

                <CreatePoint
                    isOpen={ isModalOpen }
                    onClose={ () => setIsModalOpen(false) } />
            </div>
        </div>
    );
}
