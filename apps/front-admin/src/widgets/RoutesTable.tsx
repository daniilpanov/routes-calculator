// @ts-ignore

import "../resources/scss/routes_mngmnt_style.scss";
import back_img from "../resources/images/back.png";
import forward_img from "../resources/images/forward.png";


export function RoutesTable(){
    const routes = [
        {
            id: "A",
            type: "HUB",
            routeType: "Морской",
            dateRange: "01 сент. 2025 - 30 сент. 2025",
            departure: "Врангель, РФ",
            arrival: "Вьетнам, Хайфон",
            container: "20DC",
            prices: "FIFO - 1500$ FILO - 1900$",
        },
        {
            id: "A",
            type: "HUB",
            routeType: "Морской",
            dateRange: "01 сент. 2025 - 30 сент. 2025",
            departure: "СПб, РФ",
            arrival: "Вьетнам, Хайфон",
            container: "20DC",
            prices: "FIFO - 1400$ FILO - 1800$",
        },
    ];
    return (
        <div className="page_div">
            <div className="heading_div">
                <h1>Управление маршрутами</h1>
            </div>
            <div className="control_panel_div">
                <button className="back_forward_btn">
                    <img src={ back_img } alt="back" className="back_img" />
                </button>
                <button className="back_forward_btn">
                    <img src={ forward_img } alt="forward" className="forward_img" />
                </button>
                <button className="control_btn">Создать точку</button>
                <button className="control_btn">Создать маршрут</button>
                <button className="control_btn">Объединить точки</button>
            </div>
            <div className="table_div">
                <table>
                    <thead>
                        <tr>
                            <th>V</th>
                            <th>Компания</th>
                            <th>Тип маршрута</th>
                            <th>Диапазон дат действия маршрута</th>
                            <th>Точка отправки</th>
                            <th>Точка прибытия</th>
                            <th>Контейнер</th>
                            <th>Цены</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {routes.map((route, index) => (
                            <tr key={ index }>
                                <td></td>
                                <td>{route.type}</td>
                                <td>{route.routeType}</td>
                                <td>{route.dateRange}</td>
                                <td>{route.departure}</td>
                                <td>{route.arrival}</td>
                                <td>{route.container}</td>
                                <td>{route.prices}</td>
                                <td></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

        </div>
    );
}
