import "../resources/scss/routes_mngmnt_style.scss";
import back_img from "../resources/images/back.png";
import forward_img from "../resources/images/forward.png";

export default function Routes_management() {
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

        </div>
    );
}
