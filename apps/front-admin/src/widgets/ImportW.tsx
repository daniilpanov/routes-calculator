import React, { useState } from "react";
import { CreateSample } from "./modals/CreateSample";



export function ImportW() {
    const [ isModalOpen, setIsModalOpen ] = useState(false);

    return (
        <>
            <div className="heading_div">
                <h1>Управление маршрутами</h1>
            </div>
            <div>
                <p>Выберите шаблон данных данных</p>
                <button
                    onClick={ () => setIsModalOpen(true) }
                >+</button>
            </div>
            <CreateSample
                isOpen={ isModalOpen }
                onClose={ () => setIsModalOpen(false) }
            />
        </>

    );
}

