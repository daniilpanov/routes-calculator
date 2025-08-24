import React, { useState } from "react";
import { Modal } from "../../components/Modal";
import "../../resources/scss/page/dataImport/index.scss";

interface CreateSampleProps {
    isOpen: boolean;
    onClose: () => void;
}


export function CreateSample({ isOpen, onClose }: CreateSampleProps) {

    return (
        <Modal
            isOpen={ isOpen }
            onClose={ onClose }
            className="point-modal-wrapper"
        >
            <p>Название компании</p>
            <p>Название столбца с наименованием</p>
            <p>Диапазон эффектиных дат</p>
            <p></p>
            <p></p>
        </Modal>
    );
}
