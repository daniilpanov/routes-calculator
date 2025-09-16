import React, { useEffect, useState } from "react";
import { pointsService } from "../api/Points";
import "resources/scss/index.scss";
import { Point } from "../interfaces/Points";
import changeMarker from "../resources/images/changeMarker.png";
import trashcan from "../resources/images/trashcan.png";
import copying from "../resources/images/copying.png";
import { Pagination } from "./Pagination";
import accessMarks from "../resources/images/accessMarks.png";
import cross from "../resources/images/cross.png";


export function PointsTable() {
    const [ PAGE_SIZE ] = useState<number>(25);
    const [ totalPage, setTotalPages ] = useState<number>(0);
    const [ page, setPage ] = useState(1);
    const [ points, setPoints ] = useState<Point[]>([]);
    const [ addingPoints, setAddingPoints ] = useState<Omit<Point, "id">[]>([]);
    const [ loading, setLoading ] = useState(false);

    useEffect(() => {
        fenchPoints();
    }, [ page ]);
    const [ emptyPoint, setEmptyPoint ] = useState<Omit<Point, "id">>(
        {
            RU_city: "",
            RU_country: "",
            country: "",
            city: "",
        });
    const handleAddPoint = () => {
        setAddingPoints(prev => [ ...prev, { ...emptyPoint } ]);
    };
    const fenchPoints = async () => {
        setLoading(true);
        try {
            const response = await pointsService.getPoints({
                page: page,
                limit: PAGE_SIZE,
            });
            if (response.status === "OK") {
                setPoints(response.points);
                setTotalPages(Math.ceil(response.count / PAGE_SIZE));

            }
            console.log(response);
        } catch (error) {
            console.log(error);
        } finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (<p>
            Загрузка...
        </p>);
    }

    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление точками</h1></div>
            <div className="control_panel_div">
                <button
                    onClick={ handleAddPoint }
                    className="control_btn"
                >Создать точку</button>
            </div>
            <div className="table_div">
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>RU страна</th>
                            <th>RU город</th>
                            <th>EN страна</th>
                            <th>En город</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            points.map(point => {
                                return (
                                    <tr>
                                        <td></td>
                                        <td>{point.RU_country}</td>
                                        <td>{point.RU_city}</td>
                                        <td>{point.country}</td>
                                        <td>{point.city}</td>
                                        <td>
                                            <div className="action_div">
                                                <button className="actions_btn edit">
                                                    <img src={ changeMarker } alt="изменить" className="actions_img" />
                                                </button>
                                                <button className="actions_btn cancel">
                                                    <img src={ trashcan } alt="удалить" className="actions_img" />
                                                </button>
                                                <button className="actions_btn copy">
                                                    <img src={ copying } alt="копировать" className="actions_img" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        }
                        {
                            addingPoints.map(point => {
                                return (
                                    <tr>
                                        <td></td>
                                        <td>
                                            <input
                                                className="input"
                                                type="text"
                                            />
                                        </td>
                                        <td>
                                            <input
                                                className="input"
                                                type="text"
                                            />
                                        </td>
                                        <td>
                                            <input
                                                className="input"
                                                type="text"
                                            />
                                        </td>
                                        <td>
                                            <input
                                                className="input"
                                                type="text"
                                            />
                                        </td>
                                        <td>
                                            <div className="action_div">
                                                <button className="actions_btn save" >
                                                    <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                                </button>
                                                <button className="actions_btn cancel">
                                                    <img src={ cross } alt="отменить" className="actions_img" />
                                                </button>
                                            </div>
                                        </td>
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

