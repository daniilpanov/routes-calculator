import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { ROUTES } from "@/constants";
import { dropsApi } from "@/api/DropsApi";
import { Drop } from "@/interfaces/Model/Drop";
import arrow_right from "@/resources/svg/arrow_right.svg";

import {
    parseDateFromTimestampToInput,
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
    id?: number;
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
    const [ editingDrop, setEditingDrop ] = useState<addingDrops[]>([]);
    const [ deletingDrops, setDeletingDrops ] = useState<{ ids: number[] }>({ ids: [] });

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
    const handleSaveNewDrop = async (index: number) => {
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
    function handleCancelNewDrop(index: number) {
        setAddingDrops(prevDrops => prevDrops.filter((_, i) => i !== index));
    }
    function handleCopyDrop(drop: Drop) {
        const copyDrop: addingDrops = {
            company_name: drop.company.name,
            container_name: drop.container.name,
            sea_start_point_name: drop.sea_start_point,
            sea_end_point_name: drop.sea_end_point,
            rail_start_point_name: drop.rail_start_point,
            rail_end_point_name: drop.rail_end_point,
            start_date: parseDateFromTimestampToInput(drop.start_date),
            end_date: parseDateFromTimestampToInput(drop.end_date),
            price: drop.price,
            currency: "USD",
        };
        console.log(copyDrop);
        setAddingDrops([ copyDrop, ...addingDrops ]);
    }

    async function handleDeleteDrops(id: number) {
        const deleteDrop = {
            ids: [ id ],
        };
        try {
            const response = await dropsApi.deleteDrops(deleteDrop);
            if (response.status === "OK") {
                setDrops(prevDrops => prevDrops.filter(drop => drop.id !== id));
                setDeletingDrops(prev => ({
                    ids: prev.ids.filter(dropId => dropId !== id),
                }));
                console.log(response);
                setDeletingDrops({ ids: [] });
                alert("Дроп успешно удален");
            } else {
                alert("Ошибка при удалении дропа");
            }
        } catch (err) { console.error(err); }
    }
    async function handleDeleteSelectedDrops() {
        if (deletingDrops.ids.length === 0) {
            return alert("Нет дропов для удаления");
        }

        const idsToDelete = [ ...deletingDrops.ids ];

        try {
            const response = await dropsApi.deleteDrops({ ids: idsToDelete });
            if (response.status === "OK") {
                setDrops(prevDrops => prevDrops.filter(drop => !idsToDelete.includes(drop.id)));
                setDeletingDrops({ ids: [] });
                console.log(response);
                alert("Дропы успешно удалены");
            } else {
                alert("Ошибка при удалении дропов");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка при удалении дропов");
        }
    }
    const handleCheckboxChange = (id: number) => {
        setDeletingDrops(prev => {
            if (prev.ids.includes(id)) {
                return { ids: prev.ids.filter(dropId => dropId !== id) };
            } else {
                return { ids: [ ...prev.ids, id ] };
            }
        });
    };
    const handleSaveEdit = async (dropId: number) => {
        const editedDrop = editingDrop.find(ed => ed.id === dropId);
        if (!editedDrop) return;

        const company = companies.find(c => c.name === editedDrop.company_name);
        const container = containers.find(c => c.name === editedDrop.container_name);

        if (!company || !container) {
            alert("Ошибка в данных");
            return;
        }

        const editData: any = {
            drop_id: dropId,
            company_id: company.id,
            container_id: container.id,
            sea_start_point_id: editedDrop.sea_start_point_name?.id || null,
            sea_end_point_id: editedDrop.sea_end_point_name?.id || null,
            rail_start_point_id: editedDrop.rail_start_point_name?.id || null,
            rail_end_point_id: editedDrop.rail_end_point_name?.id || null,
            start_date: parseInputToTimestamp(editedDrop.start_date || ""),
            end_date: parseInputToTimestamp(editedDrop.end_date || ""),
            price: editedDrop.price || 0,
            currency: "USD",
        };

        try {
            const response = await dropsApi.editDrops(editData);
            if (response.status === "OK") {
                setDrops(prev =>
                    prev.map(drop =>
                        drop.id === dropId
                            ? response.changed_drop
                            : drop,
                    ),
                );
                setEditingDrop(prev => prev.filter(ed => ed.id !== dropId));
                alert("Сохранено");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка сохранения");
        }
    };

    const handleCancelEdit = (dropId: number) => {
        setEditingDrop(prev => prev.filter(ed => ed.id !== dropId));
    };
    const handleEditDrop = (drop: Drop) => {
        const isAlreadyEditing = editingDrop.some(ed => ed.id === drop.id);

        if (isAlreadyEditing) {
            setEditingDrop(prev => prev.filter(ed => ed.id !== drop.id));
        } else {
            const editDrop: addingDrops = {
                id: drop.id,
                company_name: drop.company.name,
                container_name: drop.container.name,
                sea_start_point_name: drop.sea_start_point,
                sea_end_point_name: drop.sea_end_point,
                rail_start_point_name: drop.rail_start_point,
                rail_end_point_name: drop.rail_end_point,
                start_date: parseDateFromTimestampToInput(drop.start_date),
                end_date: parseDateFromTimestampToInput(drop.end_date),
                price: drop.price,
                currency: "USD",
            };
            setEditingDrop(prev => [ ...prev, editDrop ]);
        }
    };
    const handleChangeEditDrop = (dropId: number, field: keyof addingDrops, value: any) => {
        setEditingDrop(prev =>
            prev.map(drop =>
                drop.id === dropId
                    ? { ...drop, [field]: value }
                    : drop,
            ),
        );
    };
    return (
        <div className="page_div">
            <div className="heading_div"><h1>Управление drop off</h1></div>
            <div className="control_panel_div">
                <div className="d-f fd-r g-10 fg-1">
                    <button className="control_btn" onClick={ addDrop }>Создать drop</button>
                    <button
                        className="control_btn"
                        onClick={ handleDeleteSelectedDrops }
                        disabled={ deletingDrops.ids.length === 0 }
                    >
                        Удалить выбранные
                    </button>
                </div>
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="control_btn jc-c">
                    Таблица маршрутов
                    <img src={ arrow_right } alt="arrow_right" className="icon" />
                </NavLink>
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
                        {drops.map((drop, index) => {
                            return (
                                <tr key={ drop.id }>
                                    <td className="cell_cb">
                                        <input
                                            type="checkbox"
                                            checked={ deletingDrops.ids.includes(drop.id) }
                                            onChange={ () => handleCheckboxChange(drop.id) }
                                        />
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <Dropdown
                                                    options={ companies.map(c => c.name) }
                                                    selected={ editingDrop.find(ed => ed.id === drop.id)?.company_name || "" }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "company_name", val) }
                                                />
                                            </>
                                        ) : (
                                            <>
                                                {drop.company.name}
                                            </>
                                        )}
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <Dropdown
                                                    options={ containers.map(c => c.name) }
                                                    selected={ editingDrop.find(ed => ed.id === drop.id)?.container_name || "" }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "container_name", val) }
                                                />
                                            </>
                                        ) : (
                                            <>
                                                {drop.container.name}
                                            </>
                                        )}
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <SearchableDropdown
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.sea_start_point_name || null }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "sea_start_point_name", val) }
                                                />
                                                <br />-
                                                <br /><SearchableDropdown
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.sea_end_point_name || null }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "sea_end_point_name", val) }
                                                />
                                            </>
                                        ) : (drop.sea_start_point) ? (
                                            <>
                                                {drop.sea_start_point?.RU_country}, {drop.sea_start_point?.RU_city}
                                                <br />-
                                                <br />{drop.sea_end_point?.RU_country}, {drop.sea_end_point?.RU_city}
                                            </>) :
                                            "-"}
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <SearchableDropdown
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.rail_start_point_name || null }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "rail_start_point_name", val) }
                                                />
                                                <br />-
                                                <br /><SearchableDropdown
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.rail_end_point_name || null }
                                                    onSelect={ (val) => handleChangeEditDrop(drop.id, "rail_end_point_name", val) }
                                                />
                                            </>
                                        ) : (drop.rail_start_point) ? (
                                            <>
                                                {drop.rail_start_point?.RU_country}, {drop.rail_start_point?.RU_city}
                                                <br />-
                                                <br />{drop.rail_end_point?.RU_country}, {drop.rail_end_point?.RU_city}
                                            </>) :
                                            "-"}
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <input
                                                    type="date"
                                                    className="date-input"
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.start_date || "" }
                                                    onChange={ (e) => handleChangeEditDrop(drop.id, "start_date", e.target.value) }
                                                />

                                                <br />-
                                                <br /><input
                                                    type="date"
                                                    className="date-input"
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.end_date || "" }
                                                    onChange={ (e) => handleChangeEditDrop(drop.id, "end_date", e.target.value) }
                                                />
                                            </>
                                        ) : (
                                            <>
                                                <>
                                                    {parseDateFromTimestampToOutput(drop.start_date)}
                                                    <br />-
                                                    <br />{parseDateFromTimestampToOutput(drop.end_date)}
                                                </>
                                            </>
                                        )}
                                    </td>
                                    <td className="cell">
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <>
                                                <input
                                                    type="number"
                                                    className="input"
                                                    value={ editingDrop.find(ed => ed.id === drop.id)?.price || 0 }
                                                    onChange={ (e) => handleChangeEditDrop(drop.id, "price", Number(e.target.value)) }
                                                />
                                            </>
                                        ) : (
                                            <>
                                                {drop.price} {drop.currency}
                                            </>
                                        )}
                                    </td>
                                    <td>
                                        {editingDrop.some(editDrop => editDrop.id === drop.id) ? (
                                            <div className="action_div">
                                                <button className="actions_btn save" onClick={ () => handleSaveEdit(drop.id) }>
                                                    <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                                </button>
                                                <button className="actions_btn cancel" onClick={ () => handleCancelEdit(drop.id) }>
                                                    <img src={ cross } alt="отменить" className="actions_img" />
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="action_div">
                                                <button className="actions_btn edit">
                                                    <img src={ changeMarker } alt="изменить" className="actions_img" onClick={ () => handleEditDrop(drop) } />
                                                </button>
                                                <button className="actions_btn cancel">
                                                    <img src={ trashcan } alt="удалить" className="actions_img" onClick={ () => handleDeleteDrops(drop.id) } />
                                                </button>
                                                <button className="actions_btn copy">
                                                    <img src={ copying } alt="копировать" className="actions_img" onClick={ () => handleCopyDrop(drop) } />
                                                </button>
                                            </div>
                                        )}
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
                                            value={ newDrop.price || 0 }
                                            onChange={ e => handleChangeNewDrop(index, "price", e.target.value) }

                                        />
                                    </td>
                                    <td className="cell">
                                        <div className="action_div">
                                            <button className="actions_btn save" onClick={ () => handleSaveNewDrop(index) }>
                                                <img src={ accessMarks } alt="сохранить" className="actions_img" />
                                            </button>
                                            <button className="actions_btn cancel" onClick={ () => handleCancelNewDrop(index) }>
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
