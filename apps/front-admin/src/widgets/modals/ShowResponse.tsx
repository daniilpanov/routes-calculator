import React from "react";
import "@/resources/scss/index.scss";
import { Modal } from "@/components/Modal";

interface ShowResponseProps {
    isOpen: boolean;
    onClose: () => void;
    answer: any;
}

export function ShowResponse({ isOpen, onClose, answer }: ShowResponseProps) {
    return (
        <Modal
            isOpen={ isOpen }
            onClose={ onClose }
            className="modal-wrapper"
        >
            <h4>Предварительный результат</h4>
            <p>{`Загружено маршрутов: ${answer?.count_new_routes ?? 0}`}</p>
            <p>{`Загружено новых точек: ${answer?.count_new_points ?? 0}`}</p>
            <p>{`Файл: ${answer?.file ?? ""}`}</p>
            <div className="control_div">
                <button
                    className="control_btn cancel"
                >Отмена</button>
                <button
                    className="control_btn edit"
                >Редактировать</button>
                <button
                    className="control_btn accept"
                >Подтвердить</button>
            </div>
        </Modal>
    );
}
