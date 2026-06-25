import { createSetting, deleteSetting, listSettings, updateSetting } from "@/api/Settings";
import type { ISetting } from "@/interfaces/Setting";
import { ChangeEvent, FormEvent, useEffect, useState } from "react";

const VALUE_TYPES = [ "BOOL", "INT", "FLOAT", "STRING", "JSON" ] as const;
const emptyForm = { group: "", name: "", description: "", value_type: "STRING", value: "" };

export default function Settings() {
    const [ settings, setSettings ] = useState<ISetting[]>([]);
    const [ form, setForm ] = useState(emptyForm);
    const [ editingId, setEditingId ] = useState<number | null>(null);
    const [ loading, setLoading ] = useState(false);
    const [ message, setMessage ] = useState<string | null>(null);
    const [ error, setError ] = useState<string | null>(null);
    const [ groupFilter, setGroupFilter ] = useState("");
    const [ searchFilter, setSearchFilter ] = useState("");

    const loadSettings = async () => {
        setLoading(true);
        setError(null);
        try {
            setSettings(await listSettings(groupFilter, searchFilter));
        } catch (e) {
            setError((e as Error).message || "Не удалось загрузить настройки");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadSettings();
    }, []);

    const resetForm = () => {
        setForm(emptyForm);
        setEditingId(null);
    };

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        setMessage(null);
        setError(null);

        const payload = {
            group: form.group.trim(),
            name: form.name.trim(),
            description: form.description.trim() || null,
            value_type: form.value_type,
            value: form.value.trim() || null,
        };

        if (!payload.group || !payload.name) {
            setError("Group и Name обязательны");
            return;
        }

        try {
            if (editingId)
                await updateSetting(editingId, payload);
            else
                await createSetting(payload);

            setMessage(editingId ? "Настройка обновлена" : "Настройка создана");
            resetForm();
            await loadSettings();
        } catch (e) {
            setError((e as Error).message || "Ошибка сохранения");
        }
    };

    const handleEdit = (setting: ISetting) => {
        setEditingId(setting.id);
        setForm({
            group: setting.group,
            name: setting.name,
            description: setting.description || "",
            value_type: setting.value_type,
            value: setting.value || "",
        });
    };

    const handleDelete = async (setting: ISetting) => {
        if (!window.confirm(`Удалить настройку ${setting.group}.${setting.name}?`))
            return;

        setMessage(null);
        setError(null);
        try {
            await deleteSetting(setting.id);
            if (editingId === setting.id)
                resetForm();
            setMessage("Настройка удалена");
            await loadSettings();
        } catch (e) {
            setError((e as Error).message || "Ошибка удаления");
        }
    };

    const handleSearch = (event: FormEvent) => {
        event.preventDefault();
        void loadSettings();
    };

    const editingSetting = editingId ? settings.find(s => s.id === editingId) : null;
    const isLockedEditing = editingSetting?.locked ?? false;

    const renderValueInput = () => {
        const common = { value: form.value, onChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setForm({ ...form, value: e.target.value }) };

        switch (form.value_type.toLowerCase()) {
        case "bool":
            return (
                <select { ...common }>
                    <option value="">—</option>
                    <option value="true">Да</option>
                    <option value="false">Нет</option>
                </select>
            );
        case "int":
            return <input type="number" step="1" { ...common } />;
        case "float":
            return <input type="number" step="any" { ...common } />;
        case "json":
            return <textarea rows={ 4 } { ...common } />;
        default:
            return <input { ...common } />;
        }
    };

    return (
        <div className="data-import-page">
            <h1>Настройки</h1>

            {loading && <p>Загрузка…</p>}
            {message && <div className="message success">{message}</div>}
            {error && <div className="message error">{error}</div>}

            <form onSubmit={ handleSearch } className="button-group" style={ { display: "flex", gap: "0.5rem", marginBottom: "1rem" } }>
                <input placeholder="Фильтр по group" value={ groupFilter } onChange={ e => setGroupFilter(e.target.value) } />
                <input placeholder="Поиск по name" value={ searchFilter } onChange={ e => setSearchFilter(e.target.value) } />
                <button type="submit">Поиск</button>
                <button type="button" onClick={ () => { setGroupFilter(""); setSearchFilter(""); void loadSettings(); } }>Сбросить</button>
            </form>

            <form onSubmit={ handleSubmit } className="button-group">
                <label>
                    Group
                    <input value={ form.group } onChange={ e => setForm({ ...form, group: e.target.value }) } placeholder="general" disabled={ isLockedEditing } />
                </label>
                <label>
                    Name
                    <input value={ form.name } onChange={ e => setForm({ ...form, name: e.target.value }) } placeholder="setting_name" disabled={ isLockedEditing } />
                </label>
                <label>
                    Description
                    <input value={ form.description } onChange={ e => setForm({ ...form, description: e.target.value }) } placeholder="Описание настройки" />
                </label>
                <label>
                    Type
                    <select value={ form.value_type } onChange={ e => setForm({ ...form, value_type: e.target.value }) } disabled={ isLockedEditing }>
                        { VALUE_TYPES.map(t => <option key={ t } value={ t }>{ t }</option>) }
                    </select>
                </label>
                <label>
                    Value
                    { renderValueInput() }
                </label>
                <button type="submit">{ editingId ? "Сохранить" : "Добавить" }</button>
                {editingId && <button type="button" onClick={ resetForm }>Отмена</button>}
            </form>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Group</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Value</th>
                        <th>Locked</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {settings.map(setting => (
                        <tr key={ setting.id }>
                            <td>{ setting.id }</td>
                            <td>{ setting.group }</td>
                            <td>{ setting.name }</td>
                            <td>{ setting.description }</td>
                            <td>{ setting.value_type }</td>
                            <td style={ { maxWidth: "200px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" } }>{ setting.value }</td>
                            <td>{ setting.locked ? "🔒" : "" }</td>
                            <td>
                                <button type="button" onClick={ () => handleEdit(setting) }>Изменить</button>
                                {!setting.locked && <button type="button" onClick={ () => void handleDelete(setting) }>Удалить</button>}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
