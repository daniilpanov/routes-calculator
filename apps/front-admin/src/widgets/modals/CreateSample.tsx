import React, { useState } from "react";
import { Modal } from "../../components/Modal";
import "../../resources/scss/page/dataImport/index.scss";
import { Dropdown } from "../../components/Dropdown";

interface CreateSampleProps {
    isOpen: boolean;
    onClose: () => void;
}


export function CreateSample({ isOpen, onClose }: CreateSampleProps) {
    const [ temp, setTemp ] = useState("1");
    const [ optionsDropdown ] = useState<{ [key: string]: string[] }>({
        nameCompany: [ "Название компании", "Название столбца наименованием" ],
    });

    return (
        <Modal
            isOpen={ isOpen }
            onClose={ onClose }
            className="point-modal-wrapper"
        >
            <Dropdown options={ optionsDropdown.nameCompany } selected={ temp } onSelect={ setTemp } className="company-dropdown-wrapper" />
            <p>Название компании</p>
            <p>Название столбца с наименованием</p>
            <p>Диапазон эффектиных дат</p>
            <p></p>
            <p></p>
        </Modal>
    );
}
