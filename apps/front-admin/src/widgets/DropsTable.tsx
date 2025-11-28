import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { ROUTES } from "@/constants";
import { dropsApi } from "@/api/DropsApi";
import { routesApi } from "@/api/RoutesApi";
import { Drop } from "@/interfaces/Model/Drop";
import { parseDateFromTimestampToOutput } from "@/utils/Date";
import { Pagination } from "@/widgets/Pagination";

const PAGE_SIZE = 25;

export function DropsTable() {
    const [ loading, setLoading ] = useState<boolean>(false);
    const [ drops, setDrops ] = useState<Drop[]>([]);
    const [ error, setError ] = useState<string>();
    const [ totalPage, setTotalPages ] = useState<number>(0);
    const [ page, setPage ] = useState(1);

    useEffect(() => {
        fetchDrops();
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
    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление drop'ами</h1></div>
            <div className="control_panel_div">
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="control_btn">Таблица маршрутов</NavLink>
                <button className="control_btn">Создать маршрут</button>
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
                                            <br />{drop.sea_end_point?.RU_country}, {drop.sea_end_point?.RU_country}
                                        </>) :
                                        "-"}
                                    </td>
                                    <td className="cell">{(drop.rail_start_point) ? (
                                        <>
                                            {drop.rail_start_point?.RU_country}, {drop.rail_start_point?.RU_city}
                                            <br />-
                                            <br />{drop.rail_end_point?.RU_country}, {drop.rail_end_point?.RU_country}
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
                                </tr>
                            );
                        })
                        }

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
