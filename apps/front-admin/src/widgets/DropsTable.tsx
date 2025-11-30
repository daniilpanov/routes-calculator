import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { ROUTES } from "@/constants";
import { dropsApi } from "@/api/DropsApi";
import { Drop } from "@/interfaces/Model/Drop";
import {
    parseDateFromTimestampToOutput,
    parseInputToTimestamp,
} from "@/utils/Date";
import { Pagination } from "@/widgets/Pagination";
import changeMarker from "@/resources/images/changeMarker.png";
import trashcan from "@/resources/images/trashcan.png";
import copying from "@/resources/images/copying.png";
import { companiesService } from "@/api/Companies";
import { containersApi } from "@/api/ContainersApi";
import { Company } from "@/interfaces/Companies";
import { Container } from "@/interfaces/Containers";
import { Dropdown } from "@/components/Dropdown";
import { SearchableDropdown } from "@/components/SearchableDropdown";
import { Point } from "@/interfaces/Points";
import accessMarks from "@/resources/images/accessMarks.png";
import cross from "@/resources/images/cross.png";

const PAGE_SIZE = 25;

interface addingDrops {
    company_name: string | null,
    container_name: string | null,
    sea_start_point_name: Point | null,
    sea_end_point_name: Point | null,
    rail_start_point_name: Point | null,
    rail_end_point_name: Point | null,
    start_date: string | null,
    end_date: string | null,
    price: number | null,
    currency: "USD"
}

export function DropsTable() {
    const [ loading, setLoading ] = useState<boolean>(false);
    const [ drops, setDrops ] = useState<Drop[]>([]);
    const [ companies, setCompanies ] = useState<Company[]>([]);
    const [ containers, setContainers ] = useState<Container[]>([]);
    const [ addingDrops, setAddingDrops ] = useState<addingDrops[]>([]);
    const [ error, setError ] = useState<string>();
    const [ totalPage, setTotalPages ] = useState<number>(0);
    const [ page, setPage ] = useState(1);

    const emptyDrop: addingDrops = {
        company_name: null,
        container_name: null,
        sea_start_point_name: null,
        sea_end_point_name: null,
        rail_start_point_name: null,
        rail_end_point_name: null,
        start_date: null,
        end_date: null,
        price: null,
        currency: "USD",
    };

    useEffect(() => {
        fetchDrops();
        fetchCompanies();
        fetchContainers();
    }, [ page ]);

    const fetchDrops = async () => {
        try {
            setLoading(true);
            const response = await dropsApi.getDrops(page, PAGE_SIZE);
            if (response.status === "OK") {
                setDrops(response.drops);
                setTotalPages(Math.ceil(response.count / PAGE_SIZE));
            } else setError("Не удалось загрузить дропы");
        } catch (err) {
            setError("Ошибка при загрузке дропов");
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
    const addDrop = async () => {
        setAddingDrops([ emptyDrop, ...addingDrops ]);
    };
    const handleChangeNewDrop = (index: number, field: string, value: string | Point) => {
        setAddingDrops(prevDrops =>
            prevDrops.map((drop, i) =>
                i === index ? { ...drop, [field]: value } : drop,
            ),
        );
    };
    const handleSaveNewRoute = async (index: number) => {
        const newDrop = addingDrops[index];
        console.log(newDrop);
        if (!newDrop) return;
        if (
            !newDrop.company_name ||
            !newDrop.container_name ||
            !newDrop.price ||
            !newDrop.start_date ||
            !newDrop.end_date
        )
            return alert("Все поля обязательны для заполнения");

        const noSeaPoints = !newDrop.sea_start_point_name && !newDrop.sea_end_point_name;
        const noRailPoints = !newDrop.rail_start_point_name && !newDrop.rail_end_point_name;

        if (noSeaPoints && noRailPoints) {
            return alert("Должны быть указаны либо морские точки, либо ж/д точки");
        }
        const company = companies.find(c => c.name === newDrop.company_name);
        const container = containers.find(c => c.name === newDrop.container_name);
        if (!company || !container) {
            return alert("Неизвестная ошибка");
        }

        const addingDrop: any = {
            company_id: company.id,
            container_id: container.id,
            start_date: parseInputToTimestamp(newDrop.start_date),
            end_date: parseInputToTimestamp(newDrop.end_date),
            price: newDrop.price,
            currency: "USD",
        };

        if (newDrop.rail_start_point_name && newDrop.rail_end_point_name) {
            addingDrop.rail_start_point_id = newDrop.rail_start_point_name.id;
            addingDrop.rail_end_point_id = newDrop.rail_end_point_name.id;
        }

        if (newDrop.sea_start_point_name && newDrop.sea_end_point_name) {
            addingDrop.sea_start_point_id = newDrop.sea_start_point_name.id;
            addingDrop.sea_end_point_id = newDrop.sea_end_point_name.id;
        }
        console.log(addingDrop);

        try {
            const response = await dropsApi.addDrops(addingDrop);
            if (response.status === "OK") {
                setDrops(drops => [ response.new_drop, ...drops ]);
                setAddingDrops(prevDrops => prevDrops.filter((_, i) => i !== index));
                console.log(response);
                alert("Дроп успешно добавлен");
            } else {
                alert("Ошибка при создании дропа");
            }
        } catch (err) { console.error(err); }
    };
    function handleCancelNewRoute(index: number) {
        setAddingDrops(prevDrops => prevDrops.filter((_, i) => i !== index));
    }

    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление drop'ами</h1></div>
            <div className="control_panel_div">
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="control_btn">Таблица маршрутов</NavLink>
                <button className="control_btn" onClick={ addDrop }>Создать drop</button>
                <button
                    className="control_btn"
                    //onClick={ handleDeleteSelectedRoutes }
                    //disabled={ selectedRouteIds.length === 0 }
                >
                    Удалить выбранные
                </button>
            </div>
            <div className="table_div">
                <table>
                    <thead>
                        <tr>
                            <th className="cell_cb"></th>
                            <th className="cell">Компания</th>
                            <th className="cell">Контейнер</th>
                            <th className="cell">Точка отправки по морю<br />-<br />Точка прибытия по морю</th>
                            <th className="cell">Точка отправки по ЖД<br />-<br />Точка прибытия по ЖД</th>
                            <th className="cell">Диапазон дат</th>
                            <th className="cell">Цена</th>
                            <th className="cell">Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {drops.map(drop => {
                            return (
                                <tr key={ drop.id }>
                                    <td className="cell_cb"></td>
                                    <td className="cell">{drop.company.name}</td>
                                    <td className="cell">{drop.container.name}</td>
                                    <td className="cell">{(drop.sea_start_point) ? (
                                        <>
                                            {drop.sea_start_point?.RU_country}, {drop.sea_start_point?.RU_city}
                                            <br />-
                                            <br />{drop.sea_end_point?.RU_country}, {drop.sea_end_point?.RU_city}
                                        </>) :
                                        "-"}
                                    </td>
                                    <td className="cell">{(drop.rail_start_point) ? (
                                        <>
                                            {drop.rail_start_point?.RU_country}, {drop.rail_start_point?.RU_city}
                                            <br />-
                                            <br />{drop.rail_end_point?.RU_country}, {drop.rail_end_point?.RU_city}
                                        </>) :
                                        "-"}
                                    </td>
                                    <td className="cell">{
                                        <>
                                            {parseDateFromTimestampToOutput(drop.start_date)}
                                            <br />-
                                            <br />{parseDateFromTimestampToOutput(drop.end_date)}
                                        </>
                                    }
                                    </td>
                                    <td className="cell">{drop.price} {drop.currency}</td>
                                    <td>
                                        <>
                                            <button className="actions_btn edit">
                                                <img src={ changeMarker } alt="изменить" className="actions_img" />
                                            </button>
                                            <button className="actions_btn cancel">
                                                <img src={ trashcan } alt="удалить" className="actions_img" />
                                            </button>
                                            <button className="actions_btn copy">
                                                <img src={ copying } alt="копировать" className="actions_img" />
                                            </button>
                                        </>
                                    </td>
                                </tr>
                            );
                        })
                        }
                        {addingDrops.map((newDrop, index) => {
                            return (
                                <tr key={ index }>
                                    <td className="cell"></td>
                                    <td>
                                        <Dropdown
                                            options={ companies.map(c => c.name) }
                                            selected={ newDrop.company_name || "" }
                                            onSelect={ val => (handleChangeNewDrop(index, "company_name", val)) }
                                        />
                                    </td>
                                    <td className="cell">
                                        <Dropdown
                                            options={ containers.map(c => c.name) }
                                            selected={ newDrop.container_name || "" }
                                            onSelect={ val => (handleChangeNewDrop(index, "container_name", val)) }
                                        />
                                    </td>
                                    <td className="cell">
                                        <SearchableDropdown
                                            value={ newDrop.sea_start_point_name }
                                            onSelect={ val => handleChangeNewDrop(index, "sea_start_point_name", val) }
                                        />
                                        <br />-
                                        <br /><SearchableDropdown
                                            value={ newDrop.sea_end_point_name }
                                            onSelect={ val => handleChangeNewDrop(index, "sea_end_point_name", val) }
                                        />
                                    </td>
                                    <td className="cell">
                                        <SearchableDropdown
                                            value={ newDrop.rail_start_point_name }
                                            onSelect={ val => handleChangeNewDrop(index, "rail_start_point_name", val) }
                                        />
                                        <br />-
                                        <br /><SearchableDropdown
                                            value={ newDrop.rail_end_point_name }
                                            onSelect={ val => handleChangeNewDrop(index, "rail_end_point_name", val) }
                                        />
                                    </td>
                                    <td className="cell">
                                        <input
                                            type="date"
                                            className="date-input"
                                            value={ newDrop.start_date || 0 }
                                            onChange={ e => handleChangeNewDrop(index, "start_date", e.target.value) }
                                        />
                                        <br />-
                                        <br /><input
                                            type="date"
                                            className="date-input"
                                            value={ newDrop.end_date || 0 }
                                            onChange={ e => handleChangeNewDrop(index, "end_date", e.target.value) }
                                        />
                                    </td>
                                    <td className="cell">
                                        <input
                                            type="number"
                                            className="input"
                                            onChange={ e => handleChangeNewDrop(index, "price", e.target.value) }

                                        />
                                    </td>
                                    <td className="cell">
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
            </div>
        </div>
    );
}
